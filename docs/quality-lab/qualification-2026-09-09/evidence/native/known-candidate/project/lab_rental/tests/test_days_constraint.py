from psycopg2.errors import CheckViolation

from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


@tagged('post_install', '-at_install')
class TestLabRentalDaysConstraint(TransactionCase):
    """Contrainte de table ``lab_rental_check_days_positive`` (décision D-31)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rental = cls.env['lab.rental'].create({
            'name': 'Location de référence',
            'days': 5,
            'daily_rate': 10.0,
        })

    def _read_days_in_db(self, rental):
        """Relire ``days`` en base, hors cache de l'ORM."""
        self.env.cr.execute('SELECT days FROM lab_rental WHERE id = %s', [rental.id])
        return self.env.cr.fetchone()[0]

    def test_create_negative_days_is_rejected(self):
        """A1 — une création à ``days = -1`` est refusée par la base."""
        with self.assertRaises(CheckViolation), mute_logger('odoo.sql_db'), self.env.cr.savepoint():
            self.env['lab.rental'].create({
                'name': 'Location négative',
                'days': -1,
                'daily_rate': 10.0,
            })
            self.env.flush_all()

    def test_write_negative_days_is_rejected(self):
        """A2 — une écriture à ``days = -3`` est refusée et la valeur reste 5."""
        with self.assertRaises(CheckViolation), mute_logger('odoo.sql_db'), self.env.cr.savepoint():
            self.rental.days = -3
            self.env.flush_all()

        self.rental.invalidate_recordset()
        self.assertEqual(self.rental.days, 5)
        self.assertEqual(self._read_days_in_db(self.rental), 5)

    def test_zero_days_is_accepted(self):
        """A3 — zéro jour reste autorisé et le total vaut 0."""
        rental = self.env['lab.rental'].create({
            'name': 'Location à zéro jour',
            'days': 0,
            'daily_rate': 10.0,
        })
        self.env.flush_all()
        self.assertEqual(rental.days, 0)
        self.assertEqual(rental.amount_total, 0.0)

    def test_positive_days_amount_total(self):
        """A4 — non-régression du total stocké : 4 jours au tarif de 12,5 donnent 50."""
        rental = self.env['lab.rental'].create({
            'name': 'Location de quatre jours',
            'days': 4,
            'daily_rate': 12.5,
        })
        self.assertEqual(rental.amount_total, 50.0)

    def test_valid_rental_survives_rejection(self):
        """A5 — un rejet n'altère pas les locations valides et le curseur reste utilisable."""
        valid = self.env['lab.rental'].create({
            'name': 'Location valide',
            'days': 3,
            'daily_rate': 20.0,
        })
        self.env.flush_all()

        with self.assertRaises(CheckViolation), mute_logger('odoo.sql_db'), self.env.cr.savepoint():
            self.env['lab.rental'].create({
                'name': 'Location négative',
                'days': -1,
                'daily_rate': 20.0,
            })
            self.env.flush_all()

        valid.invalidate_recordset()
        self.assertEqual(valid.days, 3)
        self.assertEqual(valid.amount_total, 60.0)
        self.assertEqual(self._read_days_in_db(valid), 3)
        self.assertFalse(self.env['lab.rental'].search([('days', '<', 0)]))

    def test_constraint_exists_in_database(self):
        """A6 — la contrainte est réellement posée sur la table."""
        self.env.cr.execute(
            """
            SELECT pg_get_constraintdef(oid)
              FROM pg_constraint
             WHERE conrelid = 'lab_rental'::regclass
               AND conname = 'lab_rental_check_days_positive'
            """,
        )
        definition = self.env.cr.fetchone()
        self.assertTrue(definition, "La contrainte lab_rental_check_days_positive est absente de la base.")
        self.assertEqual(definition[0], 'CHECK ((days >= 0))')
