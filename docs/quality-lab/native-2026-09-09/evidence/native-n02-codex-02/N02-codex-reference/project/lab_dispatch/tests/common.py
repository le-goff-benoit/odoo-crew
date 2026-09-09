from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class LabDispatchCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.draft = cls.env['lab.dispatch'].create({
            'name': 'Draft',
            'snapshot_total': 999,
            'line_ids': [
                Command.create({'quantity': 2, 'price': 10}),
                Command.create({'quantity': 3, 'price': 30, 'cancelled': True}),
            ],
        })
        cls.done = cls.env['lab.dispatch'].create({
            'name': 'Validated',
            'state': 'done',
            'snapshot_total': 777,
            'line_ids': [
                Command.create({'quantity': 2, 'price': 10}),
                Command.create({'quantity': 3, 'price': 30, 'cancelled': True}),
            ],
        })

    def assertPersistedTotal(self, record, expected):
        """Vérifier le montant stocké après éviction du cache ORM."""
        record.flush_recordset()
        record.invalidate_recordset()
        self.assertEqual(record.snapshot_total, expected)
