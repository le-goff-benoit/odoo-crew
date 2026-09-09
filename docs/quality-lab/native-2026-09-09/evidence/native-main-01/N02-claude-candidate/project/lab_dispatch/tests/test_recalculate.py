from unittest.mock import patch

from odoo.tests import tagged

from .common import LabDispatchCommon


@tagged('post_install', '-at_install')
class TestLabDispatchRecalculate(LabDispatchCommon):
    """Décision D-12 : recalcul des seuls brouillons, lignes annulées exclues."""

    def _write_spy(self):
        """Espionne lab.dispatch.write pour prouver l'absence totale d'écriture."""
        model_cls = type(self.env['lab.dispatch'])
        original_write = model_cls.write
        written_ids = []

        def spy(records, vals):
            written_ids.extend(records.ids)
            return original_write(records, vals)

        return patch.object(model_cls, 'write', spy), written_ids

    def test_draft_excludes_cancelled_lines(self):
        """CA1 : un brouillon ne somme que les lignes non annulées."""
        dispatch = self._build_dispatch('DRAFT', 'draft', 999.0, [
            (2.0, 10.0, False),
            (3.0, 30.0, True),
        ])

        dispatch.action_recalculate()

        self.assertEqual(dispatch.snapshot_total, 20.0)

    def test_done_is_never_written(self):
        """CA2 : un dossier validé garde son total et n'est pas écrit du tout."""
        dispatch = self._build_dispatch('DONE', 'done', 777.0, [
            (2.0, 10.0, False),
            (3.0, 30.0, True),
        ])
        spy, written_ids = self._write_spy()

        with spy:
            dispatch.action_recalculate()

        self.assertEqual(dispatch.snapshot_total, 777.0)
        self.assertNotIn(dispatch.id, written_ids, "un dossier validé ne doit pas être écrit, pas même à l'identique")

    def test_mixed_selection(self):
        """CA3 : une sélection mixte recalcule les brouillons et ignore les validés."""
        draft = self._build_dispatch('MIXED_DRAFT', 'draft', 999.0, [
            (2.0, 10.0, False),
            (3.0, 30.0, True),
        ])
        done = self._build_dispatch('MIXED_DONE', 'done', 777.0, [
            (2.0, 10.0, False),
            (3.0, 30.0, True),
        ])
        spy, written_ids = self._write_spy()

        with spy:
            result = (draft | done).action_recalculate()

        self.assertTrue(result)
        self.assertEqual(draft.snapshot_total, 20.0)
        self.assertEqual(done.snapshot_total, 777.0)
        self.assertNotIn(done.id, written_ids)

    def test_recalculate_is_idempotent(self):
        """CA4 : deux appels consécutifs donnent le même résultat."""
        draft = self._build_dispatch('IDEM_DRAFT', 'draft', 999.0, [
            (2.0, 10.0, False),
            (3.0, 30.0, True),
        ])
        done = self._build_dispatch('IDEM_DONE', 'done', 777.0, [
            (2.0, 10.0, False),
        ])
        records = draft | done

        records.action_recalculate()
        first_pass = (draft.snapshot_total, done.snapshot_total)
        records.action_recalculate()

        self.assertEqual((draft.snapshot_total, done.snapshot_total), first_pass)
        self.assertEqual(first_pass, (20.0, 777.0))

    def test_empty_and_fully_cancelled(self):
        """Cas limites : aucune ligne, ou uniquement des lignes annulées."""
        empty = self._build_dispatch('EMPTY', 'draft', 999.0, [])
        cancelled = self._build_dispatch('CANCELLED', 'draft', 999.0, [
            (3.0, 30.0, True),
        ])

        (empty | cancelled).action_recalculate()

        self.assertEqual(empty.snapshot_total, 0.0)
        self.assertEqual(cancelled.snapshot_total, 0.0)

    def test_empty_recordset_does_not_fail(self):
        """Une sélection vide ne lève rien."""
        self.assertTrue(self.Dispatch.browse().action_recalculate())
