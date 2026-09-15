from odoo.tests.common import tagged

from .common import LabPreparationCommon


@tagged('post_install', '-at_install')
class TestPreparationCron(LabPreparationCommon):
    """Décision N-17 — le traitement périodique ne touche que les drafts automatiques."""

    def test_cron_computes_remaining_quantity(self):
        """C1 — un draft automatique reçoit ordered - delivered."""
        preparation = self.new_preparation(ordered_qty=10, delivered_qty=3)

        self.Preparation._cron_prepare()

        self.assertEqual(preparation.prepared_qty, 7)
        self.assertFalse(preparation.manual)
        self.assertEqual(preparation.state, 'draft')

    def test_cron_never_goes_negative(self):
        """C2 — livré au-delà du commandé donne zéro, jamais un négatif."""
        preparation = self.new_preparation(ordered_qty=4, delivered_qty=9)

        self.Preparation._cron_prepare()

        self.assertEqual(preparation.prepared_qty, 0)

    def test_cron_keeps_manual_zero(self):
        """C3 — une saisie manuelle à zéro est une valeur, pas une absence."""
        preparation = self.new_preparation(ordered_qty=10)
        preparation.action_set_manual(0)

        self.assertTrue(preparation.manual)
        self.assertEqual(preparation.prepared_qty, 0)

        self.Preparation._cron_prepare()

        self.assertEqual(preparation.prepared_qty, 0)
        self.assertTrue(preparation.manual)

    def test_cron_keeps_manual_partial(self):
        """C4 — une saisie manuelle partielle est conservée à l'identique."""
        preparation = self.new_preparation(ordered_qty=10, delivered_qty=3)
        preparation.action_set_manual(2)

        self.Preparation._cron_prepare()

        self.assertEqual(preparation.prepared_qty, 2)

    def test_cron_freezes_done(self):
        """C5 — un enregistrement terminé est figé."""
        preparation = self.new_preparation(
            ordered_qty=10, delivered_qty=4, prepared_qty=88, state='done',
        )

        self.Preparation._cron_prepare()

        self.assertEqual(preparation.prepared_qty, 88)
        self.assertEqual(preparation.state, 'done')

    def test_cron_is_idempotent(self):
        """C6 — rejouer le cron ne change plus rien."""
        automatic = self.new_preparation(ordered_qty=10, delivered_qty=3)
        manual = self.new_preparation(ordered_qty=10)
        manual.action_set_manual(0)
        done = self.new_preparation(ordered_qty=10, prepared_qty=88, state='done')

        self.Preparation._cron_prepare()
        snapshot = [(record.prepared_qty, record.manual, record.state)
                    for record in (automatic | manual | done)]

        self.Preparation._cron_prepare()

        self.assertEqual(
            [(record.prepared_qty, record.manual, record.state)
             for record in (automatic | manual | done)],
            snapshot,
        )


@tagged('post_install', '-at_install')
class TestPreparationCopy(LabPreparationCommon):
    """Décision N-17 — une duplication est une nouvelle demande."""

    def test_copy_resets_history(self):
        """C7 — seul ordered_qty survit à la duplication."""
        source = self.new_preparation(ordered_qty=10, delivered_qty=3)
        source.action_set_manual(2)

        duplicate = source.copy()

        self.assertEqual(duplicate.ordered_qty, 10)
        self.assertEqual(duplicate.delivered_qty, 0)
        self.assertEqual(duplicate.prepared_qty, 0)
        self.assertFalse(duplicate.manual)
        self.assertEqual(duplicate.state, 'draft')

    def test_copy_of_done_is_a_fresh_draft(self):
        """C8 — la copie d'un terminé repart en brouillon automatique."""
        source = self.new_preparation(ordered_qty=10, delivered_qty=4, state='done')
        source.action_set_manual(6)

        duplicate = source.copy()

        self.assertEqual(duplicate.state, 'draft')
        self.assertFalse(duplicate.manual)

        self.Preparation._cron_prepare()

        self.assertEqual(duplicate.prepared_qty, 10)
        self.assertEqual(source.prepared_qty, 6)


@tagged('post_install', '-at_install')
class TestPreparationRemainder(LabPreparationCommon):
    """Décision N-17 — le reliquat porte le reste, la source est close."""

    def test_remainder_creates_the_rest(self):
        """C9 — un reste positif donne un draft du reste et clôt la source."""
        source = self.new_preparation(ordered_qty=10, delivered_qty=4)
        source.action_set_manual(6)

        remainder = source.action_remainder()

        self.assertEqual(len(remainder), 1)
        self.assertEqual(remainder.ordered_qty, 6)
        self.assertEqual(remainder.delivered_qty, 0)
        self.assertEqual(remainder.prepared_qty, 0)
        self.assertFalse(remainder.manual)
        self.assertEqual(remainder.state, 'draft')
        self.assertEqual(remainder.parent_id, source)
        self.assertEqual(source.state, 'done')
        self.assertEqual(source.prepared_qty, 6)

    def test_remainder_without_rest_creates_nothing(self):
        """C10 — sans reste positif, recordset vide et aucune ligne créée."""
        source = self.new_preparation(ordered_qty=10, delivered_qty=10)
        source.action_set_manual(10)
        before = self.Preparation.search_count([])

        remainder = source.action_remainder()

        self.assertFalse(remainder)
        self.assertEqual(self.Preparation.search_count([]), before)
        self.assertEqual(source.state, 'done')
        self.assertEqual(source.prepared_qty, 10)

    def test_remainder_requires_a_singleton(self):
        """C11 — l'action est un singleton."""
        records = self.new_preparation(ordered_qty=10) | self.new_preparation(ordered_qty=5)

        with self.assertRaises(ValueError):
            records.action_remainder()
