from odoo import Command
from odoo.tests.common import TransactionCase


class LabDispatchCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        """Create synthetic dossiers with distinct stored and line totals."""
        super().setUpClass()
        cls.draft, cls.done = cls.env['lab.dispatch'].create([
            {
                'name': name,
                'state': state,
                'snapshot_total': total,
                'line_ids': [
                    Command.create({'quantity': 2, 'price': 10}),
                    Command.create({'quantity': 3, 'price': 30, 'cancelled': True}),
                ],
            }
            for name, state, total in [('Draft', 'draft', 999), ('Done', 'done', 777)]
        ])
