from odoo.tests import tagged

from .common import LabRentalCommon


@tagged('post_install', '-at_install')
class TestPreparationFee(LabRentalCommon):

    def test_rental_threshold(self):
        """Le forfait unique commence à quatre jours inclus."""
        for days, expected in [(3, 30), (4, 52), (5, 62), (20, 212)]:
            with self.subTest(days=days):
                record = self.Rental.create({
                    'name': 'Location', 'days': days, 'daily_rate': 10,
                    'kind': 'rental',
                })
                self.assertStoredTotals(record, [expected])

    def test_loans_have_no_fee(self):
        """Les prêts conservent seulement le montant de base."""
        for days, expected in [(3, 30), (4, 40), (5, 50)]:
            with self.subTest(days=days):
                record = self.Rental.create({
                    'name': 'Prêt', 'days': days, 'daily_rate': 10,
                    'kind': 'loan',
                })
                self.assertStoredTotals(record, [expected])

    def test_zero_values(self):
        """Un tarif nul ne supprime pas le forfait d'une location éligible."""
        for kind, days, rate, expected in [
            ('rental', 0, 10, 0), ('loan', 0, 10, 0),
            ('rental', 0, 0, 0), ('loan', 0, 0, 0),
            ('rental', 3, 0, 0), ('rental', 4, 0, 12),
            ('loan', 4, 0, 0),
        ]:
            with self.subTest(kind=kind, days=days, rate=rate):
                record = self.Rental.create({
                    'name': 'Valeur nulle', 'kind': kind,
                    'days': days, 'daily_rate': rate,
                })
                self.assertStoredTotals(record, [expected])

    def test_decimal_rate(self):
        """Ne pas ajouter d'arrondi monétaire au calcul convenu."""
        records = self.Rental.create([
            {'name': 'Location décimale', 'days': 4, 'daily_rate': 1.2345},
            {'name': 'Prêt décimal', 'kind': 'loan', 'days': 4, 'daily_rate': 1.2345},
        ])
        self.assertStoredTotals(records, [16.938, 4.938])

    def test_days_changes(self):
        """Franchir le seuil dans les deux sens recalcule le forfait."""
        record = self.Rental.create({'name': 'Durée', 'days': 3, 'daily_rate': 10})
        self.assertStoredTotals(record, [30])
        for days, expected in [(4, 52), (5, 62), (3, 30), (0, 0)]:
            record.write({'days': days})
            self.assertStoredTotals(record, [expected])

    def test_daily_rate_changes(self):
        """Le forfait reste fixe quand seul le tarif varie."""
        record = self.Rental.create({'name': 'Tarif', 'days': 4, 'daily_rate': 10})
        self.assertStoredTotals(record, [52])
        record.write({'daily_rate': 20})
        self.assertStoredTotals(record, [92])
        record.write({'daily_rate': 0})
        self.assertStoredTotals(record, [12])

    def test_kind_changes(self):
        """Changer uniquement le type ajoute ou retire le forfait."""
        record = self.Rental.create({'name': 'Type', 'days': 4, 'daily_rate': 10})
        self.assertStoredTotals(record, [52])
        record.write({'kind': 'loan'})
        self.assertStoredTotals(record, [40])
        record.write({'kind': 'rental'})
        self.assertStoredTotals(record, [52])

    def test_mixed_batch(self):
        """Créer et modifier un lot hétérogène sans contaminer ses totaux."""
        records = self.Rental.create([
            {'name': 'Courte', 'days': 3, 'daily_rate': 10},
            {'name': 'Longue', 'days': 4, 'daily_rate': 10},
            {'name': 'Prêt', 'kind': 'loan', 'days': 4, 'daily_rate': 10},
        ])
        self.assertStoredTotals(records, [30, 52, 40])
        records.write({'daily_rate': 20})
        self.assertStoredTotals(records, [60, 92, 80])
