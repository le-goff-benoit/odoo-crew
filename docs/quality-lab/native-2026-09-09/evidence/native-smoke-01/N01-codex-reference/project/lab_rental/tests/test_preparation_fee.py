from odoo.tests import tagged

from .common import LabRentalCommon


@tagged('post_install', '-at_install')
class TestPreparationFee(LabRentalCommon):
    """Contrat métier D-02 : forfait fixe, seuil inclusif et prêts exclus."""

    def test_rental_threshold(self):
        """Appliquer 12 EUR à partir de quatre jours, sans pourcentage."""
        records = self.Rental.create([
            {'name': f'Location {days}', 'days': days, 'daily_rate': 10}
            for days in (3, 4, 5)
        ])
        self.assertStoredTotals(records, [30, 52, 62])

    def test_loans_excluded(self):
        """Exclure les prêts avant, au seuil et après le seuil."""
        records = self.Rental.create([
            {'name': f'Prêt {days}', 'kind': 'loan', 'days': days, 'daily_rate': 10}
            for days in (3, 4, 5)
        ])
        self.assertStoredTotals(records, [30, 40, 50])

    def test_zero_and_decimal_amounts(self):
        """Préserver les zéros et ne pas ajouter d'arrondi monétaire."""
        records = self.Rental.create([
            {'name': 'Défauts'},
            {'name': 'Durée nulle', 'days': 0, 'daily_rate': 20},
            {'name': 'Location gratuite', 'days': 4, 'daily_rate': 0},
            {'name': 'Prêt gratuit', 'kind': 'loan', 'days': 4, 'daily_rate': 0},
            {'name': 'Décimales', 'days': 4, 'daily_rate': 1.234},
        ])
        self.assertStoredTotals(records, [0, 0, 12, 0, 16.936])

    def test_days_recompute_both_directions(self):
        """Ajouter et retirer les frais en franchissant le seuil."""
        record = self.Rental.create({'name': 'Durée', 'days': 3, 'daily_rate': 10})
        self.assertStoredTotals(record, [30])
        record.days = 4
        self.assertStoredTotals(record, [52])
        record.days = 3
        self.assertStoredTotals(record, [30])

    def test_daily_rate_recompute(self):
        """Recalculer le tarif tout en conservant un forfait fixe."""
        record = self.Rental.create({'name': 'Tarif', 'days': 4, 'daily_rate': 10})
        self.assertStoredTotals(record, [52])
        record.daily_rate = 20
        self.assertStoredTotals(record, [92])
        record.daily_rate = 0
        self.assertStoredTotals(record, [12])

    def test_kind_recompute_both_directions(self):
        """Retirer et rétablir les frais lors du changement de type."""
        record = self.Rental.create({'name': 'Type', 'days': 4, 'daily_rate': 10})
        self.assertStoredTotals(record, [52])
        record.kind = 'loan'
        self.assertStoredTotals(record, [40])
        record.kind = 'rental'
        self.assertStoredTotals(record, [52])

    def test_mixed_batch_write_and_search(self):
        """Recalculer un lot hétérogène et rechercher son total stocké."""
        records = self.Rental.create([
            {'name': 'Courte', 'days': 3, 'daily_rate': 10},
            {'name': 'Longue', 'days': 5, 'daily_rate': 10},
            {'name': 'Prêt', 'kind': 'loan', 'days': 4, 'daily_rate': 10},
        ])
        self.assertStoredTotals(records, [30, 62, 40])
        records.write({'daily_rate': 20})
        self.assertStoredTotals(records, [60, 112, 80])
        self.assertEqual(self.Rental.search([
            ('id', 'in', records.ids), ('amount_total', '=', 112),
        ]), records[1])
