from odoo.tests.common import TransactionCase


class LabRentalCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        """Préparer le modèle métier sans dépendance envers les ventes."""
        super().setUpClass()
        cls.Rental = cls.env['lab.rental']

    def assertStoredTotals(self, records, expected):
        """Vérifier les montants après écriture et relecture hors cache ORM."""
        self.assertTrue(records._fields['amount_total'].store)
        records.flush_recordset()
        records.invalidate_recordset()
        for record, amount in zip(records, expected, strict=True):
            self.assertAlmostEqual(record.amount_total, amount, places=8)
