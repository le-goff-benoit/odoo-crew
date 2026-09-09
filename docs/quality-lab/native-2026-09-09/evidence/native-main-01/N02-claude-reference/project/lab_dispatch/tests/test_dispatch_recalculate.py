from odoo.tests import tagged
from odoo.tools import SQL

from .common import LabDispatchCommon


@tagged('post_install', '-at_install')
class TestDispatchRecalculate(LabDispatchCommon):
    """Contrat D-12 : seuls les brouillons sont recalculés, hors lignes annulées."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Une ligne active à 20,00 et une ligne annulée à 90,00 : le brut vaut 110,00.
        cls.draft = cls._new_dispatch('Brouillon', 'draft', 999.0, [(2, 10, False), (3, 30, True)])
        cls.done = cls._new_dispatch('Validé', 'done', 777.0, [(2, 10, False), (3, 30, True)])

    def _write_date(self, dispatch):
        """Relit ``write_date`` en base, hors cache, pour détecter la moindre écriture."""
        dispatch.env.flush_all()
        return dispatch.env.execute_query(
            SQL('SELECT write_date FROM lab_dispatch WHERE id = %s', dispatch.id)
        )[0][0]

    def test_draft_excludes_cancelled_lines(self):
        """C1 — un brouillon ignore ses lignes annulées."""
        self.draft.action_recalculate()
        self.assertEqual(self.draft.snapshot_total, 20.0)

    def test_done_total_is_frozen(self):
        """C2 — un dossier validé garde son total, même faux au regard de ses lignes."""
        self.done.action_recalculate()
        self.assertEqual(self.done.snapshot_total, 777.0)

    def test_done_is_never_written(self):
        """C3 — un dossier validé n'est pas réécrit : sa date d'écriture ne bouge pas.

        La date est d'abord repoussée dans le passé : dans une même transaction, une
        écriture réelle la ramènerait à l'horodatage de la transaction.
        """
        self.env.execute_query(SQL(
            "UPDATE lab_dispatch SET write_date = %s WHERE id = %s",
            '2000-01-01 00:00:00', self.done.id,
        ))
        self.env.invalidate_all()
        before = self._write_date(self.done)
        self.done.action_recalculate()
        self.assertEqual(self._write_date(self.done), before)

    def test_mixed_selection(self):
        """C4 — une sélection mixte recalcule les brouillons et ignore les validés sans erreur."""
        (self.draft | self.done).action_recalculate()
        self.assertEqual(self.draft.snapshot_total, 20.0)
        self.assertEqual(self.done.snapshot_total, 777.0)

    def test_draft_fully_cancelled(self):
        """C5 — un brouillon dont toutes les lignes sont annulées tombe à zéro."""
        dispatch = self._new_dispatch('Tout annulé', 'draft', 500.0, [(2, 10, True), (3, 30, True)])
        dispatch.action_recalculate()
        self.assertEqual(dispatch.snapshot_total, 0.0)

    def test_recalculate_is_idempotent(self):
        """C6 — deux appels successifs donnent le même total et laissent les validés figés."""
        self.draft.action_recalculate()
        self.draft.action_recalculate()
        self.assertEqual(self.draft.snapshot_total, 20.0)
        self.assertEqual(self.done.snapshot_total, 777.0)

    def test_empty_selection(self):
        """Cas limite — appeler l'action sur un recordset vide ne lève rien."""
        self.assertTrue(self.Dispatch.browse().action_recalculate())
