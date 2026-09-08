from odoo import Command
from odoo.exceptions import AccessError, UserError
from odoo.tests.common import TransactionCase, tagged, new_test_user


@tagged('post_install', '-at_install')
class TestExpenseContract(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.worker = new_test_user(cls.env, login='expense_worker', groups='base.group_user')
        cls.manager = new_test_user(cls.env, login='expense_manager', groups='base.group_user,quality_case.group_approver')
        cls.south = cls.env['res.company'].create({'name': 'Synthetic expense South'})
        cls.other = new_test_user(cls.env, login='expense_other', groups='base.group_user,quality_case.group_approver',
                                  company_id=cls.south.id, company_ids=[Command.set([cls.south.id])])

    def request(self, amount=300, user=None):
        return self.env['quality_case.expense'].with_user(user or self.worker).create({'name': 'Synthetic expense', 'amount': amount})

    def test_boundary_and_approval(self):
        small = self.request(250)
        small.action_pay()
        self.assertEqual(small.state, 'paid')
        large = self.request(250.01)
        try: large.action_pay()
        except UserError: pass
        self.assertEqual(large.state, 'draft')
        large.with_user(self.manager).action_approve()
        large.action_pay()
        self.assertEqual(large.state, 'paid')

    def test_increase_revalidates_decrease_and_unchanged_do_not(self):
        record = self.request()
        record.with_user(self.manager).action_approve()
        record.write({'amount': 290})
        self.assertTrue(record.approved)
        record.write({'amount': 290, 'company_id': record.company_id.id})
        self.assertTrue(record.approved)
        record.write({'amount': 295})
        self.assertFalse(record.approved)

    def test_no_self_or_unprivileged_approval(self):
        for user in (self.worker, self.manager):
            record = self.request(user=user)
            try: record.action_approve()
            except AccessError: pass
            self.assertFalse(record.approved)

    def test_defaults_cannot_forge_workflow(self):
        for context in ({'default_approved': True}, {'default_state': 'paid'}):
            try:
                record = self.env['quality_case.expense'].with_user(self.worker).with_context(**context).create({'name': 'Defaults', 'amount': 300})
            except AccessError:
                continue
            self.assertFalse(record.approved)
            self.assertEqual(record.state, 'draft')

    def test_direct_values_and_context_cannot_forge_workflow(self):
        for context in ({}, {'quality_case_privileged_write': True}, {'quality_case_protected_write': True}, {'skip_approval': True}):
            record = self.request().with_context(**context)
            for vals in ({'approved': True}, {'state': 'paid'}):
                try: record.write(vals)
                except AccessError: pass
                self.assertFalse(record.approved)
                self.assertEqual(record.state, 'draft')

    def test_company_rules_apply_to_actions(self):
        record = self.request().with_user(self.other)
        with self.assertRaises(AccessError): record.action_approve()
        with self.assertRaises(AccessError): record.action_pay()
