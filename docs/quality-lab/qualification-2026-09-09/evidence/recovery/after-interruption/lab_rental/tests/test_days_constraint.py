from psycopg2 import IntegrityError

from odoo.tests.common import TransactionCase, tagged
from odoo.tools import mute_logger


@tagged('post_install', '-at_install')
class TestLabRentalDaysConstraint(TransactionCase):
    """Vérifie la contrainte SQL 'days >= 0' sur lab.rental (D-31)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rental_model = cls.env['lab.rental']

    def test_create_negative_days_is_rejected(self):
        """Une création avec days=-1 est refusée par la contrainte CHECK."""
        with self.cr.savepoint(), mute_logger('odoo.sql_db'), self.assertRaises(IntegrityError):
            self.rental_model.create({
                'name': 'Location invalide',
                'days': -1,
                'daily_rate': 10.0,
            })
            self.env.flush_all()

        # aucun enregistrement partiel n'a survécu à la tentative
        self.assertFalse(
            self.rental_model.search([('name', '=', 'Location invalide')]),
            "La tentative rejetée ne doit laisser aucun enregistrement partiel.",
        )

    def test_write_negative_days_is_rejected(self):
        """Un write(days=-1) sur un enregistrement existant valide est refusé."""
        rental = self.rental_model.create({
            'name': 'Location valide',
            'days': 5,
            'daily_rate': 10.0,
        })
        self.env.flush_all()

        with self.cr.savepoint(), mute_logger('odoo.sql_db'), self.assertRaises(IntegrityError):
            rental.write({'days': -1})
            self.env.flush_all()

        # conservation : l'enregistrement existe toujours avec ses valeurs d'avant tentative
        rental.invalidate_recordset()
        self.assertEqual(rental.days, 5)
        self.assertEqual(rental.daily_rate, 10.0)
        self.assertEqual(rental.amount_total, 50.0)

    def test_zero_days_is_accepted(self):
        """days=0 est accepté sans particularité, à la création comme en écriture."""
        rental = self.rental_model.create({
            'name': 'Location à jour zéro',
            'days': 0,
            'daily_rate': 25.0,
        })
        self.env.flush_all()
        self.assertEqual(rental.days, 0)
        self.assertEqual(rental.amount_total, 0.0)

        other = self.rental_model.create({
            'name': 'Location à repasser à zéro',
            'days': 3,
            'daily_rate': 25.0,
        })
        other.write({'days': 0})
        self.env.flush_all()
        self.assertEqual(other.days, 0)
        self.assertEqual(other.amount_total, 0.0)

    def test_amount_total_matches_days_times_daily_rate(self):
        """amount_total reste days * daily_rate, y compris pour days=0."""
        rental = self.rental_model.create({
            'name': 'Location calcul',
            'days': 7,
            'daily_rate': 12.5,
        })
        self.assertEqual(rental.amount_total, 7 * 12.5)

        rental.write({'days': 0})
        self.assertEqual(rental.amount_total, 0.0)

        rental.write({'days': 4, 'daily_rate': 3.0})
        self.assertEqual(rental.amount_total, 12.0)

    def test_rejected_write_preserves_existing_valid_rental(self):
        """Après un write(days=-1) rejeté, l'enregistrement valide existe
        toujours en base avec ses valeurs d'avant tentative, et aucun
        enregistrement partiel n'a été créé à côté."""
        rental = self.rental_model.create({
            'name': 'Location à préserver',
            'days': 2,
            'daily_rate': 15.0,
        })
        self.env.flush_all()
        rental_id = rental.id

        with self.cr.savepoint(), mute_logger('odoo.sql_db'), self.assertRaises(IntegrityError):
            rental.write({'days': -1})
            self.env.flush_all()

        # relecture indépendante du cache : l'enregistrement existe toujours,
        # avec les valeurs d'avant la tentative
        rental.invalidate_recordset()
        reread = self.rental_model.browse(rental_id)
        self.assertTrue(reread.exists())
        self.assertEqual(reread.days, 2)
        self.assertEqual(reread.daily_rate, 15.0)
        self.assertEqual(reread.amount_total, 30.0)

        # aucun enregistrement partiel n'a été créé pendant la tentative
        self.assertEqual(
            self.rental_model.search_count([('name', '=', 'Location à préserver')]),
            1,
        )
