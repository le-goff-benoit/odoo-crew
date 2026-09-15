from odoo.tests import tagged

from .common import PreparationCommon


@tagged('post_install', '-at_install')
class TestPreparation(PreparationCommon):
    def test_cron_mixed_cohort_and_replay(self):
        automatic = self.make_preparation(delivered_qty=3, prepared_qty=999)
        protected = self.make_preparation(manual=True, prepared_qty=0)
        protected |= self.make_preparation(manual=True, prepared_qty=2, delivered_qty=3)
        protected |= self.make_preparation(state='done', prepared_qty=88, delivered_qty=4)
        protected |= self.make_preparation(state='done', manual=True, prepared_qty=1)
        before = self.snapshot(protected)
        self.Preparation._cron_prepare()
        self.assertEqual(automatic.prepared_qty, 7)
        self.assertEqual(self.snapshot(protected), before)
        after = self.snapshot(automatic | protected)
        self.Preparation._cron_prepare()
        self.assertEqual(self.snapshot(automatic | protected), after)

    def test_cron_nonpositive_and_fractional_remaining(self):
        equal = self.make_preparation(delivered_qty=10, prepared_qty=9)
        excess = self.make_preparation(delivered_qty=12, prepared_qty=9)
        small = self.make_preparation(ordered_qty=0.004, delivered_qty=0.001)
        self.Preparation._cron_prepare()
        self.assertEqual(equal.prepared_qty, 0)
        self.assertEqual(excess.prepared_qty, 0)
        self.assertAlmostEqual(small.prepared_qty, 0.003)

    def test_manual_zero_then_cron(self):
        record = self.make_preparation(prepared_qty=5)
        record.action_set_manual(0)
        self.assertTrue(record.manual)
        self.assertEqual(record.prepared_qty, 0)
        self.Preparation._cron_prepare()
        self.assertEqual(record.prepared_qty, 0)

    def test_manual_nonzero_then_cron(self):
        records = self.make_preparation() | self.make_preparation(delivered_qty=4)
        records.action_set_manual(2)
        self.assertEqual(records.mapped('manual'), [True, True])
        self.Preparation._cron_prepare()
        self.assertEqual(records.mapped('prepared_qty'), [2, 2])

    def test_duplicate_then_cron(self):
        for state in ('draft', 'done'):
            for manual in (False, True):
                with self.subTest(state=state, manual=manual):
                    source = self.make_preparation(
                        state=state, manual=manual, delivered_qty=3, prepared_qty=2,
                    )
                    before = self.snapshot(source)
                    duplicate = source.copy()
                    self.assertRecordValues(duplicate, [{
                        'ordered_qty': 10, 'delivered_qty': 0, 'prepared_qty': 0,
                        'manual': False, 'state': 'draft',
                    }])
                    self.assertEqual(self.snapshot(source), before)
                    self.Preparation._cron_prepare()
                    self.assertEqual(duplicate.prepared_qty, 10)
                    if state == 'done' or manual:
                        self.assertEqual(self.snapshot(source), before)

    def test_remainder_then_cron(self):
        for manual, prepared in ((True, 0), (True, 2), (False, 7)):
            with self.subTest(manual=manual, prepared=prepared):
                source = self.make_preparation(
                    manual=manual, prepared_qty=prepared, delivered_qty=3,
                )
                count = self.Preparation.search_count([])
                remainder = source.action_remainder()
                self.assertEqual(len(remainder), 1)
                self.assertEqual(self.Preparation.search_count([]), count + 1)
                self.assertRecordValues(remainder, [{
                    'ordered_qty': 7, 'delivered_qty': 0, 'prepared_qty': 0,
                    'manual': False, 'state': 'draft', 'parent_id': source.id,
                }])
                self.assertRecordValues(source, [{
                    'ordered_qty': 10, 'delivered_qty': 3, 'prepared_qty': prepared,
                    'manual': manual, 'state': 'done',
                }])
                before = self.snapshot(source)
                self.Preparation._cron_prepare()
                self.assertEqual(remainder.prepared_qty, 7)
                self.assertEqual(self.snapshot(source), before)
                after = self.snapshot(remainder)
                self.Preparation._cron_prepare()
                self.assertEqual(self.snapshot(remainder), after)

    def test_remainder_nonpositive(self):
        for delivered in (10, 12):
            with self.subTest(delivered=delivered):
                source = self.make_preparation(delivered_qty=delivered, prepared_qty=2)
                before = self.snapshot(source)
                count = self.Preparation.search_count([])
                remainder = source.action_remainder()
                self.assertEqual(remainder, self.Preparation.browse())
                self.assertEqual(self.Preparation.search_count([]), count)
                self.assertEqual(self.snapshot(source), before)

    def test_remainder_fractional(self):
        source = self.make_preparation(ordered_qty=0.004, delivered_qty=0.001)
        remainder = source.action_remainder()
        self.assertAlmostEqual(remainder.ordered_qty, 0.003)
        self.Preparation._cron_prepare()
        self.assertAlmostEqual(remainder.prepared_qty, 0.003)

    def test_remainder_requires_singleton(self):
        records = self.make_preparation() | self.make_preparation()
        before = self.snapshot(records)
        count = self.Preparation.search_count([])
        with self.assertRaisesRegex(ValueError, 'Expected singleton'):
            records.action_remainder()
        self.assertEqual(self.snapshot(records), before)
        self.assertEqual(self.Preparation.search_count([]), count)
