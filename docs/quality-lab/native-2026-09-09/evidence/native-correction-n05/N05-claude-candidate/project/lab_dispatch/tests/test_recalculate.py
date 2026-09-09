from odoo.tests import tagged

from .common import LabDispatchCommon


@tagged('post_install', '-at_install')
class TestLabDispatchRecalculate(LabDispatchCommon):
    """Règle D-12 (decisions/2026-09-08.md) : brouillons recalculés hors lignes annulées, validés figés."""

    def test_draft_excludes_cancelled_lines(self):
        """CA1 — le total d'un brouillon ignore les lignes annulées."""
        dispatch = self._make_dispatch(
            'CA1', snapshot=999.0, lines=[(2.0, 10.0, False), (3.0, 30.0, True)],
        )

        dispatch.action_recalculate()

        self.assertEqual(dispatch.snapshot_total, 20.0)

    def test_done_is_never_written(self):
        """CA2 — un dossier validé garde son total et n'est pas écrit du tout."""
        dispatch = self._make_dispatch(
            'CA2', state='done', snapshot=777.0, lines=[(2.0, 10.0, False), (3.0, 30.0, True)],
        )

        written = self._written_ids(dispatch, dispatch.action_recalculate)

        self.assertEqual(dispatch.snapshot_total, 777.0)
        self.assertNotIn(dispatch.id, written, "un dossier validé ne doit recevoir aucun write")

    def test_mixed_selection(self):
        """CA3 — une sélection mixte recalcule les brouillons, ignore les validés, sans erreur."""
        draft = self._make_dispatch(
            'CA3-brouillon', snapshot=999.0, lines=[(2.0, 10.0, False), (3.0, 30.0, True)],
        )
        done = self._make_dispatch(
            'CA3-valide', state='done', snapshot=777.0, lines=[(2.0, 10.0, False)],
        )
        selection = draft | done

        written = self._written_ids(selection, selection.action_recalculate)

        self.assertEqual(draft.snapshot_total, 20.0)
        self.assertEqual(done.snapshot_total, 777.0)
        self.assertEqual(done.state, 'done')
        self.assertNotIn(done.id, written)

    def test_draft_fully_cancelled_is_zero(self):
        """CA4 — un brouillon dont toutes les lignes sont annulées tombe à zéro."""
        dispatch = self._make_dispatch('CA4', snapshot=999.0, lines=[(3.0, 30.0, True)])

        dispatch.action_recalculate()

        self.assertEqual(dispatch.snapshot_total, 0.0)


@tagged('post_install', '-at_install')
class TestLabDispatchRepair(LabDispatchCommon):
    """Reprise des données existantes : brouillons seulement, et idempotente."""

    def test_repair_fixes_drafts_only(self):
        """CA5 — la reprise corrige les brouillons faux, y compris un écart infime."""
        gros_ecart = self._make_dispatch(
            'REPRISE-999', snapshot=999.0, lines=[(2.0, 10.0, False), (3.0, 30.0, True)],
        )
        ecart_infime = self._make_dispatch(
            'REPRISE-FRACTION', snapshot=20.004, lines=[(2.0, 10.0, False)],
        )
        deja_juste = self._make_dispatch(
            'REPRISE-JUSTE', snapshot=20.0, lines=[(2.0, 10.0, False)],
        )

        repris = self.Dispatch._repair_draft_snapshots()

        self.assertEqual(gros_ecart.snapshot_total, 20.0)
        self.assertEqual(ecart_infime.snapshot_total, 20.0)
        self.assertIn(gros_ecart, repris)
        self.assertIn(ecart_infime, repris, "un écart de 0,004 reste un écart : pas de tolérance")
        self.assertNotIn(deja_juste, repris, "un dossier déjà juste n'est pas réécrit")

    def test_repair_never_touches_done(self):
        """CA7 — la reprise n'écrit jamais un dossier validé, même au total faux."""
        done = self._make_dispatch(
            'REPRISE-VALIDE', state='done', snapshot=777.0,
            lines=[(2.0, 10.0, False), (3.0, 30.0, True)],
        )

        written = self._written_ids(self.Dispatch, self.Dispatch._repair_draft_snapshots)

        self.assertEqual(done.snapshot_total, 777.0)
        self.assertNotIn(done.id, written)

    def test_repair_is_idempotent(self):
        """CA6 — rejouer la reprise ne reprend rien et n'écrit rien."""
        self._make_dispatch(
            'REPRISE-IDEM-999', snapshot=999.0, lines=[(2.0, 10.0, False), (3.0, 30.0, True)],
        )
        self._make_dispatch('REPRISE-IDEM-FRACTION', snapshot=20.004, lines=[(2.0, 10.0, False)])

        premier_passage = self.Dispatch._repair_draft_snapshots()
        self.assertEqual(len(premier_passage), 2)

        second_passage = self.Dispatch.browse()

        def rejouer():
            nonlocal second_passage
            second_passage = self.Dispatch._repair_draft_snapshots()

        written = self._written_ids(self.Dispatch, rejouer)

        self.assertFalse(second_passage, "le second passage ne doit reprendre aucun dossier")
        self.assertFalse(written, "le second passage ne doit produire aucun write")
