from odoo.tests.common import TransactionCase


class LabRentalCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """Prepare a valid rental whose persisted values can be checked."""
        super().setUpClass()
        cls.rental = cls.env['lab.rental'].create({
            'name': 'Valid rental',
            'days': 2,
            'daily_rate': 12.5,
        })
        cls.env.flush_all()
