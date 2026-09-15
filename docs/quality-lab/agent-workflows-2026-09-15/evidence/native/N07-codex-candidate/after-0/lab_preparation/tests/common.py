from odoo.tests.common import TransactionCase


class PreparationCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Preparation = cls.env['lab.preparation']

    def make_preparation(self, **values):
        return self.Preparation.create({'name': 'N-17', 'ordered_qty': 10, **values})

    def snapshot(self, records):
        return records.read([
            'name', 'state', 'ordered_qty', 'delivered_qty',
            'prepared_qty', 'manual', 'parent_id', 'write_date',
        ])
