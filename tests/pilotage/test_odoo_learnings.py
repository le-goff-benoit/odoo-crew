"""Les fiches restent une vue des acquis relus, périmables et remplaçables."""
import json
import os
from pathlib import Path
import sys
import tempfile
import subprocess
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import odoo_documents as documents
import odoo_knowledge as knowledge
import odoo_learnings as cards


class LearningCardsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        folder = self.root / 'changelog/first'
        folder.mkdir(parents=True)
        (folder / 'README.md').write_text('# Release synthétique')
        (self.root / 'observation.md').write_text('En 18.0, vérifier le module installé. Exception : une copie ancienne.')

    def publish(self, identifier='K1', **kwargs):
        ref = documents.reference(self.root, 'observation.md')
        row = {'schema': 1, 'id': identifier, 'kind': 'discovery', 'state': 'accepted',
               'statement': 'Vérifier le module installé', 'author': 'consultant',
               'scope': ['18.0', 'paie suisse'], 'exceptions': ['Une copie ancienne'],
               'reviewed_by': 'consultant (auto-relecture)', 'review': ref, 'sources': [ref],
               'effect': 'Vérifier la base avant de promettre une fonction', **kwargs}
        knowledge.publish(self.root, 'first', row)

    def test_proposal_stays_in_release_and_never_creates_a_card(self):
        self.publish(state='proposed')
        result = cards.export(self.root)
        self.assertIsNone(result['directory'])
        self.assertFalse((self.root / '.odoo-agents/learnings').exists())

    def test_current_card_preserves_scope_exception_and_idempotence(self):
        self.publish()
        result = cards.export(self.root)
        folder = self.root / result['directory']
        path = folder / 'first--K1.json'
        card = json.loads(path.read_text())
        self.assertEqual(card['status'], 'current')
        self.assertEqual(card['learning']['scope'], ['18.0', 'paie suisse'])
        self.assertEqual(card['learning']['exceptions'], ['Une copie ancienne'])
        before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in folder.iterdir()}
        self.assertEqual(cards.export(self.root), result)
        self.assertEqual(before, {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in folder.iterdir()})
        (self.root / 'observation.md').write_text('Observation modifiée')
        result = cards.export(self.root)
        self.assertEqual(result['current'], 0)
        self.assertTrue(result['warnings'])
        self.assertEqual(json.loads(path.read_text())['status'], 'stale')

    def test_replacement_keeps_history_without_resurrecting_old_learning(self):
        self.publish()
        cards.export(self.root)
        self.publish('K2', supersedes='K1', statement='Vérifier la révision du module')
        result = cards.export(self.root)
        self.assertEqual((result['current'], result['historical']), (1, 1))
        folder = self.root / result['directory']
        self.assertEqual(json.loads((folder / 'first--K1.json').read_text())['status'], 'superseded')
        self.assertEqual(json.loads((folder / 'first--K2.json').read_text())['status'], 'current')

    def test_personal_file_is_preserved_and_no_partial_export_is_written(self):
        self.publish()
        folder = self.root / '.odoo-agents/learnings'
        folder.mkdir()
        target = folder / 'index.json'
        target.write_text('{"note": "personnelle"}')
        with self.assertRaises(ValueError):
            cards.export(self.root)
        self.assertEqual(json.loads(target.read_text()), {'note': 'personnelle'})
        self.assertFalse((folder / 'first--K1.json').exists())

    def test_invalid_identifier_cannot_escape_directory(self):
        self.publish()
        registry = self.root / '.odoo-agents/LEARNINGS.json'
        data = json.loads(registry.read_text())
        data['items'][0]['id'] = '../../outside'
        registry.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            cards.export(self.root)
        self.assertFalse((self.root / 'outside.json').exists())

    def test_prepare_exports_and_next_release_reuses_only_fresh_learning(self):
        self.publish()
        (self.root / '.odoo-agents/config').write_text('series = 18.0\n')
        (self.root / '.odoo-agents/PROJECT.md').write_text('# Projet synthétique\n')
        script = Path(cards.__file__).with_name('odoo_work.py')
        result = subprocess.run([sys.executable, str(script), 'prepare', str(self.root),
                                 '--query', 'paie suisse'], capture_output=True, text=True,
                                env={**os.environ, 'ODOO_SERIES': '18.0'})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('learning_cards', result.stdout)
        self.assertTrue((self.root / '.odoo-agents/learnings/index.json').exists())
        folder = self.root / 'changelog/second'
        folder.mkdir()
        (folder / 'README.md').write_text('# Deuxième release')
        import odoo_context
        fresh = odoo_context.context(self.root, 'paie suisse', release='second')
        self.assertIn('Vérifier le module installé', fresh['text'])
        self.assertIn('Une copie ancienne', fresh['text'])
        (self.root / 'observation.md').write_text('La source a changé')
        cards.export(self.root)
        from odoo_pilotage import learnings
        self.assertFalse(any(row['current'] for row in learnings(self.root)))
