from psycopg2.errors import CheckViolation

from odoo.tests import tagged
from odoo.tools import mute_logger

from .common import LabRentalCommon


@tagged('post_install', '-at_install')
class TestRentalDays(LabRentalCommon):

    def test_negative_days_create_rejected(self):
        """D-31 : refuser la création négative sans laisser de ligne."""
        for kind in ('rental', 'loan'):
            with self.subTest(kind=kind):
                count = self.Rental.search_count([])
                with self.assertRaises(CheckViolation), mute_logger('odoo.sql_db'), self.env.cr.savepoint():
                    self.Rental.create({
                        'name': 'Durée invalide', 'kind': kind,
                        'days': -1, 'daily_rate': 12.5,
                    })
                    self.env.flush_all()
                self.assertEqual(self.Rental.search_count([]), count)

    def test_negative_days_write_preserves_valid_rental(self):
        """D-31 : après rejet, relire la location intacte et la modifier."""
        for kind in ('rental', 'loan'):
            with self.subTest(kind=kind):
                rental = self.Rental.create({
                    'name': 'Location valide', 'kind': kind,
                    'days': 3, 'daily_rate': 12.5,
                })
                self.env.flush_all()
                with self.assertRaises(CheckViolation), mute_logger('odoo.sql_db'), self.env.cr.savepoint():
                    rental.write({'days': -1, 'daily_rate': 99})
                    self.env.flush_all()
                rental.invalidate_recordset()
                self.assertTrue(rental.exists())
                self.assertEqual(rental.days, 3)
                self.assertEqual(rental.daily_rate, 12.5)
                self.assertEqual(rental.amount_total, 37.5)
                rental.write({'days': 4})
                self.env.flush_all()
                rental.invalidate_recordset()
                self.assertEqual(rental.amount_total, 50)

    def test_zero_days_create_and_write_allowed(self):
        """D-31 : zéro est inclus, en création et en modification."""
        rental = self.Rental.create({
            'name': 'Durée nulle', 'days': 0, 'daily_rate': 12.5,
        })
        self.env.flush_all()
        rental.invalidate_recordset()
        self.assertEqual(rental.days, 0)
        self.assertEqual(rental.amount_total, 0)
        rental.write({'days': 3})
        self.env.flush_all()
        rental.invalidate_recordset()
        self.assertEqual(rental.amount_total, 37.5)
        rental.write({'days': 0})
        self.env.flush_all()
        rental.invalidate_recordset()
        self.assertEqual(rental.days, 0)
        self.assertEqual(rental.amount_total, 0)

    def test_total_and_daily_rate_rules_unchanged(self):
        """D-31 : garder jours * tarif, y compris pour un prêt."""
        for kind in ('rental', 'loan'):
            with self.subTest(kind=kind):
                rental = self.Rental.create({
                    'name': 'Calcul existant', 'kind': kind,
                    'days': 3, 'daily_rate': 12.5,
                })
                self.assertEqual(rental.amount_total, 37.5)
                for rate, expected in ((20, 60), (0, 0), (-5, -15)):
                    rental.write({'daily_rate': rate})
                    self.env.flush_all()
                    rental.invalidate_recordset()
                    self.assertEqual(rental.amount_total, expected)
