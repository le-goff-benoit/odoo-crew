from unittest.mock import patch

from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import LabRegisterCommon


@tagged('post_install', '-at_install')
class TestRepair(LabRegisterCommon):
    def test_mixed_selection_and_idempotence(self):
        late = self.make_register('late', '2020-01-02', line_ids=[
            Command.create({'quantity': 3, 'price': 5}),
        ])
        early = self.make_register('early')
        tied = self.make_register('tied', line_ids=[])
        issued = self.make_register('issued', '2019-01-01', state='issued',
                                    sequence=17, snapshot_total=555)
        other = self.make_register('other', company_id=self.company_b.id)
        unselected = self.make_register('unselected', '2018-01-01')
        excluded = issued | other | unselected
        before = self.snapshot(excluded)
        selected = late | tied | other | issued | early
        lines_before = selected.line_ids.read()
        self.assertFalse(selected.env.su)
        self.assertTrue(selected.action_repair())
        self.assertEqual((early.sequence, tied.sequence, late.sequence), (100, 200, 300))
        self.assertEqual((early.snapshot_total, tied.snapshot_total, late.snapshot_total), (20, 0, 15))
        self.assertEqual(self.snapshot(excluded), before)
        self.assertEqual(selected.line_ids.read(), lines_before)
        self.assertEqual(early.reference, 'early')
        after = self.snapshot(selected)
        with patch.object(type(selected), 'write', autospec=True) as write:
            self.assertTrue(selected.action_repair())
            write.assert_not_called()
        self.assertEqual(self.snapshot(selected), after)

    def test_active_company_switch(self):
        a = self.make_register('A')
        b = self.make_register('B', company_id=self.company_b.id)
        before = self.snapshot(a)
        selected = (a | b).with_context(
            allowed_company_ids=[self.company_b.id, self.company_a.id],
        )
        self.assertEqual(selected.env.company, self.company_b)
        self.assertTrue(selected.action_repair())
        self.assertEqual((b.sequence, b.snapshot_total), (100, 20))
        self.assertEqual(self.snapshot(a), before)

    def test_empty_and_excluded_only(self):
        draft = self.make_register('draft')
        issued = self.make_register('issued', state='issued')
        other = self.make_register('other', company_id=self.company_b.id)
        all_records = draft | issued | other
        before = self.snapshot(all_records)
        self.assertTrue(self.register.action_repair())
        self.assertTrue((issued | other).action_repair())
        self.assertEqual(self.snapshot(all_records), before)

    def test_cancelled_only_and_small_delta(self):
        cancelled = self.make_register('cancelled', line_ids=[
            Command.create({'quantity': 5, 'price': 99, 'cancelled': True}),
        ])
        tiny = self.make_register('tiny', snapshot_total=0.005, line_ids=[
            Command.create({'quantity': 1, 'price': 0.004}),
        ])
        (cancelled | tiny).action_repair()
        self.assertEqual((cancelled.sequence, tiny.sequence), (100, 200))
        self.assertEqual(cancelled.snapshot_total, 0)
        self.assertEqual(tiny.snapshot_total, 0.004)

    def test_write_rule_denial_is_atomic(self):
        allowed = self.make_register('allowed')
        denied = self.make_register('denied')
        before = self.snapshot(allowed | denied)
        self.env['ir.rule'].create({
            'name': 'Test denied repair write',
            'model_id': self.env['ir.model']._get_id('lab.register'),
            'domain_force': repr([('id', '!=', denied.id)]),
            'perm_read': False, 'perm_write': True,
            'perm_create': False, 'perm_unlink': False,
        })
        with self.assertRaises(AccessError), self.cr.savepoint():
            (allowed | denied).action_repair()
        self.assertEqual(self.snapshot(allowed | denied), before)

    def test_company_read_rule_and_acl(self):
        a = self.make_register('A')
        b = self.make_register('B', company_id=self.company_b.id)
        before = self.snapshot(a | b)
        restricted = b.with_context(allowed_company_ids=[self.company_a.id])
        with self.assertRaises(AccessError):
            restricted.read(['sequence'])
        with self.assertRaises(AccessError), self.cr.savepoint():
            restricted.action_repair()
        public = a.with_user(self.env.ref('base.public_user'))
        self.assertFalse(public.env.su)
        with self.assertRaises(AccessError), self.cr.savepoint():
            public.action_repair()
        self.assertEqual(self.snapshot(a | b), before)
