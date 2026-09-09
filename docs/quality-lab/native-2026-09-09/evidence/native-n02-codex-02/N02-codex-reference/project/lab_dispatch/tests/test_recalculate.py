from unittest.mock import patch

from odoo.fields import Command
from odoo.tests import tagged

from .common import LabDispatchCommon


@tagged('post_install', '-at_install')
class TestRecalculate(LabDispatchCommon):
    def test_draft_excludes_cancelled(self):
        """Une ligne annulée ne contribue jamais au total du brouillon."""
        self.assertTrue(self.draft.action_recalculate())
        self.assertPersistedTotal(self.draft, 20)

    def test_validated_snapshot_is_frozen(self):
        """Le montant historique reste figé même s'il diffère des lignes."""
        self.assertTrue(self.done.action_recalculate())
        self.assertPersistedTotal(self.done, 777)
        self.assertEqual(self.done.state, 'done')

    def test_validated_never_written(self):
        """Même un snapshot égal au calcul ne doit pas être réécrit."""
        self.done.snapshot_total = 20
        self.done.flush_recordset()
        with patch.object(type(self.done), 'write') as write:
            self.assertTrue(self.done.action_recalculate())
        write.assert_not_called()

    def test_mixed_selection(self):
        """Tous les brouillons sont corrigés sans toucher aux validés."""
        other_draft = self.draft.copy({
            'name': 'Other draft',
            'line_ids': [Command.create({'quantity': 4, 'price': 5})],
        })
        original_write = type(self.draft).write

        def guarded_write(records, values):
            self.assertNotIn(self.done, records)
            return original_write(records, values)

        with patch.object(type(self.draft), 'write', guarded_write):
            self.assertTrue((self.draft | self.done | other_draft).action_recalculate())
        self.assertPersistedTotal(self.draft, 20)
        self.assertPersistedTotal(other_draft, 20)
        self.assertPersistedTotal(self.done, 777)

    def test_empty_and_all_cancelled(self):
        """Sans ligne admissible, le total vaut zéro ; une sélection vide passe."""
        empty = self.env['lab.dispatch'].create({'name': 'Empty', 'snapshot_total': 99})
        self.draft.line_ids.cancelled = True
        self.assertTrue((empty | self.draft).action_recalculate())
        self.assertPersistedTotal(empty, 0)
        self.assertPersistedTotal(self.draft, 0)
        self.assertTrue(self.env['lab.dispatch'].action_recalculate())

    def test_signed_and_zero_amounts(self):
        """Les lignes actives sont additionnées sans changer leur signe."""
        self.draft.line_ids = [
            Command.clear(),
            Command.create({'quantity': -2, 'price': 10}),
            Command.create({'quantity': 3, 'price': -4}),
            Command.create({'quantity': 0, 'price': 10}),
            Command.create({'quantity': 4, 'price': 0}),
        ]
        self.draft.action_recalculate()
        self.assertPersistedTotal(self.draft, -32)

    def test_repeated_recalculation_is_noop(self):
        """Rejouer un recalcul correct ne doit produire aucune écriture."""
        self.draft.action_recalculate()
        self.assertPersistedTotal(self.draft, 20)
        with patch.object(type(self.draft), 'write') as write:
            self.assertTrue(self.draft.action_recalculate())
        write.assert_not_called()
        self.assertPersistedTotal(self.draft, 20)
