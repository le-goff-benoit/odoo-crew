from odoo.tests import tagged

from .common import LabRegisterCommon


@tagged('post_install', '-at_install', 'repair_b42')
class TestRegisterRepair(LabRegisterCommon):
    """Decision B-42: action_repair only renumbers the drafts of self in the active company."""

    def test_renumbers_active_company_drafts_by_date_then_id(self):
        """C1 and C5: 100, 200, 300 in date_document then id order."""
        drafts = self.draft_same_2 | self.draft_same_1 | self.draft_early
        self._as(self.user_multi, drafts, self.company_a).action_repair()

        self.assertEqual(self.draft_early.sequence, 100)
        self.assertEqual(self.draft_same_1.sequence, 200)
        self.assertEqual(self.draft_same_2.sequence, 300)

    def test_snapshot_total_ignores_cancelled_lines(self):
        """C2: only lines with cancelled=False are summed."""
        drafts = self.draft_early | self.draft_same_1 | self.draft_same_2
        self._as(self.user_multi, drafts, self.company_a).action_repair()

        self.assertEqual(self.draft_early.snapshot_total, 20.0)
        self.assertEqual(self.draft_same_1.snapshot_total, 15.0)
        self.assertEqual(self.draft_same_2.snapshot_total, 20.0)

    def test_issued_reference_is_preserved(self):
        """C3: an issued record inside the selection keeps state, sequence, total and reference."""
        before = self._snapshot(self.issued_a)
        selection = self.draft_early | self.issued_a | self.draft_same_1
        self._as(self.user_multi, selection, self.company_a).action_repair()

        self.assertEqual(self._snapshot(self.issued_a), before)

    def test_other_company_is_left_untouched(self):
        """C4: a mixed selection is accepted, the other company is ignored."""
        before = self._snapshot(self.draft_b)
        selection = self.draft_early | self.draft_b | self.draft_same_1
        self._as(self.user_multi, selection, self.company_a,
                 activated_companies=[self.company_a, self.company_b]).action_repair()

        self.assertEqual(self._snapshot(self.draft_b), before)
        self.assertEqual(self.draft_early.sequence, 100)
        self.assertEqual(self.draft_same_1.sequence, 200)

    def test_records_outside_self_are_untouched(self):
        """The perimeter is self, not the whole table."""
        before = self._snapshot(self.draft_outside)
        selection = self.draft_early | self.draft_same_1
        self._as(self.user_multi, selection, self.company_a).action_repair()

        self.assertEqual(self._snapshot(self.draft_outside), before)

    def test_repair_is_idempotent(self):
        """C6: replaying the repair changes nothing."""
        selection = self.draft_early | self.draft_same_1 | self.draft_same_2 | self.issued_a | self.draft_b
        as_user = self._as(self.user_multi, selection, self.company_a,
                           activated_companies=[self.company_a, self.company_b])
        as_user.action_repair()
        after_first = self._snapshot(selection | self.draft_outside)

        as_user.action_repair()

        self.assertEqual(self._snapshot(selection | self.draft_outside), after_first)

    def test_ordinary_user_repairs_with_their_own_rights(self):
        """C7: no system group needed, and no elevation to reach an invisible company."""
        self.assertFalse(self.user_single.has_group('base.group_system'))
        before_b = self._snapshot(self.draft_b)
        drafts = self.draft_early | self.draft_same_1

        self._as(self.user_single, drafts, self.company_a).action_repair()

        self.assertEqual(self.draft_early.sequence, 100)
        self.assertEqual(self.draft_same_1.sequence, 200)
        self.assertEqual(self._snapshot(self.draft_b), before_b)
