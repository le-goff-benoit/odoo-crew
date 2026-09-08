from odoo import Command
from odoo.exceptions import AccessError, UserError
from odoo.tests.common import TransactionCase, tagged, new_test_user


@tagged('post_install', '-at_install')
class TestDeliveryContract(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.north = cls.env.company
        cls.south = cls.env['res.company'].create({'name': 'Synthetic South'})
        cls.worker = new_test_user(cls.env, login='lab_worker', groups='base.group_user',
                                   company_id=cls.north.id, company_ids=[Command.set([cls.north.id])])
        cls.manager = new_test_user(cls.env, login='lab_manager', groups='base.group_user,quality_case.group_approver',
                                    company_id=cls.north.id, company_ids=[Command.set([cls.north.id])])
        cls.other = new_test_user(cls.env, login='lab_south', groups='base.group_user,quality_case.group_approver',
                                  company_id=cls.south.id, company_ids=[Command.set([cls.south.id])])

    def request(self, available, partial=True, user=None):
        return self.env['quality_case.delivery'].with_user(user or self.worker).create({
            'name': 'Synthetic request', 'ordered_qty': 80, 'available_qty': available,
            'accepts_partial': partial, 'company_id': self.north.id,
        })

    def test_threshold_and_full_delivery(self):
        for qty, partial, allowed in [(48, True, True), (47, True, False), (50, False, False), (80, False, True), (0, True, False)]:
            with self.subTest(qty=qty, partial=partial):
                record = self.request(qty, partial)
                if allowed:
                    record.action_ship()
                    self.assertEqual(record.state, 'done')
                else:
                    try: record.action_ship()
                    except UserError: pass
                    self.assertEqual(record.state, 'draft')

    def test_approval_revalidation_and_increase(self):
        record = self.request(40)
        record.with_user(self.manager).action_approve()
        record.write({'available_qty': 42})
        self.assertTrue(record.approved)
        record.write({'available_qty': 41})  # below last proposal, though above original approval
        self.assertFalse(record.approved)
        try: record.action_ship()
        except UserError: pass
        self.assertEqual(record.state, 'draft')
        record.with_user(self.manager).action_approve()
        record.action_ship()
        self.assertEqual(record.state, 'done')

    def test_no_self_approval_even_as_manager(self):
        record = self.request(40, user=self.manager)
        with self.assertRaises(AccessError):
            record.action_approve()
        self.assertFalse(record.approved)

    def test_no_forged_approval_or_state(self):
        record = self.request(40)
        for vals in ({'approved': True}, {'state': 'done'}):
            try:
                record.write(vals)
            except AccessError:
                pass
            self.assertFalse(record.approved)
            self.assertEqual(record.state, 'draft')
        with self.assertRaises(AccessError):
            record.action_approve()
        try:
            created = self.env['quality_case.delivery'].with_user(self.worker).create({
                'name': 'Forgery', 'ordered_qty': 80, 'available_qty': 40, 'approved': True})
        except AccessError:
            pass
        else:
            self.assertFalse(created.approved)
            self.assertEqual(created.state, 'draft')


    def test_other_company_denied_on_direct_access(self):
        record = self.request(40)
        other = record.with_user(self.other)
        with self.assertRaises(AccessError):
            other.read(['name'])
        with self.assertRaises(AccessError):
            other.action_approve()
        with self.assertRaises(AccessError):
            other.action_ship()
        self.assertFalse(record.approved)
        self.assertEqual(record.state, 'draft')

    def test_changed_customer_policy_invalidates_approval(self):
        record = self.request(40)
        record.with_user(self.manager).action_approve()
        record.write({'accepts_partial': False})
        self.assertFalse(record.approved)
        try: record.action_ship()
        except UserError: pass
        self.assertEqual(record.state, 'draft')

    def test_context_defaults_cannot_forge_approval_or_state(self):
        for context in ({'default_approved': True}, {'default_state': 'done'}):
            with self.subTest(context=context):
                model = self.env['quality_case.delivery'].with_user(self.worker).with_context(**context)
                # Either refuse the request or safely ignore the untrusted defaults.
                try:
                    record = model.create({'name': 'Context forgery', 'ordered_qty': 80, 'available_qty': 40})
                except AccessError:
                    continue
                self.assertFalse(record.approved)
                self.assertEqual(record.state, 'draft')

    def test_unchanged_policy_keeps_approval(self):
        record = self.request(40)
        record.with_user(self.manager).action_approve()
        record.write({'ordered_qty': 80, 'accepts_partial': True, 'company_id': self.north.id})
        self.assertTrue(record.approved)

    def test_caller_context_does_not_authorize_workflow_writes(self):
        record = self.request(40)
        for key in ('quality_case_protected_write', 'quality_case_privileged_write'):
            for vals in ({'approved': True}, {'state': 'done'}):
                try:
                    record.with_context(**{key: True}).write(vals)
                except AccessError:
                    pass
                self.assertFalse(record.approved)
                self.assertEqual(record.state, 'draft')
