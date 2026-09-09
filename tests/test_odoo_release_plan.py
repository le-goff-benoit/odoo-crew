"""Dépendances, fraîcheur, reprise et clôture sur un projet jetable."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import odoo_plan as plan
import odoo_release_guard as guard
import odoo_evidence as evidence
import odoo_loaded_instructions as loaded


class ReleasePlanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.release = self.root / 'changelog/test'; self.release.mkdir(parents=True)
        (self.release / 'README.md').write_text('<!-- release ouverte -->\n# Livraison\n')
        (self.root / 'request.md').write_text('demande originale')
        for mod in ('a', 'b'):
            (self.root / mod).mkdir(); (self.root / mod / 'code.py').write_text('a = 1\n')
        self.definition = {'schema': 1, 'tasks': [self.task('A', 'a'), self.task('B', 'b', ['A'])]}

    def task(self, identifier, scope, depends=None):
        return {'id': identifier, 'title': identifier, 'request': 'request.md', 'route': 'module',
                'risk': 'normal', 'acceptance': ['résultat attendu'], 'scopes': [scope], 'depends_on': depends or []}

    def init(self):
        plan.initialise(self.release, self.definition)

    def proof(self, scope='a'):
        p = self.root / 'proofs' / (scope + '.json')
        evidence.execute(self.root, [scope], p, [sys.executable, '-c', 'print("contrat valide")'])
        return str(p.relative_to(self.root))

    def finish_a(self):
        statefile = Path(plan.mutate(self.release, 'start', 'A'))
        state = json.loads(statefile.read_text()); state['status'] = 'complete'; statefile.write_text(json.dumps(state))
        # Le test porte sur la réception du plan ; le graphe lui-même a sa suite complète.
        for filename in ('acceptance.md', 'memory.md'):
            (self.root / filename).write_text('preuve de réception / absence de nouvelle connaissance expliquée')
        plan.mutate(self.release, 'finish', 'A', proof=self.proof(), acceptance='acceptance.md', memory='memory.md')

    def test_start_empty_module_and_deleted_snapshot(self):
        (self.root / 'a/code.py').unlink()
        self.init()
        statefile = Path(plan.mutate(self.release, 'start', 'A'))
        current, _ = plan.read(self.release)
        self.assertTrue(statefile.is_file())
        self.assertEqual(current['tasks'][0]['attempts'][0]['sources_before'], {})
        self.assertEqual(plan.source_snapshot(self.root, ['a', 'future']), {})
        with self.assertRaises(ValueError): evidence.fingerprint(self.root, ['a'])

    def test_add_tasks_preserves_receipt_and_rejects_forgery(self):
        self.init(); self.finish_a()
        before, _ = plan.read(self.release)
        plan.append_tasks(self.release, {'schema': 1, 'tasks': [self.task('C', 'c', ['A'])]})
        after, _ = plan.read(self.release)
        self.assertEqual(before['tasks'][0], after['tasks'][0])
        self.assertTrue(plan.available(after, self.root, 'C')[0])
        for task in [self.task('C', 'c'), dict(self.task('D', 'd'), receipt={}), self.task('D', 'd', ['missing'])]:
            with self.assertRaises(ValueError): plan.append_tasks(self.release, {'schema': 1, 'tasks': [task]})
        self.assertEqual(plan.read(self.release)[0], after)

    def test_dependency_receipt_and_stale_code(self):
        self.init(); p, _ = plan.read(self.release)
        self.assertFalse(plan.available(p, self.root, 'B')[0])
        self.finish_a(); p, _ = plan.read(self.release)
        self.assertTrue(plan.available(p, self.root, 'B')[0])
        (self.root / 'a/code.py').write_text('a = 2\n')
        self.assertEqual(plan.statuses(p, self.root)['A'][0], 'stale')
        self.assertFalse(plan.available(p, self.root, 'B')[0])

    def test_cyclic_and_outside_definitions_rejected(self):
        self.definition['tasks'][0]['depends_on'] = ['B']
        with self.assertRaises(ValueError): self.init()
        self.definition['tasks'][0]['depends_on'] = []
        self.definition['tasks'][0]['scopes'] = ['../elsewhere']
        with self.assertRaises(ValueError): self.init()

    def test_overlapping_tasks_wait_but_independent_ready(self):
        self.definition['tasks'] += [self.task('C', 'a'), self.task('D', 'b')]
        self.init(); plan.mutate(self.release, 'start', 'A'); p, _ = plan.read(self.release)
        self.assertFalse(plan.available(p, self.root, 'C')[0])
        self.assertTrue(plan.available(p, self.root, 'D')[0])
        with self.assertRaises(ValueError): plan.mutate(self.release, 'start', 'C')

    def test_existing_plan_and_fake_import_refused(self):
        self.init()
        with self.assertRaises(ValueError): self.init()
        other = self.root / 'changelog/other'; other.mkdir(); (other / 'README.md').write_text('x')
        self.definition['tasks'][0]['receipt'] = {'fake': True}
        with self.assertRaises(ValueError): plan.initialise(other, self.definition)

    def test_finish_requires_terminal_and_memory(self):
        self.init(); plan.mutate(self.release, 'start', 'A')
        with self.assertRaises(ValueError): plan.mutate(self.release, 'finish', 'A', proof=self.proof())

    def test_reopen_preserves_history_and_defer_is_not_dependency(self):
        self.init(); self.finish_a()
        plan.mutate(self.release, 'reopen', 'A', reason='décision D2')
        p, _ = plan.read(self.release)
        self.assertEqual(plan.statuses(p, self.root)['A'][0], 'pending')
        self.assertTrue(any(e['action'] == 'previous_attempt' for e in p['history']))
        plan.mutate(self.release, 'defer', 'A', reason='décision de périmètre')
        p, _ = plan.read(self.release)
        self.assertFalse(plan.available(p, self.root, 'B')[0])

    def test_missing_local_flow_is_not_green(self):
        self.init(); path = Path(plan.mutate(self.release, 'start', 'A')); path.unlink()
        p, _ = plan.read(self.release)
        self.assertEqual(plan.statuses(p, self.root)['A'][0], 'interrupted')

    def test_seal_requires_documents_and_invalidates_mutation(self):
        proof = self.proof()
        with self.assertRaises(ValueError): guard.seal(self.release, ['a'], [proof])
        for name in guard.REQUIRED:
            if name != 'README.md': (self.release / name).write_text('livrable réel')
        controls = {'schema':1,'risk':'normal','route':'studio','controls':[{'id':name,'status':'passed','proof':proof} for name in ('installation','update','tests','client_copy','browser','uninstall')]}
        (self.release / 'controls.json').write_text(json.dumps(controls))
        guard.seal(self.release, ['a'], [proof]); guard.check(self.release)
        (self.release / 'README.md').write_text('# Livraison\n')
        guard.check(self.release)
        (self.root / 'a/code.py').write_text('a=3')
        with self.assertRaises(ValueError): guard.check(self.release)

    def test_effort_report_is_sealed_even_when_measurements_are_missing(self):
        import odoo_effort as effort
        proof = self.proof()
        for name in guard.REQUIRED:
            if name != 'README.md':
                (self.release / name).write_text('preuve synthétique')
        controls = {'schema': 1, 'risk': 'normal', 'route': 'studio', 'controls': [
            {'id': name, 'status': 'passed', 'proof': proof}
            for name in ('installation', 'update', 'tests', 'client_copy', 'browser', 'uninstall')]}
        (self.release / 'controls.json').write_text(json.dumps(controls))
        effort.init(self.release)
        with self.assertRaises(FileNotFoundError):
            guard.seal(self.release, ['a'], [proof])
        effort.report(self.release)
        sealed = guard.seal(self.release, ['a'], [proof])
        guard.check(self.release)
        self.assertTrue(set(effort.REPORT_FILES) <= set(sealed['artifacts']))
        for name in ('effort.json',) + effort.REPORT_FILES:
            path = self.release / name
            original = path.read_bytes()
            path.write_bytes(original + b'\n')
            with self.assertRaises(ValueError):
                guard.check(self.release)
            path.write_bytes(original)
        registry = self.release / 'effort.json'
        original = registry.read_bytes()
        registry.unlink()
        with self.assertRaises(ValueError):
            guard.check(self.release)
        registry.write_bytes(original)
        guard.check(self.release)

    def test_dependency_rereception_does_not_revalidate_child(self):
        self.init(); self.finish_a()
        path = Path(plan.mutate(self.release, 'start', 'B'))
        state = json.loads(path.read_text()); state['status'] = 'complete'; path.write_text(json.dumps(state))
        plan.mutate(self.release, 'finish', 'B', proof=self.proof('b'), acceptance='acceptance.md', memory='memory.md')
        (self.root / 'a/code.py').write_text('a=2')
        p, _ = plan.read(self.release); self.assertEqual(plan.statuses(p,self.root)['B'][0], 'stale')
        plan.mutate(self.release, 'finish', 'A', proof=self.proof(), acceptance='acceptance.md', memory='memory.md')
        p, _ = plan.read(self.release)
        self.assertEqual(plan.statuses(p,self.root)['A'][0], 'validated')
        self.assertEqual(plan.statuses(p,self.root)['B'][0], 'stale')
        self.assertEqual(len(p['tasks'][0]['attempts']), 1)

    def test_release_identity_and_plan_presence_are_sealed(self):
        import shutil
        proof = self.proof()
        for name in guard.REQUIRED:
            if name != 'README.md': (self.release / name).write_text('preuve')
        data = {'schema':1,'risk':'normal','route':'studio','controls':[{'id':name,'status':'passed','proof':proof} for name in ('installation','update','tests','client_copy','browser','uninstall')]}
        (self.release / 'controls.json').write_text(json.dumps(data))
        guard.seal(self.release, ['a'], [proof])
        second = self.root / 'changelog/second'; shutil.copytree(self.release, second)
        with self.assertRaises(ValueError): guard.check(second)
        (self.release / 'plan.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'plan ajouté'):
            guard.check(self.release)

    def test_module_plan_cannot_claim_studio_controls(self):
        self.init()
        data = {'schema':1,'risk':'normal','route':'studio','controls':[{'id':name,'status':'passed','proof':'p'} for name in ('installation','update','tests','client_copy','browser','uninstall')]}
        (self.release / 'controls.json').write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'voie'):
            guard.controls(self.release,self.root,{'p':{}})

    def test_high_risk_cannot_waive_client_copy(self):
        controls = {'schema':1,'risk':'high','route':'studio','controls':[{'id':name,'status':'passed','proof':'p'} for name in ('installation','update','tests','browser','uninstall')] + [{'id':'client_copy','status':'waived','reason':'pas de copie'}]}
        (self.release / 'controls.json').write_text(json.dumps(controls))
        with self.assertRaisesRegex(ValueError,'client_copy'):
            guard.controls(self.release,self.root,{'p':{}})

    def test_changed_request_invalidates_receipt(self):
        self.init(); self.finish_a()
        (self.root / 'request.md').write_text('nouveau contrat')
        p, _ = plan.read(self.release)
        self.assertEqual(plan.statuses(p, self.root)['A'][0], 'stale')

    def test_version_prepare_idempotent_preserves_source(self):
        (self.root / 'a/__manifest__.py').write_text("# commentaire\n{'name':'été', 'version': '19.0.1.0.0'}\n")
        first = guard.prepare_release(self.release, ['a'])
        self.assertEqual(first['a']['target'], '19.0.1.0.1')
        self.assertEqual(guard.prepare_release(self.release, ['a']), first)
        self.assertTrue((self.root / 'a/__manifest__.py').read_text().startswith('# commentaire'))

    def test_close_shell_refuses_missing_seal(self):
        script = Path(__file__).resolve().parents[1] / 'scripts/odoo-release.sh'
        result = subprocess.run(['bash', str(script), 'close', str(self.release)], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('release ouverte', (self.release / 'README.md').read_text())

    def test_loaded_instructions_migration_keeps_user_text_and_backup(self):
        (self.root / 'AGENTS.md').write_text('# Personnel\n'+loaded.START+'\nancien\n'+loaded.END+'\n')
        legacy = self.root / '.agents/skills/camptocamp-docs'; legacy.mkdir(parents=True)
        (legacy / 'SKILL.md').write_text('Source : ~/.odoo19-agents/roles/docs.md\nancien')
        loaded.migrate(self.root)
        self.assertEqual(loaded.check(self.root), [])
        self.assertIn('# Personnel', (self.root / 'AGENTS.md').read_text())
        self.assertFalse(legacy.exists())
        self.assertTrue(list((self.root / '.odoo-agents-backups/loaded-instructions').iterdir()))
        before = (self.root / 'AGENTS.md').read_text(); loaded.migrate(self.root)
        self.assertEqual(before, (self.root / 'AGENTS.md').read_text())


if __name__ == '__main__': unittest.main()

class PlanHighRiskTests(unittest.TestCase):
    def test_downgrade_rejected_by_transition(self):
        import odoo_flow as flow
        graph_path = Path(__file__).resolve().parents[1] / 'workflows/odoo-workflow.json'
        graph = json.loads(graph_path.read_text())
        with tempfile.TemporaryDirectory() as tmp:
            state = flow.new_state(Path(tmp), 'development', 'high', graph_path)
            state['plan_task'] = {'risk':'high'}
            flow.complete_node(state, graph, 'briefing', 'development', ['synthetic evidence'])
            with self.assertRaisesRegex(flow.FlowError, 'module_high_risk'):
                flow.complete_node(state, graph, 'functional_review', 'module', ['synthetic evidence'])
            flow.complete_node(state, graph, 'functional_review', 'module_high_risk', ['synthetic evidence'])
            self.assertIn('module_implementation_high_risk', flow.ready_nodes(state, graph))
