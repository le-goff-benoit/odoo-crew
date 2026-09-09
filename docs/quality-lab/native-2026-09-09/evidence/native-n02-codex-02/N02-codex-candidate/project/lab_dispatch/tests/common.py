from odoo.fields import Command
from odoo.tests.common import TransactionCase


class LabDispatchCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        """Prepare deliberately stale snapshots for both states."""
        super().setUpClass()
        cls.draft, cls.done = cls.env['lab.dispatch'].create([
            {
                'name': state,
                'state': state,
                'snapshot_total': total,
                'line_ids': [
                    Command.create({'quantity': 2, 'price': 10}),
                    Command.create({'quantity': 3, 'price': 30, 'cancelled': True}),
                ],
            }
            for state, total in [('draft', 999), ('done', 777)]
        ])

    def assertStoredTotal(self, record, expected):
        """Check the database value after flushing and clearing the cache."""
        record.flush_recordset()
        record.invalidate_recordset()
        self.assertEqual(record.snapshot_total, expected)
