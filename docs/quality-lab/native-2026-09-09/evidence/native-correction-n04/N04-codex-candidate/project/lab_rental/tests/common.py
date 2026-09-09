from odoo.tests.common import TransactionCase


class LabRentalCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        """Préparer le modèle de location synthétique."""
        super().setUpClass()
        cls.Rental = cls.env['lab.rental']
