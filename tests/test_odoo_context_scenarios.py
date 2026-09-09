import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import odoo_context as context
import odoo_scenarios as scenarios
from odoo_bench_native import inside, copy_project, native_command


class ContextScenarioTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); (self.root / '.odoo-agents').mkdir()
        (self.root / 'decisions').mkdir(); (self.root / 'module').mkdir()
        self.source = self.root / 'decisions/D1.md'; self.source.write_text('La borne est inclusive, les prêts sont exclus.')
        self.rule = {'path': 'decisions/D1.md', 'sha256': hashlib.sha256(self.source.read_bytes()).hexdigest()}
        row = {'id': 'S1', 'rule': 'La borne est inclusive', 'source': self.rule, 'actor': 'gestionnaire société A',
               'setup': 'copie synthétique', 'expected': 'montant convenu', 'forbidden': 'modifier un validé',
               'triggers': ['module/*'], 'scopes': ['module'], 'command': [sys.executable, '-c', 'print("OK")'], 'group': 'server'}
        self.catalog = {'schema': 1, 'scenarios': [row]}
        (self.root / 'module/main.py').write_text('x=1')

    def test_context_omits_whole_long_block_and_tracks_freshness(self):
        (self.root / '.odoo-agents/PROJECT.md').write_text('x' * 1500 + ' EXCEPTION : prêts exclus')
        result = context.context(self.root, 'prêts', 1000)
        self.assertNotIn('x' * 200, result['text'])
        self.assertIn('.odoo-agents/PROJECT.md', result['text'])
        self.assertTrue(any(not r['included'] for r in result['sources']))
        context.verify_context(result, self.root)
        self.source.write_text('Nouvelle règle')
        with self.assertRaises(ValueError): context.verify_context(result, self.root)

    def test_new_decision_invalidates_context_even_if_old_sources_unchanged(self):
        record = context.context(self.root)
        (self.root / 'decisions/D2.md').write_text('Remplace D1')
        with self.assertRaisesRegex(ValueError, 'catalogue'):
            context.verify_context(record, self.root)

    def test_superseded_rule_never_rendered_as_current(self):
        data = {'schema': 1, 'decisions': [
            {'id':'D0', 'status':'superseded', 'statement':'ANCIENNE RÈGLE', 'sources':[self.rule], 'confirmed_by':'Alice', 'superseded_by':'D1', 'implementation':{'status':'unknown'}},
            {'id':'D1', 'status':'confirmed', 'statement':'NOUVELLE RÈGLE', 'sources':[self.rule], 'confirmed_by':'Alice', 'implementation':{'status':'not_started'}}],
            'questions':[{'id':'Q3', 'question':'Une question encore ouverte', 'status':'open', 'source':self.rule}]}
        (self.root / '.odoo-agents/DECISIONS.json').write_text(json.dumps(data))
        rendered = context.context(self.root)['text']
        self.assertIn('NOUVELLE RÈGLE', rendered); self.assertNotIn('ANCIENNE RÈGLE', rendered)
        self.assertIn('QUESTION OUVERTE', rendered)

    def test_unknown_change_expands_selection_and_stale_source_blocks(self):
        second = dict(self.catalog['scenarios'][0], id='S2', triggers=['other/*'], group='browser')
        self.catalog['scenarios'].append(second)
        exact = scenarios.select(self.catalog, self.root, ['module/main.py'])
        self.assertEqual(exact['selected'], ['S1'])
        unknown = scenarios.select(self.catalog, self.root, ['shared/utils.py'])
        self.assertEqual(unknown['selected'], ['S1', 'S2'])
        self.assertEqual(scenarios.select(self.catalog, self.root, [], group='server')['selected'], ['S1'])
        self.source.write_text('règle différente')
        with self.assertRaises(ValueError): scenarios.select(self.catalog, self.root, [])

    def test_scenario_execution_proof_includes_business_source(self):
        result = scenarios.run(self.catalog, self.root, ['S1'], self.root / 'proofs')
        proof = json.loads(Path(result[0]['proof']).read_text())
        self.assertEqual(result[0]['result'], 'passed')
        self.assertIn('decisions/D1.md', proof['sources'])
        with self.assertRaises(ValueError): scenarios.run(self.catalog, self.root, ['S1'], self.root / 'proofs')

    def test_bridge_rejects_outside_paths_and_symbolic_links(self):
        with self.assertRaises(ValueError): inside('/etc/passwd', self.root)
        (self.root / 'link').symlink_to('/etc/passwd')
        with self.assertRaises(ValueError): inside('link', self.root)
        with self.assertRaises(ValueError): copy_project(self.root, self.root / 'copied')

    def test_snapshot_excludes_installed_virtualenv_but_keeps_code(self):
        env = self.root / '.odoo-agents/tooling-venv'; env.mkdir()
        (env / 'pyvenv.cfg').write_text('home=/usr/bin')
        (env / 'lib64').symlink_to('/usr/lib')
        with tempfile.TemporaryDirectory() as dest:
            target = Path(dest) / 'snapshot'; copy_project(self.root, target)
            self.assertTrue((target / 'module/main.py').is_file())
            self.assertFalse((target / '.odoo-agents/tooling-venv').exists())

    def test_native_cli_enables_tools_but_not_delegation(self):
        cmd = native_command('codex', {'model':'fixture', 'effort':'high'})
        self.assertIn('multi_agent', cmd)
        self.assertNotIn('shell_tool', cmd)
        cmd = native_command('claude', {'model':'fixture', 'effort':'medium'})
        self.assertIn('Bash,Read,Write,Edit,Glob,Grep,Skill', cmd)


if __name__ == '__main__': unittest.main()
