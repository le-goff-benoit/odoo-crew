from unittest.mock import patch

from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import RegisterCommon


@tagged('post_install', '-at_install')
class TestRepair(RegisterCommon):
    def test_mixed_selection(self):
        """B-42: only selected drafts in the active company may change."""
        protected = self.unselected | self.issued | self.other
        before = self.snapshot(protected)
        lines = self.snapshot(self.all_records.line_ids)
        selected = self.late | self.other | self.tie | self.issued | self.early
        actor = self.as_operator(selected)
        self.assertFalse(actor.env.su)
        self.assertTrue(actor.action_repair())
        self.assertEqual(self.early.sequence, 100)
        self.assertEqual(self.tie.sequence, 200)
        self.assertEqual(self.late.sequence, 300)
        self.assertEqual((self.early | self.tie | self.late).mapped('snapshot_total'), [20, 20, 20])
        self.assertEqual(self.snapshot(protected), before)
        self.assertEqual(self.snapshot(self.all_records.line_ids), lines)
        for record in self.early | self.tie | self.late:
            self.assertEqual(record.state, 'draft')
            self.assertEqual(record.reference, record.name)

    def test_active_company_and_empty(self):
        """Access to two companies does not merge their repair scope."""
        before = self.snapshot(self.all_records - self.other)
        self.as_operator(self.all_records, self.company_b).action_repair()
        self.assertEqual((self.other.sequence, self.other.snapshot_total), (100, 20))
        self.assertEqual(self.snapshot(self.all_records - self.other), before)
        before = self.snapshot(self.all_records)
        self.as_operator(self.register).action_repair()
        self.assertEqual(self.snapshot(self.all_records), before)

    def test_totals_and_replay(self):
        """Cancelled/empty lines and sub-cent differences retain exact semantics."""
        self.early.line_ids.unlink()
        self.tie.line_ids.write({'cancelled': True})
        self.late.line_ids.filtered(lambda line: not line.cancelled).write({
            'quantity': 1, 'price': 0.001,
        })
        actor = self.as_operator(self.late | self.tie | self.early)
        actor.action_repair()
        self.assertEqual((self.early | self.tie | self.late).mapped('snapshot_total'), [0, 0, 0.001])
        before = self.snapshot(self.all_records)
        with patch.object(type(actor), 'write', autospec=True) as write:
            actor.action_repair()
        write.assert_not_called()
        self.assertEqual(self.snapshot(self.all_records), before)

    def test_restricted_company(self):
        """An ordinary user cannot repair a forbidden company's record."""
        before = self.snapshot(self.all_records)
        actor = self.other.with_user(self.restricted).with_context(
            allowed_company_ids=self.company_a.ids,
        )
        self.assertFalse(actor.env.su)
        with self.assertRaises(AccessError), self.env.cr.savepoint():
            actor.action_repair()
        self.assertEqual(self.snapshot(self.all_records), before)
        with self.assertRaises(AccessError), self.env.cr.savepoint():
            actor.with_context(allowed_company_ids=self.company_b.ids).action_repair()
        self.assertEqual(self.snapshot(self.all_records), before)
        # The same restricted user can repair a permitted record.
        self.early.with_user(self.restricted).with_context(
            allowed_company_ids=self.company_a.ids,
        ).action_repair()
        self.assertEqual((self.early.sequence, self.early.snapshot_total), (100, 20))

    def test_write_rule(self):
        """Respect write rules even when no values need changing."""
        actor = self.as_operator(self.early)
        actor.action_repair()
        self.env['ir.rule'].create({
            'name': 'Deny register writes in this test',
            'model_id': self.env['ir.model']._get_id('lab.register'),
            'domain_force': "[('id', '=', 0)]",
            'perm_read': False, 'perm_write': True,
            'perm_create': False, 'perm_unlink': False,
        })
        before = self.snapshot(self.all_records)
        with self.assertRaises(AccessError), self.env.cr.savepoint():
            actor.action_repair()
        self.assertEqual(self.snapshot(self.all_records), before)
