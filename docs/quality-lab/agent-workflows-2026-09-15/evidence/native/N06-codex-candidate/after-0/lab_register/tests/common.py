from odoo import Command
from odoo.tests.common import TransactionCase, new_test_user


class LabRegisterCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.env.company
        cls.company_b = cls.env['res.company'].create({'name': 'Repair company B'})
        cls.user = new_test_user(
            cls.env, login='repair_ordinary', groups='base.group_user',
            company_id=cls.company_a.id,
            company_ids=[Command.set((cls.company_a | cls.company_b).ids)],
        )
        cls.register = cls.env['lab.register'].with_user(cls.user).with_context(
            allowed_company_ids=[cls.company_a.id, cls.company_b.id],
        )

    def make_register(self, name, date='2020-01-01', **values):
        return self.register.create({
            'name': name,
            'date_document': date,
            'sequence': 81,
            'snapshot_total': 999,
            'reference': name,
            'line_ids': [
                Command.create({'quantity': 2, 'price': 10}),
                Command.create({'quantity': 5, 'price': 99, 'cancelled': True}),
            ],
            **values,
        })

    def snapshot(self, records):
        records.flush_recordset()
        return records.read([
            'state', 'sequence', 'snapshot_total', 'reference', 'company_id',
            'date_document', 'name', 'line_ids', 'write_date', 'write_uid',
        ])
