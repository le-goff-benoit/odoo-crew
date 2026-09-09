from psycopg2 import IntegrityError

from odoo.tests.common import TransactionCase, tagged
from odoo.tools import mute_logger


@tagged('post_install', '-at_install')
class TestDaysConstraint(TransactionCase):
    """D-31 : lab.rental.days >= 0, contrainte SQL, zéro autorisé."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Rental = cls.env['lab.rental']

    def _reject(self, callback):
        """Joue une opération attendue refusée par la base.

        Le point de sauvegarde rend la transaction utilisable ensuite : sans lui,
        l'IntegrityError la laisse avortée et le critère C5 est intestable.
        """
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            with self.env.cr.savepoint():
                callback()
                self.env.flush_all()
        self.env.invalidate_all()

    def test_create_negatif_refuse(self):
        """C1 — une création avec des jours négatifs est refusée."""
        self._reject(lambda: self.Rental.create({'name': 'Création négative', 'days': -1, 'daily_rate': 10}))
        self.assertFalse(self.Rental.search_count([('name', '=', 'Création négative')]))

    def test_write_negatif_refuse(self):
        """C2 — passer les jours d'une location existante en négatif est refusé."""
        rental = self.Rental.create({'name': 'Location saine', 'days': 3, 'daily_rate': 10})
        self._reject(lambda: rental.write({'days': -5}))
        self.assertEqual(rental.days, 3, "la valeur d'origine doit être conservée")
        self.assertEqual(rental.amount_total, 30)

    def test_location_valide_conservee_apres_rejet(self):
        """C5 — une location valide créée avant un rejet subsiste intacte."""
        valide = self.Rental.create({'name': 'Location conservée', 'days': 4, 'daily_rate': 25})
        self._reject(lambda: self.Rental.create({'name': 'Location rejetée', 'days': -2, 'daily_rate': 25}))
        self.assertTrue(valide.exists(), 'la location valide ne doit pas disparaître avec le rejet')
        self.assertEqual(valide.days, 4)
        self.assertEqual(valide.amount_total, 100, 'le total de la location valide reste jours × tarif')
        self.assertFalse(self.Rental.search_count([('name', '=', 'Location rejetée')]))

    def test_zero_reste_valide(self):
        """C3 — zéro jour reste accepté, à la création comme à la modification."""
        rental = self.Rental.create({'name': 'Prêt à zéro jour', 'days': 0, 'daily_rate': 42, 'kind': 'loan'})
        self.assertEqual(rental.days, 0)
        self.assertEqual(rental.amount_total, 0)
        autre = self.Rental.create({'name': 'Retour à zéro', 'days': 7, 'daily_rate': 42})
        autre.write({'days': 0})
        self.env.flush_all()
        self.assertEqual(autre.days, 0)
        self.assertEqual(autre.amount_total, 0)

    def test_total_inchange(self):
        """C4 — le calcul du total n'est pas modifié par la contrainte."""
        rental = self.Rental.create({'name': 'Location facturée', 'days': 6, 'daily_rate': 12.5})
        self.assertEqual(rental.amount_total, 75)
        rental.write({'days': 8})
        self.assertEqual(rental.amount_total, 100)

    def test_contrainte_bien_sql(self):
        """C6 — la contrainte existe au niveau table, pas seulement en Python."""
        self.env.cr.execute(
            """
            SELECT pg_get_constraintdef(oid)
              FROM pg_constraint
             WHERE conrelid = 'lab_rental'::regclass
               AND contype = 'c'
            """
        )
        definitions = [row[0] for row in self.env.cr.fetchall()]
        self.assertTrue(
            any('days >= 0' in definition for definition in definitions),
            f'contrainte CHECK days >= 0 absente de la table : {definitions}',
        )

    def test_pret_soumis_a_la_meme_regle(self):
        """C7 — la contrainte ne distingue pas les types (D-31 ne le fait pas)."""
        self._reject(lambda: self.Rental.create({'name': 'Prêt négatif', 'days': -3, 'kind': 'loan'}))
