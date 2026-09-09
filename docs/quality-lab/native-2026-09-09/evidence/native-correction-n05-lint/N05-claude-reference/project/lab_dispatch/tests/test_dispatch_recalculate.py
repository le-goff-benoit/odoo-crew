from odoo.fields import Command
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestDispatchRecalculate(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Dispatch = cls.env['lab.dispatch']

    def _dispatch(self, name, state, snapshot_total, lines):
        return self.Dispatch.create({
            'name': name,
            'state': state,
            'snapshot_total': snapshot_total,
            'line_ids': [
                Command.create({'quantity': quantity, 'price': price, 'cancelled': cancelled})
                for quantity, price, cancelled in lines
            ],
        })

    def test_draft_excludes_cancelled_lines(self):
        """Le total d'un brouillon n'additionne que les lignes non annulées."""
        dispatch = self._dispatch('DRAFT', 'draft', 999.0, [(2.0, 10.0, False), (3.0, 30.0, True)])

        dispatch.action_recalculate()

        self.assertEqual(dispatch.snapshot_total, 20.0)

    def test_done_is_never_recalculated(self):
        """Un dossier validé garde son total au centime près, sans écriture."""
        dispatch = self._dispatch('DONE', 'done', 777.0, [(2.0, 10.0, False), (3.0, 30.0, True)])
        write_date = dispatch.write_date

        dispatch.action_recalculate()
        dispatch.invalidate_recordset()

        self.assertEqual(dispatch.snapshot_total, 777.0)
        self.assertEqual(dispatch.write_date, write_date)

    def test_mixed_selection(self):
        """Une sélection mixte recalcule les brouillons et ignore les validés, sans erreur."""
        draft = self._dispatch('DRAFT', 'draft', 999.0, [(2.0, 10.0, False), (3.0, 30.0, True)])
        done = self._dispatch('DONE', 'done', 777.0, [(2.0, 10.0, False), (3.0, 30.0, True)])

        (draft | done).action_recalculate()

        self.assertEqual(draft.snapshot_total, 20.0)
        self.assertEqual(done.snapshot_total, 777.0)
        self.assertEqual(draft.state, 'draft')
        self.assertEqual(done.state, 'done')

    def test_recalculate_is_idempotent(self):
        """Deux recalculs successifs donnent le même total, sans dérive de centimes."""
        dispatch = self._dispatch('FRACTION', 'draft', 20.004, [(2.0, 10.0, False)])

        dispatch.action_recalculate()
        first = dispatch.snapshot_total
        dispatch.action_recalculate()

        self.assertEqual(first, 20.0)
        self.assertEqual(dispatch.snapshot_total, 20.0)

    def test_recalculate_without_line_resets_total(self):
        """Un brouillon dont toutes les lignes sont annulées retombe à zéro."""
        dispatch = self._dispatch('ALL_CANCELLED', 'draft', 999.0, [(3.0, 30.0, True)])

        dispatch.action_recalculate()

        self.assertEqual(dispatch.snapshot_total, 0.0)
