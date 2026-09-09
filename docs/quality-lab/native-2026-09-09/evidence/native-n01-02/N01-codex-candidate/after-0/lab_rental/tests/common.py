from odoo.tests.common import TransactionCase


class LabRentalCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        """Préparer le modèle autonome, dépendant uniquement de base."""
        super().setUpClass()
        cls.Rental = cls.env['lab.rental']

    def assertStoredTotals(self, records, expected):
        """Relire les totaux persistés après éviction du cache ORM."""
        self.assertTrue(records._fields['amount_total'].store)
        records.flush_recordset()
        records.invalidate_recordset()
        self.assertEqual(len(records), len(expected))
        for record, total in zip(records, expected):
            self.assertAlmostEqual(record.amount_total, total, places=9)
