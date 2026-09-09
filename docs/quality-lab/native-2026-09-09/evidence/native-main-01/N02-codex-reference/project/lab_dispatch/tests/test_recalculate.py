from unittest.mock import patch

from odoo import Command
from odoo.tests import tagged

from .common import LabDispatchCommon


@tagged('post_install', '-at_install')
class TestRecalculate(LabDispatchCommon):

    def test_draft_excludes_cancelled_lines(self):
        """Only active line amounts contribute to the draft total."""
        self.assertTrue(self.draft.action_recalculate())
        self.assertEqual(self.draft.snapshot_total, 20)

    def test_done_is_frozen(self):
        """Validated snapshots survive a recalculation request."""
        self.assertTrue(self.done.action_recalculate())
        self.assertEqual(self.done.snapshot_total, 777)

    def test_done_never_written(self):
        """Even an already matching validated total must not be written."""
        self.done.snapshot_total = 20
        self.env.flush_all()
        before = self.done.write_date
        with patch.object(type(self.done), 'write', side_effect=AssertionError('Validated write')):
            self.assertTrue(self.done.action_recalculate())
        self.done.invalidate_recordset()
        self.assertEqual(self.done.snapshot_total, 20)
        self.assertEqual(self.done.write_date, before)

    def test_mixed_selection(self):
        """Mixed selections recalculate drafts without touching validated records."""
        self.assertTrue((self.done | self.draft).action_recalculate())
        self.assertEqual(self.draft.snapshot_total, 20)
        self.assertEqual(self.done.snapshot_total, 777)
        self.assertEqual((self.draft | self.done).mapped('state'), ['draft', 'done'])

    def test_empty_and_all_cancelled(self):
        """Drafts without active lines reset to zero; an empty selection is safe."""
        records = self.env['lab.dispatch'].create([
            {'name': 'Empty', 'snapshot_total': 50},
            {
                'name': 'Cancelled', 'snapshot_total': 50,
                'line_ids': [Command.create({'quantity': 5, 'price': 8, 'cancelled': True})],
            },
        ])
        self.assertTrue(records.action_recalculate())
        self.assertEqual(records.mapped('snapshot_total'), [0, 0])
        self.assertTrue(self.env['lab.dispatch'].action_recalculate())

    def test_recalculate_is_idempotent(self):
        """A second request preserves values and avoids redundant writes."""
        records = self.draft | self.done
        records.action_recalculate()
        self.env.flush_all()
        before = records.read(['snapshot_total', 'state', 'write_date'])
        with patch.object(type(records), 'write', side_effect=AssertionError('Redundant write')):
            records.action_recalculate()
        records.invalidate_recordset()
        self.assertEqual(records.read(['snapshot_total', 'state', 'write_date']), before)
