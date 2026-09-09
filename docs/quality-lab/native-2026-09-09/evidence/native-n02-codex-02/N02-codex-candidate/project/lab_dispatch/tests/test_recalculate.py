from unittest.mock import patch

from odoo.tests import tagged

from .common import LabDispatchCommon


@tagged('post_install', '-at_install')
class TestDispatchRecalculate(LabDispatchCommon):

    def test_draft_excludes_cancelled(self):
        """Only active lines contribute to a draft snapshot."""
        self.assertTrue(self.draft.action_recalculate())
        self.assertStoredTotal(self.draft, 20)

    def test_done_keeps_snapshot(self):
        """A validated snapshot cannot be reconstructed from current lines."""
        self.assertTrue(self.done.action_recalculate())
        self.assertStoredTotal(self.done, 777)

    def test_done_does_not_read_lines_or_write(self):
        """Validated records must be skipped before any recalculation."""
        with (
            patch.object(type(self.done), 'write', side_effect=AssertionError('Validated write')),
            patch.object(type(self.done._fields['line_ids']), '__get__', side_effect=AssertionError('Validated line read')),
        ):
            self.assertTrue(self.done.action_recalculate())

    def test_mixed_selection(self):
        """A mixed selection processes drafts without rejecting validated records."""
        self.assertTrue((self.done | self.draft).action_recalculate())
        self.assertStoredTotal(self.draft, 20)
        self.assertStoredTotal(self.done, 777)

    def test_empty_and_cancelled_lines(self):
        """Empty sums reset stale drafts to zero."""
        self.draft.line_ids.write({'cancelled': True})
        self.draft.action_recalculate()
        self.assertStoredTotal(self.draft, 0)
        self.draft.line_ids.unlink()
        self.draft.snapshot_total = 42
        self.draft.action_recalculate()
        self.assertStoredTotal(self.draft, 0)
        self.assertTrue(self.env['lab.dispatch'].action_recalculate())

    def test_recalculate_is_idempotent(self):
        """Repeating the action on an accurate snapshot performs no write."""
        self.draft.snapshot_total = 20
        self.draft.flush_recordset()
        with patch.object(type(self.draft), 'write', side_effect=AssertionError('Redundant write')):
            self.assertTrue(self.draft.action_recalculate())
        self.assertStoredTotal(self.draft, 20)
