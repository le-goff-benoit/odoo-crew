from odoo import Command
from odoo.tests import TransactionCase
from odoo.tests.common import new_test_user


class RegisterCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.env.company
        cls.company_b = cls.env['res.company'].create({'name': 'Repair B'})
        cls.operator = new_test_user(
            cls.env, login='repair_operator', groups='base.group_user',
            company_id=cls.company_a.id,
            company_ids=[Command.set((cls.company_a | cls.company_b).ids)],
        )
        cls.restricted = new_test_user(
            cls.env, login='repair_restricted', groups='base.group_user',
            company_id=cls.company_a.id,
            company_ids=[Command.set(cls.company_a.ids)],
        )
        cls.register = cls.env['lab.register']
        cls.early = cls.make_register('early', '2020-01-01')
        cls.tie = cls.make_register('tie', '2020-01-01')
        cls.late = cls.make_register('late', '2020-01-02')
        cls.unselected = cls.make_register('unselected', '2018-01-01')
        cls.issued = cls.make_register('issued', '2019-01-01', state='issued')
        cls.other = cls.make_register(
            'other', '2017-01-01', company_id=cls.company_b.id,
        )
        cls.all_records = (
            cls.early | cls.tie | cls.late | cls.unselected | cls.issued | cls.other
        )

    @classmethod
    def make_register(cls, name, date, **values):
        return cls.register.create({
            'name': name, 'date_document': date,
            'company_id': cls.company_a.id,
            'sequence': 17, 'snapshot_total': 555, 'reference': name,
            'line_ids': [
                Command.create({'quantity': 2, 'price': 10}),
                Command.create({'quantity': 5, 'price': 99, 'cancelled': True}),
            ],
            **values,
        })

    def as_operator(self, records, active=None):
        active = active or self.company_a
        other = self.company_b if active == self.company_a else self.company_a
        return records.with_user(self.operator).with_context(
            allowed_company_ids=[active.id, other.id],
        )

    def snapshot(self, records):
        records.flush_recordset()
        records.invalidate_recordset()
        return records.read()
