from odoo.tests import tagged

from .common import LabDispatchCommon


@tagged('post_install', '-at_install')
class TestLabDispatchRecalculate(LabDispatchCommon):

    def test_cancelled_lines_are_excluded(self):
        """CA1 — une ligne annulée ne compte pas dans le total du brouillon."""
        dispatch = self._new_dispatch(
            'CA1', 'draft', 999.0, [(2.0, 10.0, False), (3.0, 30.0, True)],
        )
        dispatch.action_recalculate()
        self.assertEqual(dispatch.snapshot_total, 20.0)

    def test_done_dispatch_is_frozen(self):
        """CA2 — un dossier validé n'est ni recalculé ni réécrit."""
        dispatch = self._new_dispatch(
            'CA2', 'done', 777.0, [(2.0, 10.0, False), (3.0, 30.0, True)],
        )
        dispatch.flush_recordset()
        write_date = dispatch.write_date
        dispatch.action_recalculate()
        dispatch.invalidate_recordset()
        self.assertEqual(dispatch.snapshot_total, 777.0)
        self.assertEqual(dispatch.write_date, write_date, "aucune écriture ne doit toucher un dossier validé")

    def test_mixed_selection(self):
        """CA3 — une sélection mixte recalcule les brouillons et ignore les validés."""
        draft = self._new_dispatch('CA3-draft', 'draft', 999.0, [(2.0, 10.0, False), (3.0, 30.0, True)])
        done = self._new_dispatch('CA3-done', 'done', 777.0, [(2.0, 10.0, False)])
        (draft | done).action_recalculate()
        self.assertEqual(draft.snapshot_total, 20.0)
        self.assertEqual(done.snapshot_total, 777.0)
        self.assertEqual(done.state, 'done')

    def test_draft_without_line(self):
        """CA4 — un brouillon sans ligne retombe à zéro."""
        dispatch = self._new_dispatch('CA4', 'draft', 999.0, [])
        dispatch.action_recalculate()
        self.assertEqual(dispatch.snapshot_total, 0.0)

    def test_recalculate_is_idempotent(self):
        """CA5 — rejouer le recalcul ne fait pas dériver les valeurs."""
        draft = self._new_dispatch('CA5-draft', 'draft', 999.0, [(2.0, 10.0, False), (3.0, 30.0, True)])
        done = self._new_dispatch('CA5-done', 'done', 777.0, [(2.0, 10.0, False)])
        (draft | done).action_recalculate()
        first_pass = (draft.snapshot_total, done.snapshot_total)
        (draft | done).action_recalculate()
        self.assertEqual((draft.snapshot_total, done.snapshot_total), first_pass)
        self.assertEqual(first_pass, (20.0, 777.0))
