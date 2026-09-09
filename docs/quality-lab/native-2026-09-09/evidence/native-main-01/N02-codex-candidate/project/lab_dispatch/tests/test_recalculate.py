from unittest.mock import patch

from odoo import Command
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged('post_install', '-at_install')
class TestRecalculate(TransactionCase):

    @classmethod
    def setUpClass(cls):
        """Prepare historical totals and an ordinary internal user."""
        super().setUpClass()
        cls.user = new_test_user(cls.env, login='dispatch_operator', groups='base.group_user')
        cls.draft, cls.done = cls.env['lab.dispatch'].create([
            {
                'name': name,
                'state': state,
                'snapshot_total': total,
                'line_ids': [
                    Command.create({'quantity': 2, 'price': 10}),
                    Command.create({'quantity': 3, 'price': 30, 'cancelled': True}),
                ],
            }
            for name, state, total in [('Draft', 'draft', 999), ('Validated', 'done', 777)]
        ])

    def test_draft_excludes_cancelled(self):
        """Cancelled lines must not contribute to a stored draft total."""
        self.assertTrue(self.draft.action_recalculate())
        self.draft.flush_recordset()
        self.draft.invalidate_recordset()
        self.assertEqual(self.draft.snapshot_total, 20)

    def test_validated_snapshot_unchanged(self):
        """Validated snapshots must retain their historical amount."""
        before = self.done.read(['snapshot_total', 'state', 'write_date'])
        self.assertTrue(self.done.action_recalculate())
        self.done.flush_recordset()
        self.done.invalidate_recordset()
        self.assertEqual(self.done.read(['snapshot_total', 'state', 'write_date']), before)

    def test_validated_never_written(self):
        """Even a snapshot equal to the live sum must not be rewritten."""
        self.done.snapshot_total = 110
        with patch.object(type(self.done), 'write', autospec=True) as write:
            self.assertTrue(self.done.action_recalculate())
        write.assert_not_called()

    def test_mixed_selection_internal_user(self):
        """An ordinary internal user can process a mixed selection safely."""
        records = (self.done | self.draft).with_user(self.user)
        self.assertFalse(records.env.su)
        self.assertTrue(records.action_recalculate())
        records.flush_recordset()
        records.invalidate_recordset()
        self.assertEqual(records.mapped('snapshot_total'), [777, 20])
        self.assertEqual(records.mapped('state'), ['done', 'draft'])

    def test_empty_and_all_cancelled(self):
        """A draft with no active line has a zero total."""
        empty, cancelled = self.env['lab.dispatch'].create([
            {'name': 'Empty', 'snapshot_total': 123},
            {
                'name': 'All cancelled',
                'snapshot_total': 456,
                'line_ids': [Command.create({'quantity': 4, 'price': 5, 'cancelled': True})],
            },
        ])
        self.assertTrue((empty | cancelled).action_recalculate())
        self.assertEqual((empty | cancelled).mapped('snapshot_total'), [0, 0])
        self.assertTrue(self.env['lab.dispatch'].action_recalculate())

    def test_active_amounts(self):
        """All active amounts, including fractional and negative ones, count."""
        self.draft.line_ids = [
            Command.create({'quantity': 0.5, 'price': 7}),
            Command.create({'quantity': -2, 'price': 3}),
            Command.create({'quantity': 0, 'price': 500}),
        ]
        self.draft.action_recalculate()
        self.assertEqual(self.draft.snapshot_total, 17.5)

    def test_recalculate_idempotent(self):
        """A second pass must not write an already correct draft."""
        self.draft.action_recalculate()
        self.draft.flush_recordset()
        before = self.draft.read(['snapshot_total', 'state', 'write_date'])
        with patch.object(type(self.draft), 'write', autospec=True) as write:
            self.assertTrue(self.draft.action_recalculate())
        write.assert_not_called()
        self.draft.invalidate_recordset()
        self.assertEqual(self.draft.read(['snapshot_total', 'state', 'write_date']), before)
