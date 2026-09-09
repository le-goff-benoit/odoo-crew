from psycopg2.errors import CheckViolation

from odoo.tests import tagged
from odoo.tools import mute_logger

from .common import LabRentalCommon


@tagged('post_install', '-at_install')
class TestPreparationFees(LabRentalCommon):

    def test_rental_threshold(self):
        """Appliquer douze euros dès quatre jours, sans pourcentage."""
        records = self.Rental.create([
            {'name': f'Location {days}', 'days': days, 'daily_rate': 10, 'kind': 'rental'}
            for days in (3, 4, 5)
        ])
        self.assertStoredTotals(records, [30, 52, 62])

    def test_loans_excluded(self):
        """Exclure les prêts avant, à et après la borne."""
        records = self.Rental.create([
            {'name': f'Prêt {days}', 'days': days, 'daily_rate': 10, 'kind': 'loan'}
            for days in (3, 4, 5)
        ])
        self.assertStoredTotals(records, [30, 40, 50])

    def test_zero_values_and_defaults(self):
        """Accepter zéro et facturer le seul forfait si le tarif est nul."""
        records = self.Rental.create([
            {'name': 'Valeurs par défaut'},
            {'name': 'Zéro jour', 'days': 0, 'daily_rate': 10},
            {'name': 'Tarif nul', 'days': 4, 'daily_rate': 0},
            {'name': 'Prêt gratuit', 'days': 4, 'daily_rate': 0, 'kind': 'loan'},
        ])
        self.assertStoredTotals(records, [0, 0, 12, 0])

    def test_no_extra_rounding(self):
        """Conserver les décimales du tarif sans arrondi ajouté."""
        record = self.Rental.create({'name': 'Décimales', 'days': 4, 'daily_rate': 0.3333})
        self.assertStoredTotals(record, [13.3332])

    def test_days_recompute_both_directions(self):
        """Ajouter puis retirer les frais quand la durée franchit la borne."""
        record = self.Rental.create({'name': 'Durée variable', 'days': 3, 'daily_rate': 10})
        self.assertStoredTotals(record, [30])
        record.write({'days': 4})
        self.assertStoredTotals(record, [52])
        record.write({'days': 5})
        self.assertStoredTotals(record, [62])
        record.write({'days': 3})
        self.assertStoredTotals(record, [30])

    def test_rate_recompute(self):
        """Recalculer le tarif sans augmenter le forfait fixe."""
        record = self.Rental.create({'name': 'Tarif variable', 'days': 4, 'daily_rate': 10})
        self.assertStoredTotals(record, [52])
        record.write({'daily_rate': 20})
        self.assertStoredTotals(record, [92])
        record.write({'daily_rate': 0})
        self.assertStoredTotals(record, [12])

    def test_kind_recompute_both_directions(self):
        """Retirer les frais lors du passage en prêt et les rétablir en location."""
        record = self.Rental.create({'name': 'Type variable', 'days': 4, 'daily_rate': 10})
        self.assertStoredTotals(record, [52])
        record.write({'kind': 'loan'})
        self.assertStoredTotals(record, [40])
        record.write({'kind': 'rental'})
        self.assertStoredTotals(record, [52])

    def test_mixed_batch_and_no_cumulative_fee(self):
        """Calculer chaque élément du lot et garder un forfait unique au rejeu."""
        records = self.Rental.create([
            {'name': 'Location courte', 'days': 3, 'daily_rate': 10},
            {'name': 'Location longue', 'days': 5, 'daily_rate': 10},
            {'name': 'Prêt long', 'days': 5, 'daily_rate': 10, 'kind': 'loan'},
        ])
        self.assertStoredTotals(records, [30, 62, 50])
        for _iteration in range(2):
            records.write({'days': 4, 'daily_rate': 20})
            self.assertStoredTotals(records, [92, 92, 80])

    @mute_logger('odoo.sql_db')
    def test_negative_values_rejected_on_create(self):
        """Refuser chaque entrée négative, pour les prêts comme les locations."""
        for kind in ('rental', 'loan'):
            for field in ('days', 'daily_rate'):
                with self.subTest(kind=kind, field=field):
                    with self.assertRaisesRegex(CheckViolation, f'lab_rental_{field}_nonnegative'), self.env.cr.savepoint():
                        record = self.Rental.create({'name': 'Invalide', 'kind': kind, field: -1})
                        record.flush_recordset()

    @mute_logger('odoo.sql_db')
    def test_negative_values_rejected_on_write(self):
        """Préserver le montant valide après une modification refusée."""
        record = self.Rental.create({'name': 'Entrées valides', 'days': 4, 'daily_rate': 10})
        self.assertStoredTotals(record, [52])
        for field in ('days', 'daily_rate'):
            with self.subTest(field=field):
                with self.assertRaisesRegex(CheckViolation, f'lab_rental_{field}_nonnegative'), self.env.cr.savepoint():
                    record.write({field: -1})
                    record.flush_recordset()
                self.assertStoredTotals(record, [52])
