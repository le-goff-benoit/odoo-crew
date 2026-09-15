from odoo.tests import tagged
from odoo.exceptions import AccessError

from .common import LabRegisterCommon


@tagged('post_install', '-at_install')
class TestRegisterRepair(LabRegisterCommon):

    def test_draft_sequences_and_snapshot(self):
        """C1/C2: drafts of the active company get 100, 200 and totals ignore cancelled lines."""
        (self.draft_early + self.draft_late).action_repair()

        self.assertEqual(self.draft_early.sequence, 100)
        self.assertEqual(self.draft_late.sequence, 200)
        self.assertEqual(self.draft_early.snapshot_total, 20.0)
        self.assertEqual(self.draft_late.snapshot_total, 20.0)

    def test_issued_record_is_preserved(self):
        """C3: a mixed selection ignores issued records instead of renumbering them."""
        (self.draft_early + self.issued + self.draft_late).action_repair()

        self.assert_untouched(self.issued, 17, 555.0, 'ISSUED/005', 'issued')
        self.assertEqual(self.draft_early.sequence, 100)
        self.assertEqual(self.draft_late.sequence, 200)

    def test_other_company_is_preserved(self):
        """C4: the active company decides, even when the user may access several."""
        self.assertIn(self.other_draft.company_id, self.env.user.company_ids)
        self.assertEqual(self.env.company, self.company_main)

        (self.draft_early + self.other_draft).action_repair()

        self.assert_untouched(self.other_draft, 80, 666.0, 'OTHER/DRAFT', 'draft')

    def test_records_out_of_self_are_untouched(self):
        """C5: action_repair works on self, not on the whole table."""
        self.draft_early.action_repair()

        self.assertEqual(self.draft_early.sequence, 100)
        self.assert_untouched(self.draft_late, 10, 123.0, 'DRAFT-B', 'draft')
        self.assert_untouched(self.issued, 17, 555.0, 'ISSUED/005', 'issued')
        self.assert_untouched(self.other_draft, 80, 666.0, 'OTHER/DRAFT', 'draft')

    def test_repair_is_idempotent(self):
        """C6: replaying the repair changes no value."""
        records = self.draft_early + self.draft_late
        records.action_repair()
        before = [(r.sequence, r.snapshot_total) for r in records]

        records.action_repair()

        self.assertEqual([(r.sequence, r.snapshot_total) for r in records], before)

    def test_plain_user_can_repair_without_sudo(self):
        """C7: a base.group_user member repairs his own drafts under his own rights."""
        plain_user = self.env['res.users'].create({
            'name': 'Repair Operator',
            'login': 'repair_operator',
            'group_ids': [(6, 0, [self.env.ref('base.group_user').id])],
            'company_id': self.company_main.id,
            'company_ids': [(6, 0, self.company_main.ids)],
        })
        # He only belongs to the main company: his environment carries that one alone.
        drafts = (self.draft_early + self.draft_late).with_user(plain_user).with_context(
            allowed_company_ids=self.company_main.ids,
        )

        drafts.action_repair()

        self.assertEqual(drafts.mapped('sequence'), [100, 200])
        # The other company stays out of his reach: the record rule hides it.
        with self.assertRaises(AccessError):
            self.other_draft.with_user(plain_user).with_context(
                allowed_company_ids=self.company_main.ids,
            ).read(['sequence'])
