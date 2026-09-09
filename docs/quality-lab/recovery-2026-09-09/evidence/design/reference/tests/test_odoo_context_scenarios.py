import hashlib
import json
from pathlib import Path
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import odoo_context as context
import odoo_scenarios as scenarios
from odoo_bench_native import inside, copy_project, native_command, native_delegation_summary, trial, Lab


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

    def test_context_cannot_claim_another_project(self):
        record = context.context(self.root)
        record['project'] = '/another-project'
        with self.assertRaisesRegex(ValueError, 'autre projet'):
            context.verify_context(record, self.root)

    def test_unselected_source_becoming_relevant_invalidates_context(self):
        record = context.context(self.root, query='livraison')
        self.assertNotIn('decisions/D1.md', [r['path'] for r in record['sources']])
        self.source.write_text('La livraison suit une nouvelle règle.')
        with self.assertRaisesRegex(ValueError, 'catalogue'):
            context.verify_context(record, self.root)

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

    def test_lint_bridge_is_bounded_and_records_real_command_result(self):
        lab = Lab.__new__(Lab)
        lab.lock = threading.Lock(); lab.case = {'module': 'module'}
        lab.folder = self.root; lab.project = self.root; lab.pack = self.root / 'pack'
        lab.backend = self.root / 'backend'; lab.env = {}; lab.events = []
        with patch.object(lab, 'sync'), patch('odoo_bench_native.execute', return_value=SimpleNamespace(stdout='ruff passed', returncode=0)) as execute:
            with self.assertRaises(ValueError): lab.handle(['lint', 'another_module'])
            execute.assert_not_called()
            result = lab.handle(['lint', 'module'])
        self.assertEqual(result['exit_code'], 0)
        self.assertEqual(execute.call_args.args[0], ['bash', str(lab.pack / 'scripts/odoo-lint.sh'), str(lab.backend / 'addons/module')])
        self.assertEqual(lab.events[0]['args'], ['lint', 'module'])
        self.assertEqual((self.root / 'bridge-000.log').read_text(), 'ruff passed')

    def test_failed_native_setup_is_preserved_as_incident(self):
        with patch('odoo_bench_native._trial', side_effect=RuntimeError('build failed')):
            folder = self.root / 'trial'
            result = trial(folder, self.root, {'id': 'N00'}, 'codex', {}, 1)
        self.assertEqual(result['status'], 'incident')
        self.assertEqual(result['turns'], [])
        self.assertEqual(json.loads((folder / 'state.json').read_text()), result)

    def test_native_cli_enables_tools_but_not_delegation(self):
        cmd = native_command('codex', {'model':'fixture', 'effort':'high'})
        self.assertIn('multi_agent', cmd)
        self.assertNotIn('shell_tool', cmd)
        cmd = native_command('claude', {'model':'fixture', 'effort':'medium'})
        self.assertIn('Bash,Read,Write,Edit,Glob,Grep,Skill', cmd)

    def test_delegation_requires_explicit_claude_option(self):
        settings = {'model': 'fixture', 'effort': 'medium', 'delegate': True}
        cmd = native_command('claude', settings)
        exposed = cmd[cmd.index('--tools') + 1].split(',')
        self.assertTrue({'Agent', 'TaskOutput', 'TaskStop'}.issubset(exposed))
        with self.assertRaises(ValueError):
            native_command('codex', settings)

    def test_native_delegation_counts_agent_work_not_shell_or_requests(self):
        raw = self.root / 'raw.jsonl'
        rows = [
            {'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'name': 'Agent'}]}},
            {'type': 'system', 'subtype': 'task_started', 'task_type': 'local_bash', 'task_id': 'shell'},
            {'type': 'system', 'subtype': 'task_notification', 'task_id': 'shell', 'status': 'completed'},
        ]
        raw.write_text('\n'.join(json.dumps(row) for row in rows))
        self.assertEqual(native_delegation_summary(raw, 'claude')['started'], 0)
        for task_id, outcome in [('a', 'completed'), ('b', 'failed')]:
            rows.extend([
                {'type': 'system', 'subtype': 'task_started', 'task_type': 'local_agent',
                 'task_id': task_id, 'tool_use_id': 'call-' + task_id, 'subagent_type': 'odoo-tester'},
                {'type': 'system', 'subtype': 'task_progress', 'task_id': task_id},
                {'type': 'system', 'subtype': 'task_notification', 'task_id': task_id, 'status': outcome},
            ])
        raw.write_text('\n'.join(json.dumps(row) for row in rows))
        result = native_delegation_summary(raw, 'claude')
        self.assertEqual(result['started'], 2)
        self.assertEqual(result['with_progress'], 2)
        self.assertEqual(result['completed'], 1)
        self.assertEqual(result['tasks']['b']['status'], 'failed')
        self.assertEqual(native_delegation_summary(raw, 'codex'), {'supported': False})

    def test_native_delegation_keeps_interrupted_child_incomplete(self):
        raw = self.root / 'partial.jsonl'
        row = {'type': 'system', 'subtype': 'task_started', 'task_type': 'local_agent', 'task_id': 'unfinished'}
        raw.write_text('not JSON\nnull\n' + json.dumps(row))
        result = native_delegation_summary(raw, 'claude')
        self.assertEqual(result['started'], 1)
        self.assertEqual(result['with_progress'], 0)
        self.assertEqual(result['completed'], 0)
        self.assertEqual(result['tasks']['unfinished']['status'], 'incomplete')
        self.assertIsNone(result['provider_summary'])


if __name__ == '__main__': unittest.main()
