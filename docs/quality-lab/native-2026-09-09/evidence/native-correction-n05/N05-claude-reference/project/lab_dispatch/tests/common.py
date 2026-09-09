from odoo.tests.common import TransactionCase


class LabDispatchCommon(TransactionCase):
    """Jeu de données minimal partagé par les tests de recalcul."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Dispatch = cls.env['lab.dispatch']

    @classmethod
    def _new_dispatch(cls, name, state, snapshot_total, lines):
        """Crée un dossier avec ses lignes ; ``lines`` = [(quantity, price, cancelled)]."""
        return cls.Dispatch.create({
            'name': name,
            'state': state,
            'snapshot_total': snapshot_total,
            'line_ids': [
                (0, 0, {'quantity': quantity, 'price': price, 'cancelled': cancelled})
                for quantity, price, cancelled in lines
            ],
        })
