import runpy
from pathlib import Path

from psycopg2.errors import CheckViolation

from odoo.tests import tagged
from odoo.tools import SQL, mute_logger

from .common import LabRentalCommon


@tagged('post_install', '-at_install')
class TestPreparation(LabRentalCommon):

    def test_rental_threshold(self):
        """Le forfait de 12 EUR commence à quatre jours inclus."""
        records = self.env['lab.rental'].create([
            {'name': f'Location {days}', 'days': days, 'daily_rate': 10}
            for days in (3, 4, 5)
        ])
        self.assertStoredTotals(records, [30, 52, 62])

    def test_loans_excluded(self):
        """Les prêts ne reçoivent jamais de frais de préparation."""
        records = self.env['lab.rental'].create([
            {'name': f'Prêt {days}', 'kind': 'loan', 'days': days, 'daily_rate': 10}
            for days in (3, 4, 5)
        ])
        self.assertStoredTotals(records, [30, 40, 50])

    def test_zero_and_decimal_amounts(self):
        """Accepter zéro et conserver les décimales sans arrondi ajouté."""
        records = self.env['lab.rental'].create([
            {'name': 'Durée nulle', 'days': 0, 'daily_rate': 10},
            {'name': 'Tarif nul', 'days': 4, 'daily_rate': 0},
            {'name': 'Prêt gratuit', 'kind': 'loan', 'days': 4, 'daily_rate': 0},
            {'name': 'Décimales', 'days': 4, 'daily_rate': 10.1234},
        ])
        self.assertStoredTotals(records, [0, 12, 0, 52.4936])

    def test_days_recompute_both_directions(self):
        """Passer le seuil dans les deux sens ajoute puis retire les frais."""
        record = self.env['lab.rental'].create({'name': 'Durée', 'days': 3, 'daily_rate': 10})
        self.assertStoredTotals(record, [30])
        record.days = 4
        self.assertStoredTotals(record, [52])
        record.days = 3
        self.assertStoredTotals(record, [30])

    def test_rate_recompute(self):
        """Le tarif modifie la base mais le forfait reste fixe."""
        record = self.env['lab.rental'].create({'name': 'Tarif', 'days': 4, 'daily_rate': 10})
        self.assertStoredTotals(record, [52])
        record.daily_rate = 20
        self.assertStoredTotals(record, [92])
        record.daily_rate = 0
        self.assertStoredTotals(record, [12])

    def test_kind_recompute_batch(self):
        """La conversion en lot location/prêt recalcule chaque total."""
        records = self.env['lab.rental'].create([
            {'name': 'Sous le seuil', 'days': 3, 'daily_rate': 10},
            {'name': 'Au seuil', 'days': 4, 'daily_rate': 10},
        ])
        self.assertStoredTotals(records, [30, 52])
        records.write({'kind': 'loan'})
        self.assertStoredTotals(records, [30, 40])
        records.write({'kind': 'rental'})
        self.assertStoredTotals(records, [30, 52])
        records.write({'days': 5, 'daily_rate': 20})
        self.assertStoredTotals(records, [112, 112])

    def test_negative_inputs_rejected(self):
        """Refuser chaque entrée négative en création et modification."""
        record = self.env['lab.rental'].create({'name': 'Zéro autorisé'})
        self.assertStoredTotals(record, [0])
        for field in ('days', 'daily_rate'):
            with self.subTest(field=field, operation='create'):
                with mute_logger('odoo.sql_db'), self.assertRaises(CheckViolation), self.env.cr.savepoint():
                    self.env['lab.rental'].create({'name': 'Invalide', field: -1})
            with self.subTest(field=field, operation='write'):
                with mute_logger('odoo.sql_db'), self.assertRaises(CheckViolation), self.env.cr.savepoint():
                    record.write({field: -1})
                    record.flush_recordset()

    def test_migration_existing_totals_idempotent(self):
        """Corriger les valeurs historiques une seule fois sans altérer les entrées."""
        records = self.env['lab.rental'].create([
            {'name': 'Ancienne location', 'days': 4, 'daily_rate': 10},
            {'name': 'Ancien prêt', 'kind': 'loan', 'days': 4, 'daily_rate': 10},
        ])
        records.flush_recordset()
        # Simuler en SQL les valeurs stockées avant D-02 sans déclencher le compute.
        self.env.cr.execute(SQL(
            'UPDATE lab_rental SET amount_total = 40 WHERE id IN %s',
            tuple(records.ids),
        ))
        records.invalidate_recordset()
        self.assertStoredTotals(records, [40, 40])
        inputs = ['name', 'days', 'daily_rate', 'kind', 'write_date']
        before = records.read(inputs)
        path = Path(__file__).resolve().parents[1] / 'migrations/19.0.1.0.1/post-recompute-amount-total.py'
        migrate = runpy.run_path(str(path))['migrate']
        migrate(self.env.cr, '19.0.1.0.0')
        self.assertStoredTotals(records, [52, 40])
        migrate(self.env.cr, '19.0.1.0.0')
        self.assertStoredTotals(records, [52, 40])
        records.invalidate_recordset()
        self.assertEqual(records.read(inputs), before)
