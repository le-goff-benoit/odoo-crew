from psycopg2 import IntegrityError

from odoo.tests import TransactionCase, tagged
from odoo.tools import mute_logger


@tagged('post_install', '-at_install')
class TestRentalDaysConstraint(TransactionCase):
    """Durées de location négatives refusées par la contrainte SQL (D-31)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rental = cls.env['lab.rental'].create({
            'name': 'Location de référence',
            'days': 5,
            'daily_rate': 12.0,
        })

    def test_constraint_is_in_database(self):
        """La contrainte est réellement posée sur la table, pas seulement dans le code."""
        self.env.cr.execute(
            """
            SELECT pg_get_constraintdef(oid)
              FROM pg_constraint
             WHERE conrelid = 'lab_rental'::regclass
               AND conname = 'lab_rental_check_days_positive'
            """
        )
        definition = self.env.cr.fetchone()
        self.assertTrue(definition, "La contrainte lab_rental_check_days_positive est absente de la base.")
        self.assertIn('days >= 0', definition[0])

    @mute_logger('odoo.sql_db')
    def test_create_negative_days_refused(self):
        """Une création avec des jours négatifs est refusée et ne laisse rien en base."""
        with self.assertRaises(IntegrityError):
            self.env['lab.rental'].create({
                'name': 'Location refusée',
                'days': -1,
                'daily_rate': 12.0,
            })
            self.env.flush_all()

        self.assertFalse(
            self.env['lab.rental'].search([('name', '=', 'Location refusée')]),
            "Aucun enregistrement ne doit subsister après le refus.",
        )

    @mute_logger('odoo.sql_db')
    def test_write_negative_days_refused(self):
        """Une modification vers des jours négatifs est refusée."""
        with self.assertRaises(IntegrityError):
            self.rental.days = -3
            self.env.flush_all()

    @mute_logger('odoo.sql_db')
    def test_valid_rental_survives_refusal(self):
        """Après un refus, la location valide garde sa durée et son total."""
        with self.assertRaises(IntegrityError):
            self.rental.days = -3
            self.env.flush_all()

        self.env.invalidate_all()
        self.assertEqual(self.rental.days, 5)
        self.assertEqual(self.rental.amount_total, 60.0)

    def test_zero_days_allowed(self):
        """Le zéro reste une durée valide et donne un total nul."""
        rental = self.env['lab.rental'].create({
            'name': 'Prêt du jour',
            'days': 0,
            'daily_rate': 12.0,
            'kind': 'loan',
        })
        self.env.flush_all()
        self.assertEqual(rental.days, 0)
        self.assertEqual(rental.amount_total, 0.0)

    def test_total_still_computed(self):
        """Le calcul du total existant est inchangé."""
        self.rental.days = 7
        self.assertEqual(self.rental.amount_total, 84.0)
