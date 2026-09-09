from odoo.tests import TransactionCase


class LabRentalCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Rental = cls.env['lab.rental']

    @classmethod
    def _create_rental(cls, name, kind='rental', days=0, daily_rate=0.0):
        return cls.Rental.create({
            'name': name,
            'kind': kind,
            'days': days,
            'daily_rate': daily_rate,
        })
