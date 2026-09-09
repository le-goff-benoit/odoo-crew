from odoo.tests.common import TransactionCase


class LabRentalCommon(TransactionCase):
    """Fixtures du modèle autonome, qui ne dépend que de base."""

    @classmethod
    def setUpClass(cls):
        """Préparer l'accès au modèle de location."""
        super().setUpClass()
        cls.Rental = cls.env['lab.rental']

    def assertStoredTotals(self, records, expected):
        """Relire les montants stockés après vidage et invalidation du cache."""
        self.assertTrue(records._fields['amount_total'].store)
        self.env.flush_all()
        records.invalidate_recordset()
        for record, amount in zip(records, expected, strict=True):
            self.assertAlmostEqual(record.amount_total, amount)
