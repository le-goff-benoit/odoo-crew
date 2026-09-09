from odoo.tests.common import TransactionCase


class LabDispatchCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Dispatch = cls.env['lab.dispatch']

    @classmethod
    def _build_dispatch(cls, name, state, snapshot_total, lines):
        """Create a dispatch with its lines; `lines` is a list of (qty, price, cancelled)."""
        return cls.Dispatch.create({
            'name': name,
            'state': state,
            'snapshot_total': snapshot_total,
            'line_ids': [
                (0, 0, {'quantity': quantity, 'price': price, 'cancelled': cancelled})
                for quantity, price, cancelled in lines
            ],
        })
