from odoo.tests import tagged

from .common import LabPreparationCommon


@tagged('post_install', '-at_install')
class TestPeriodicPreparation(LabPreparationCommon):
    """Decision N-17: the cron only recomputes automatic drafts."""

    def test_cron_computes_remaining_quantity(self):
        """C1: an automatic draft gets what is ordered minus what is delivered."""
        preparation = self.new_preparation('AUTO', ordered_qty=10, delivered_qty=3)

        self.Preparation._cron_prepare()

        self.assertEqual(preparation.prepared_qty, 7)

    def test_cron_never_goes_below_zero(self):
        """C2: delivering more than ordered leaves nothing to prepare."""
        preparation = self.new_preparation('OVER_DELIVERED', ordered_qty=10, delivered_qty=12)

        self.Preparation._cron_prepare()

        self.assertEqual(preparation.prepared_qty, 0)

    def test_cron_keeps_manual_zero(self):
        """C3: a manual zero is an explicit decision, not an empty value."""
        preparation = self.new_preparation('MANUAL_ZERO', ordered_qty=10, delivered_qty=0)

        preparation.action_set_manual(0)

        self.assertEqual(preparation.prepared_qty, 0)
        self.assertTrue(preparation.manual, "action_set_manual(0) must still flag the record as manual")

        self.Preparation._cron_prepare()

        self.assertEqual(preparation.prepared_qty, 0, "the cron must not overwrite a manual zero")
        self.assertTrue(preparation.manual)

    def test_cron_keeps_manual_partial(self):
        """C4: any manual entry is kept as is."""
        preparation = self.new_preparation('MANUAL_PARTIAL', ordered_qty=10, delivered_qty=3)
        preparation.action_set_manual(2)

        self.Preparation._cron_prepare()

        self.assertEqual(preparation.prepared_qty, 2)
        self.assertTrue(preparation.manual)

    def test_cron_freezes_done_records(self):
        """C5: a done record is frozen, even when it is not manual."""
        preparation = self.new_preparation(
            'DONE_AUTO', ordered_qty=10, delivered_qty=4, prepared_qty=88, state='done',
        )

        self.Preparation._cron_prepare()

        self.assertEqual(preparation.prepared_qty, 88)
        self.assertEqual(preparation.state, 'done')

    def test_cron_is_idempotent(self):
        """C6: replaying the cron changes nothing on the whole cohort."""
        cohort = (
            self.new_preparation('IDEM_AUTO', ordered_qty=10, delivered_qty=3)
            | self.new_preparation('IDEM_DONE', ordered_qty=10, delivered_qty=4, prepared_qty=88, state='done')
        )
        manual = self.new_preparation('IDEM_MANUAL', ordered_qty=10, delivered_qty=3)
        manual.action_set_manual(0)
        cohort |= manual

        self.Preparation._cron_prepare()
        before = [self.snapshot(record) for record in cohort]
        self.Preparation._cron_prepare()

        self.assertEqual([self.snapshot(record) for record in cohort], before)


@tagged('post_install', '-at_install')
class TestPreparationDuplication(LabPreparationCommon):
    """Decision N-17: a duplicate is a brand new request."""

    def test_copy_resets_execution_and_keeps_ordered_quantity(self):
        """C7: only the ordered quantity survives a duplication."""
        source = self.new_preparation(
            'SOURCE', ordered_qty=10, delivered_qty=4, prepared_qty=88, manual=True, state='done',
        )
        before = self.snapshot(source)

        duplicate = source.copy()

        self.assertEqual(duplicate.ordered_qty, 10)
        self.assertEqual(duplicate.delivered_qty, 0)
        self.assertEqual(duplicate.prepared_qty, 0)
        self.assertFalse(duplicate.manual)
        self.assertEqual(duplicate.state, 'draft')
        self.assertEqual(self.snapshot(source), before, "duplicating must not touch the source")

    def test_copy_then_cron_computes_the_new_request(self):
        """A duplicate is an automatic draft again: the cron owns it."""
        source = self.new_preparation('SOURCE_CRON', ordered_qty=10, delivered_qty=4)
        source.action_set_manual(1)

        duplicate = source.copy()
        self.Preparation._cron_prepare()

        self.assertEqual(duplicate.prepared_qty, 10)
        self.assertEqual(source.prepared_qty, 1)


@tagged('post_install', '-at_install')
class TestPreparationRemainder(LabPreparationCommon):
    """Decision N-17: the remainder is a new draft linked to its source."""

    def test_remainder_creates_draft_and_closes_source(self):
        """C8: the remainder carries what is left, the source is closed as is."""
        source = self.new_preparation('SPLIT', ordered_qty=10, delivered_qty=3, prepared_qty=5)

        remainder = source.action_remainder()

        self.assertEqual(len(remainder), 1)
        self.assertEqual(remainder.ordered_qty, 7)
        self.assertEqual(remainder.delivered_qty, 0)
        self.assertEqual(remainder.prepared_qty, 0)
        self.assertFalse(remainder.manual)
        self.assertEqual(remainder.state, 'draft')
        self.assertEqual(remainder.parent_id, source)
        self.assertEqual(source.state, 'done')
        self.assertEqual(source.prepared_qty, 5, "closing the source must not overwrite its prepared quantity")

    def test_remainder_without_leftover_does_nothing(self):
        """C9: no positive leftover, no record and no write at all."""
        for delivered in (10, 12):
            with self.subTest(delivered=delivered):
                source = self.new_preparation(
                    'NO_SPLIT_%s' % delivered, ordered_qty=10, delivered_qty=delivered, prepared_qty=5,
                )
                before = self.snapshot(source)
                count = self.Preparation.search_count([])

                remainder = source.action_remainder()

                self.assertFalse(remainder)
                self.assertEqual(remainder._name, 'lab.preparation')
                self.assertEqual(self.Preparation.search_count([]), count, "no record may be created")
                self.assertEqual(self.snapshot(source), before, "the source must stay untouched")

    def test_remainder_requires_a_single_record(self):
        """C10: the method is a singleton."""
        pair = (
            self.new_preparation('PAIR_A', ordered_qty=10, delivered_qty=3)
            | self.new_preparation('PAIR_B', ordered_qty=10, delivered_qty=3)
        )

        with self.assertRaises(ValueError):
            pair.action_remainder()

    def test_remainder_of_remainder(self):
        """Splitting twice keeps each remainder attached to its own source."""
        source = self.new_preparation('CHAIN', ordered_qty=10, delivered_qty=3)

        first = source.action_remainder()
        first.delivered_qty = 2
        second = first.action_remainder()

        self.assertEqual(first.ordered_qty, 7)
        self.assertEqual(second.ordered_qty, 5)
        self.assertEqual(second.parent_id, first)
        self.assertEqual(first.state, 'done')


@tagged('post_install', '-at_install')
class TestPreparationScheduledAction(LabPreparationCommon):
    """Hypothesis H3: 'periodic' has to be wired to a scheduled action."""

    def test_scheduled_action_is_declared(self):
        """C11: the module ships the cron that calls the preparation."""
        cron = self.env.ref('lab_preparation.ir_cron_lab_preparation')

        self.assertEqual(cron.model_id.model, 'lab.preparation')
        self.assertEqual(cron.state, 'code')
        self.assertIn('_cron_prepare', cron.code)
        self.assertTrue(cron.active)
