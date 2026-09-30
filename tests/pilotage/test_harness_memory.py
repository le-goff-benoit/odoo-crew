"""Regression cases from the audit, with synthetic projects only."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import odoo_briefing as briefing
import odoo_context as context
import odoo_documents as documents
import odoo_knowledge as knowledge


class MemoryAuditTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / '.odoo-agents').mkdir()
        for release in ('first', 'second'):
            folder = self.root / 'changelog' / release
            folder.mkdir(parents=True)
            (folder / 'README.md').write_text('# Synthetic release\n')
        (self.root / 'decision.md').write_text('Le responsable confirme la règle A, sauf pour les avoirs.')

    def row(self, identifier='K1', **kw):
        return {'schema': 1, 'id': identifier, 'kind': 'decision', 'state': 'accepted',
                'statement': 'Règle A', 'author': 'agent', 'scope': ['account.move'],
                'exceptions': ['Sauf les avoirs'], 'reviewed_by': 'responsable',
                'review': documents.reference(self.root, 'decision.md'),
                'sources': [documents.reference(self.root, 'decision.md')], **kw}

    def test_plain_bold_and_bulleted_lessons_keep_exceptions_not_following_fields(self):
        for label in ('**Appris** :', '- Appris :', '- **Appris** :', '**Appris :**'):
            with self.subTest(label=label):
                result = briefing.learned_lines(['## 2026-09-30 — Exemple\n' + label
                    + ' Règle A\n  sauf les avoirs.\n- Reste : ne pas extraire.'])
                self.assertEqual(len(result), 1)
                self.assertIn('sauf les avoirs', result[0])
                self.assertNotIn('ne pas extraire', result[0])

    def test_unstructured_current_decisions_cannot_disappear_behind_budget(self):
        (self.root / '.odoo-agents/PROJECT.md').write_text(
            '# Projet\n## Compréhension métier\n' + 'Contexte. ' * 150
            + '\n## Décisions actées\n' + 'Règle approuvée. ' * 180
            + '\n### Exception\nSauf les avoirs.\n')
        record = context.context(self.root, 'facture', budget=1200)
        self.assertIn('Sauf les avoirs', record['text'])
        self.assertEqual(record['budget_status'], 'insufficient')

    def test_accepted_decision_is_shared_across_releases_without_invented_delivery(self):
        knowledge.publish(self.root, 'first', self.row())
        data = json.loads((self.root / '.odoo-agents/DECISIONS.json').read_text())
        self.assertEqual(data['decisions'][0]['implementation']['status'], 'unknown')
        self.assertIn('Sauf les avoirs', knowledge.brief(self.root, 'second')['text'])
        knowledge.publish(self.root, 'first', self.row())
        self.assertEqual(len(json.loads((self.root / '.odoo-agents/DECISIONS.json').read_text())['decisions']), 1)

    def test_proposal_never_becomes_confirmed(self):
        knowledge.publish(self.root, 'first', self.row(state='proposed'))
        self.assertFalse((self.root / '.odoo-agents/DECISIONS.json').exists())

    def test_acceptance_can_explicitly_replace_a_proposal(self):
        knowledge.publish(self.root, 'first', self.row(state='proposed'))
        knowledge.publish(self.root, 'first', self.row('K2', supersedes='K1'))
        data = json.loads((self.root / '.odoo-agents/DECISIONS.json').read_text())
        self.assertEqual([r['id'] for r in data['decisions']], ['first--K2'])

    def test_cross_release_replacement_and_competing_replacement(self):
        knowledge.publish(self.root, 'first', self.row())
        knowledge.publish(self.root, 'second', self.row('K2', statement='Règle B', supersedes_project='first--K1'))
        text = knowledge.brief(self.root, 'second')['text']
        self.assertNotIn(': Règle A', text)
        self.assertIn('Règle B', text)
        with self.assertRaises(ValueError):
            knowledge.publish(self.root, 'second', self.row('K3', supersedes_project='first--K1'))
        self.assertFalse((self.root / 'changelog/second/knowledge/K3.json').exists())

    def test_stale_current_decision_refuses_promotion(self):
        row = self.row()
        (self.root / 'decision.md').write_text('Texte changé')
        with self.assertRaises(ValueError):
            knowledge.publish(self.root, 'first', row)
        self.assertFalse((self.root / '.odoo-agents/DECISIONS.json').exists())

    def test_holdout_exception_label_is_not_a_new_journal_field(self):
        rows = briefing.learned_lines(['## 2026-10-01 — Inédit\n- **Appris :** Règle globale.\n  Exception : les avoirs.\n- QA : contrôle exécuté.'])
        self.assertEqual(len(rows), 1)
        self.assertIn('Exception : les avoirs', rows[0])
        self.assertNotIn('contrôle exécuté', rows[0])

    def test_replaced_decision_is_historical_even_when_reading_its_original_release(self):
        knowledge.publish(self.root, 'first', self.row())
        knowledge.publish(self.root, 'second', self.row('K2', statement='Règle B', supersedes_project='first--K1'))
        old = knowledge.contributions(self.root, 'first')[0]
        self.assertFalse(old['current'])
        (self.root / 'decision.md').write_text('Source courante changée')
        data = knowledge.snapshot(self.root, 'first')
        self.assertTrue(data['warnings'])
        self.assertFalse(data['contributions'][0]['current'])
