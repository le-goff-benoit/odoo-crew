from psycopg2.errors import CheckViolation

from odoo.tests import tagged
from odoo.tools import mute_logger

from .common import LabRentalCommon


@tagged('post_install', '-at_install')
class TestRentalDays(LabRentalCommon):
    def test_negative_days_create(self):
        """Reject negative days for both kinds without persisting a record."""
        for kind in ('rental', 'loan'):
            with self.subTest(kind=kind):
                name = f'Invalid {kind}'
                with self.assertRaises(CheckViolation), mute_logger('odoo.sql_db'):
                    self.env['lab.rental'].create({
                        'name': name, 'kind': kind, 'days': -1, 'daily_rate': 12.5,
                    })
                    self.env.flush_all()
                self.assertFalse(self.env['lab.rental'].search([('name', '=', name)]))
        self.rental.invalidate_recordset()
        self.assertRecordValues(self.rental, [{'days': 2, 'daily_rate': 12.5, 'amount_total': 25}])

    def test_negative_days_write_preserves_rental(self):
        """Roll back every changed value and allow valid edits after rejection."""
        for kind in ('rental', 'loan'):
            with self.subTest(kind=kind):
                self.rental.write({'kind': kind, 'days': 2, 'daily_rate': 12.5})
                self.env.flush_all()
                with self.assertRaises(CheckViolation), mute_logger('odoo.sql_db'):
                    self.rental.write({'days': -1, 'daily_rate': 99, 'name': 'Rejected change'})
                    self.env.flush_all()
                self.rental.invalidate_recordset()
                self.assertRecordValues(self.rental, [{
                    'name': 'Valid rental', 'kind': kind,
                    'days': 2, 'daily_rate': 12.5, 'amount_total': 25,
                }])
                self.rental.write({'days': 3})
                self.env.flush_all()
                self.rental.invalidate_recordset()
                self.assertRecordValues(self.rental, [{'days': 3, 'amount_total': 37.5}])

    def test_zero_days(self):
        """Accept explicit, default and updated zero durations."""
        for kind in ('rental', 'loan'):
            with self.subTest(kind=kind):
                rentals = self.env['lab.rental'].create([
                    {'name': 'Explicit zero', 'kind': kind, 'days': 0, 'daily_rate': 12.5},
                    {'name': 'Default zero', 'kind': kind, 'daily_rate': 12.5},
                ])
                self.rental.write({'kind': kind, 'days': 0})
                self.env.flush_all()
                records = rentals | self.rental
                records.invalidate_recordset()
                self.assertRecordValues(records, [{'days': 0, 'amount_total': 0}] * 3)

    def test_total_calculation_unchanged(self):
        """Keep days times rate for both kinds, including zero and negative rates."""
        for kind in ('rental', 'loan'):
            with self.subTest(kind=kind):
                rental = self.env['lab.rental'].create({
                    'name': 'Total calculation', 'kind': kind, 'days': 2, 'daily_rate': 12.5,
                })
                self.assertEqual(rental.amount_total, 25)
                rental.write({'days': 3})
                self.assertEqual(rental.amount_total, 37.5)
                rental.write({'daily_rate': 7.5})
                self.assertEqual(rental.amount_total, 22.5)
                rental.write({'daily_rate': -7.5})
                self.assertEqual(rental.amount_total, -22.5)
                rental.write({'daily_rate': 0})
                self.env.flush_all()
                rental.invalidate_recordset()
                self.assertEqual(rental.amount_total, 0)
