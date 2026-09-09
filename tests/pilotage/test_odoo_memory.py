import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('memory', ROOT / 'scripts/odoo_memory.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'message.md').write_text('Le client confirme la règle actuelle.')
        self.source = {'path': 'message.md', 'sha256': hashlib.sha256((self.root / 'message.md').read_bytes()).hexdigest()}
        self.data = {'schema': 1, 'decisions': [
            {'id': 'D1', 'status': 'superseded', 'superseded_by': 'D2', 'statement': 'Ancienne règle INAPPLICABLE',
             'confirmed_by': 'Client', 'sources': [self.source], 'implementation': {'status': 'not_started'}},
            {'id': 'D2', 'status': 'confirmed', 'statement': 'Règle actuelle avec exception', 'confirmed_by': 'Client',
             'sources': [self.source], 'implementation': {'status': 'not_started'}}],
             'questions': [{'id': 'Q1', 'question': 'Quel point de blocage ?', 'status': 'open', 'source': self.source}]}

    def test_current_rule_not_old_statement_and_open_question_persists(self):
        text = m.render(self.data, self.root)
        self.assertIn('Règle actuelle avec exception', text)
        self.assertNotIn('INAPPLICABLE', text)
        self.assertIn('D1 → D2', text)
        self.assertIn('QUESTION OUVERTE', text)
        self.assertIn('réalisation=not_started', text)

    def test_stale_source_blocks_claim_of_valid_memory(self):
        (self.root / 'message.md').write_text('Le message a changé.')
        with self.assertRaises(m.MemoryError): m.render(self.data, self.root)

    def test_proposal_cannot_replace_confirmed_or_resolve_question(self):
        self.data['decisions'][1]['status'] = 'proposed'
        with self.assertRaises(m.MemoryError): m.validate(self.data, self.root)
        self.data['decisions'] = self.data['decisions'][1:]
        self.data['questions'][0].update(status='resolved', decision_id='D2')
        with self.assertRaises(m.MemoryError): m.validate(self.data, self.root)

    def test_realization_requires_evidence_and_deployment_target(self):
        self.data['decisions'][1]['implementation'] = {'status': 'deployed'}
        with self.assertRaises(m.MemoryError): m.validate(self.data, self.root)
        self.data['decisions'][1]['implementation']['evidence'] = self.source
        with self.assertRaises(m.MemoryError): m.validate(self.data, self.root)
        self.data['decisions'][1]['implementation']['instance'] = 'synthetic-local'
        m.validate(self.data, self.root)

    def test_cycle_rejected(self):
        self.data['decisions'][1].update(status='superseded', superseded_by='D1')
        with self.assertRaises(m.MemoryError): m.validate(self.data, self.root)

    def test_unknown_implementation_does_not_claim_not_started(self):
        self.data['decisions'][1]['implementation'] = {'status': 'unknown'}
        text = m.render(self.data, self.root)
        self.assertIn('réalisation=unknown', text)
        self.assertNotIn('réalisation=not_started', text)
