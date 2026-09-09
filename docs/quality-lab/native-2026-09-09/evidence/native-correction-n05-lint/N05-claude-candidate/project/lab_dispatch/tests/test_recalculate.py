from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

FIGE = "2020-01-01 00:00:00"


@tagged('post_install', '-at_install')
class TestRecalculate(TransactionCase):
    """D-12 : action_recalculate ne recalcule que les brouillons, hors lignes annulées."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatch = cls.env['lab.dispatch']

    def _dossier(self, name, state, snapshot):
        return self.dispatch.create({
            'name': name,
            'state': state,
            'snapshot_total': snapshot,
            'line_ids': [
                Command.create({'quantity': 2.0, 'price': 10.0, 'cancelled': False}),
                Command.create({'quantity': 3.0, 'price': 30.0, 'cancelled': True}),
            ],
        })

    def _figer_write_date(self, records):
        """Force une write_date connue pour détecter toute écriture, même à valeur égale."""
        records.flush_recordset()
        self.env.cr.execute(
            "UPDATE lab_dispatch SET write_date = %s WHERE id IN %s",
            (FIGE, tuple(records.ids)),
        )
        records.invalidate_recordset()

    def _write_date_sql(self, record):
        self.env.cr.execute("SELECT write_date FROM lab_dispatch WHERE id = %s", (record.id,))
        return self.env.cr.fetchone()[0]

    def test_brouillon_exclut_les_lignes_annulees(self):
        """C1 — le total d'un brouillon ignore les lignes cancelled=True."""
        brouillon = self._dossier('C1', 'draft', 999.0)
        brouillon.action_recalculate()
        self.assertEqual(brouillon.snapshot_total, 20.0)

    def test_valide_reste_strictement_inchange(self):
        """C2 — un dossier validé n'est ni recalculé, ni même réécrit."""
        valide = self._dossier('C2', 'done', 777.0)
        self._figer_write_date(valide)

        valide.action_recalculate()
        valide.flush_recordset()

        self.assertEqual(valide.snapshot_total, 777.0)
        self.assertEqual(
            str(self._write_date_sql(valide)), FIGE,
            "le dossier validé a été écrit alors qu'il doit rester figé",
        )

    def test_selection_mixte(self):
        """C3 — brouillons recalculés, validés ignorés, aucune erreur."""
        brouillon = self._dossier('C3-draft', 'draft', 999.0)
        valide = self._dossier('C3-done', 'done', 777.0)
        self._figer_write_date(valide)

        (brouillon | valide).action_recalculate()
        (brouillon | valide).flush_recordset()

        self.assertEqual(brouillon.snapshot_total, 20.0)
        self.assertEqual(valide.snapshot_total, 777.0)
        self.assertEqual(str(self._write_date_sql(valide)), FIGE)

    def test_brouillon_sans_ligne(self):
        """Hypothèse retenue : une somme vide vaut zéro."""
        brouillon = self.dispatch.create({'name': 'C1-vide', 'state': 'draft', 'snapshot_total': 999.0})
        brouillon.action_recalculate()
        self.assertEqual(brouillon.snapshot_total, 0.0)


@tagged('post_install', '-at_install')
class TestReprise(TransactionCase):
    """D-12 : la reprise ne touche que les brouillons et se rejoue sans effet."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatch = cls.env['lab.dispatch']

    def _dossier(self, name, state, snapshot, lignes):
        return self.dispatch.create({
            'name': name,
            'state': state,
            'snapshot_total': snapshot,
            'line_ids': [Command.create(ligne) for ligne in lignes],
        })

    def test_reprise_corrige_les_brouillons(self):
        """C6 — la reprise redresse les brouillons faux, y compris une dérive fine."""
        faux = self._dossier('R-faux', 'draft', 999.0, [
            {'quantity': 2.0, 'price': 10.0, 'cancelled': False},
            {'quantity': 3.0, 'price': 30.0, 'cancelled': True},
        ])
        derive = self._dossier('R-derive', 'draft', 20.004, [
            {'quantity': 2.0, 'price': 10.0, 'cancelled': False},
        ])

        repris = self.dispatch._reprise_snapshot_brouillons()

        self.assertEqual(faux.snapshot_total, 20.0)
        self.assertEqual(derive.snapshot_total, 20.0)
        self.assertLessEqual({faux.id, derive.id}, set(repris.ids))

    def test_reprise_ignore_les_valides(self):
        """C6 — un dossier validé faux reste faux : il est figé."""
        valide = self._dossier('R-valide', 'done', 777.0, [
            {'quantity': 2.0, 'price': 10.0, 'cancelled': False},
        ])

        repris = self.dispatch._reprise_snapshot_brouillons()

        self.assertEqual(valide.snapshot_total, 777.0)
        self.assertNotIn(valide.id, repris.ids)

    def test_reprise_idempotente(self):
        """C4/C5 — la seconde exécution ne modifie aucun enregistrement."""
        self._dossier('R-idem', 'draft', 999.0, [
            {'quantity': 2.0, 'price': 10.0, 'cancelled': False},
            {'quantity': 3.0, 'price': 30.0, 'cancelled': True},
        ])

        premier = self.dispatch._reprise_snapshot_brouillons()
        self.assertTrue(premier, "la première passe doit corriger au moins un dossier")

        second = self.dispatch._reprise_snapshot_brouillons()
        self.assertFalse(second, "la reprise rejouée a modifié des dossiers : elle n'est pas idempotente")
