import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import odoo_feedback as feedback


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / '.odoo-agents').mkdir()
        self.journal = self.root / '.odoo-agents/JOURNAL.md'
        self.journal.write_text('## 2026-09-30 — Exemple\n- Appris : garder les exceptions.\n')
        self.release = self.root / 'changelog/first'
        self.release.mkdir(parents=True)
        (self.release / 'README.md').write_text('# Release')

    def test_collection_is_idempotent_and_history_survives_source_append(self):
        first = feedback.collect(self.root, 'first')
        self.assertEqual(first['pending'], 1)
        self.assertEqual(first, feedback.collect(self.root, 'first'))
        self.journal.write_text(self.journal.read_text() + '\n## 2026-10-01 — Suite\n- Appris : contrôler le résultat.\n')
        current = feedback.collect(self.root, 'first')
        self.assertEqual(current['pending'], 2)
        self.assertIn(first['events'][0], current['events'])
        self.assertFalse((self.root / '.odoo-agents/DECISIONS.json').exists())

    def test_triage_does_not_mutate_observation_and_survives_collection(self):
        first = feedback.collect(self.root)
        row = first['events'][0]
        path = self.root / '.odoo-agents/feedback/events' / (row['id'] + '.json')
        before = path.read_bytes()
        feedback.triage(self.root, row['id'], 'reviewed', 'responsable', 'À tester sur un cas inédit')
        self.assertEqual(feedback.collect(self.root)['pending'], 0)
        self.assertEqual(before, path.read_bytes())
        path.write_text('{}')
        self.assertTrue(feedback.snapshot(self.root)['warnings'])
        with self.assertRaises(ValueError): feedback.collect(self.root)

    def test_reopen_reason_and_closure_are_collected_without_changing_release(self):
        (self.release / 'plan.json').write_text(json.dumps({'history': [
            {'action': 'reopen', 'task_id': 'T1', 'reason': 'Le montant attendu diffère du résultat'}]}))
        closure = self.release / 'closure.json'; closure.write_text('{"proof": "synthetic"}')
        before = closure.read_bytes()
        result = feedback.collect(self.root, 'first')
        self.assertEqual({r['kind'] for r in result['events']}, {'lesson', 'reopen', 'closure'})
        self.assertEqual(before, closure.read_bytes())

    def test_failed_automatic_collection_remains_visible_and_retry_clears_warning(self):
        (self.release / 'plan.json').write_text('broken')
        self.assertTrue(feedback.automatic(self.root, 'first')['pending_collection'])
        self.assertTrue(feedback.snapshot(self.root)['warnings'])
        (self.release / 'plan.json').write_text('{}')
        feedback.collect(self.root, 'first')
        self.assertFalse(feedback.snapshot(self.root)['warnings'])

    def test_explicit_correction_requires_source_and_remains_candidate(self):
        row = feedback.record(self.root, '.odoo-agents/JOURNAL.md', 'garder les exceptions.', 'human_correction', 'first')
        same = feedback.record(self.root, '.odoo-agents/JOURNAL.md', 'garder les exceptions.', 'human_correction', 'first')
        self.assertEqual(row, same)
        self.assertEqual(feedback.snapshot(self.root)['pending'], 1)
        with self.assertRaises(ValueError):
            feedback.record(self.root, '.odoo-agents/JOURNAL.md', 'inventé', 'human_correction')

    def test_delta_markers_never_create_duplicate_historical_lessons(self):
        from odoo_reception import append_block
        self.journal.write_text('# Journal\n')
        for index in (1, 2):
            content = f'## 2026-10-0{index} — Tâche\n- Appris : leçon {index}.\n'.encode()
            block, _ = append_block({'target': '.odoo-agents/JOURNAL.md', 'draft': {'sha256': str(index) * 64}}, content)
            with self.journal.open('ab') as stream: stream.write(block)
            result = feedback.collect(self.root)
            self.assertEqual(result['pending'], index)
            self.assertTrue(all('crew-memory' not in e['text'] for e in result['events']))
