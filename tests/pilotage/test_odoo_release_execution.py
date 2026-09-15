"""Contrats amont, contre-exemples de fraîcheur et continuation bornée."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import odoo_candidate as candidate
import odoo_evidence as evidence
import odoo_intentions as intentions
import odoo_orchestrate as orchestration
import odoo_plan as plan
from tests.pilotage import test_odoo_release_plan as fixtures


class StableReceipts(unittest.TestCase):
    setUp = fixtures.ReleasePlanTests.setUp
    task = fixtures.ReleasePlanTests.task
    init = fixtures.ReleasePlanTests.init
    finish_a = fixtures.ReleasePlanTests.finish_a

    def proof(self, scope='a'):
        if self.definition.get('schema') != 2:
            return fixtures.ReleasePlanTests.proof(self, scope)
        check = self.definition['tasks'][0]['checks'][0]
        path = self.root / 'proofs' / (scope + str(len(list((self.root / 'proofs').glob('*.json')))) + '.json')
        evidence.execute(self.root, [scope], path, check['command'], environment=check['environment'])
        return str(path.relative_to(self.root))

    def test_date_and_fresh_log_do_not_invalidate_same_result(self):
        self.init(); self.finish_a()
        path = Path(plan.mutate(self.release, 'start', 'B'))
        snapshot = json.loads(path.read_text()); snapshot['status'] = 'complete'; path.write_text(json.dumps(snapshot))
        plan.mutate(self.release, 'finish', 'B', proof=self.proof('b'), acceptance='acceptance.md', memory='memory.md')
        before, _ = plan.read(self.release)
        plan.mutate(self.release, 'finish', 'A', proof=self.proof(), acceptance='acceptance.md', memory='memory.md')
        after, _ = plan.read(self.release)
        self.assertNotEqual(before['tasks'][0]['receipt']['proof'], after['tasks'][0]['receipt']['proof'])
        self.assertEqual(plan.statuses(after, self.root)['B'][0], 'validated')
        after['tasks'][0]['receipt']['at'] = '2030-01-01T00:00:00Z'
        self.assertEqual(plan.statuses(after, self.root)['B'][0], 'validated')

    def test_scoped_source_addition_and_revision_impact(self):
        self.definition['tasks'][0]['request_excerpt'] = 'demande originale'
        self.init(); self.finish_a()
        (self.root / 'request.md').write_text('demande originale\n\nNouvelle demande indépendante')
        current, _ = plan.read(self.release)
        self.assertEqual(plan.statuses(current, self.root)['A'][0], 'validated')
        plan.revise_tasks(self.release, {'tasks': [{'id': 'B', 'acceptance': ['nouveau résultat B']}]}, 'Décision B2')
        current, _ = plan.read(self.release)
        self.assertEqual(plan.statuses(current, self.root)['A'][0], 'validated')
        (self.root / 'request.md').write_text('demande remplacée')
        self.assertEqual(plan.statuses(current, self.root)['A'][0], 'stale')

    def test_intentions_schema_two_and_history(self):
        definition = {'items': [{'id': 'I1', 'text': 'Demande', 'purpose': 'Résultat', 'source': {'path': 'request.md'}}]}
        intentions.update(self.release, definition)
        self.definition['schema'] = 2
        self.definition['author'] = {'role': 'orchestrator', 'provider': 'codex', 'model': 'principal'}
        self.definition['decisions'] = []
        self.definition['intentions_file'] = 'changelog/test/intentions.json'
        for task in self.definition['tasks']:
            task.update(intentions=['I1'], reads=[], writes=task['scopes'],
                        checks=[{'id': 'result', 'command': [sys.executable, '-c', 'print("contrat valide")'], 'environment': 'synthetic', 'cases': ['borne', 'vide']}],
                        execution={'provider': 'codex', 'model': 'principal', 'effort': 'high'})
        self.init(); self.finish_a()
        data = intentions.reconcile(self.release)
        self.assertEqual(data['items'][0]['status'], 'planned')
        self.assertEqual(data['items'][0]['tasks'], ['A', 'B'])
        changed = deepcopy(definition); changed['items'][0]['questions'] = ['Quelle borne ?']
        intentions.update(self.release, changed)
        current, _ = plan.read(self.release)
        self.assertFalse(plan.available(current, self.root, 'B')[0])
        self.assertEqual(plan.statuses(current, self.root)['A'][0], 'stale')
        data = intentions.read(self.release / 'intentions.json')
        self.assertTrue(any(e.get('item', {}).get('source', {}).get('original') == 'demande originale' for e in data['history']))

    def test_stop_guard_session_scope_idempotency_and_waits(self):
        self.init()
        state = orchestration.update(self.root, 'activate', owner='Codex principal', provider='codex', model='principal',
                                     session_id='s1', release=self.release, tasks=['A'])
        event = {'hook_event_name': 'Stop', 'session_id': 's1'}
        before = orchestration.state_path(self.root).read_bytes()
        result = orchestration.hook(state, event)
        self.assertEqual(result['decision'], 'block')
        self.assertIn('A:start', result['reason']); self.assertNotIn('B:start', result['reason'])
        self.assertEqual(orchestration.hook(state, event), result)
        self.assertEqual(orchestration.state_path(self.root).read_bytes(), before)
        for patch in ({'stop_hook_active': True}, {'session_id': 's2'}, {'hook_event_name': 'SubagentStop'},
                      {'hook_event_name': 'StopFailure'}, {'hook_event_name': 'Interrupt'}, {'parent_agent_id': 'parent'}):
            self.assertEqual(orchestration.hook(state, event | patch), {})
        for status in ('paused', 'interrupted', 'waiting_human', 'waiting_resource', 'complete'):
            self.assertEqual(orchestration.hook(state | {'status': status}, event), {})
        with self.assertRaises(ValueError):
            orchestration.update(self.root, 'pause', owner='someone else', reason='pause')
        self.finish_a()
        self.assertEqual(orchestration.hook(state, event), {})

    def test_preparation_attach_preserves_identity_and_timer(self):
        self.init()
        before = orchestration.update(self.root, 'activate', owner='principal', provider='claude', model='principal', session_id='s')
        after = orchestration.update(self.root, 'attach', owner='principal', release=self.release, tasks=['A', 'B'], phase='implementation')
        self.assertEqual(before['id'], after['id']); self.assertEqual(before['started_at'], after['started_at'])
        self.assertEqual(after['authorized_tasks'], ['A', 'B'])
        self.assertGreater(after['revision'], before['revision'])

    def test_received_tasks_do_not_satisfy_an_uncovered_intention(self):
        definition = {'items': [{'id': 'I1', 'text': 'sections', 'purpose': 'total correct',
                                 'criteria': ['total correct'], 'source': {'path': 'request.md'}}]}
        intentions.update(self.release, definition)
        self.definition['tasks'] = [self.task('A', 'a')]
        self.definition['tasks'][0]['intentions'] = ['I1']
        self.init(); self.finish_a()
        self.assertEqual(intentions.reconcile(self.release)['items'][0]['status'], 'planned')
        definition['items'][0]['coverage'] = [{'criterion': 'total correct', 'task': 'A', 'task_criterion': 'absent'}]
        intentions.update(self.release, definition)
        self.assertEqual(intentions.reconcile(self.release)['items'][0]['status'], 'planned')
        definition['items'][0]['coverage'][0]['task_criterion'] = 'résultat attendu'
        intentions.update(self.release, definition)
        self.assertEqual(intentions.reconcile(self.release)['items'][0]['status'], 'satisfied')

    def test_completed_orchestration_is_archived_and_wait_reason_persisted(self):
        self.init()
        state = orchestration.update(self.root, 'activate', owner='main', provider='codex', model='principal', session_id='s1')
        paused = orchestration.update(self.root, 'waiting-human', owner='main', reason='Quelle borne inclure ?')
        self.assertEqual(paused['reason'], 'Quelle borne inclure ?')
        orchestration.update(self.root, 'resume', owner='main', session_id='s2')
        orchestration.update(self.root, 'complete', owner='main')
        next_state = orchestration.update(self.root, 'activate', owner='main', provider='codex', model='principal', session_id='s3')
        self.assertNotEqual(state['id'], next_state['id'])
        archived = self.root / '.odoo-agents/orchestrations' / (state['id'] + '.json')
        self.assertEqual(json.loads(archived.read_text())['status'], 'complete')

    def test_prescribed_checks_cannot_be_replaced_or_omitted(self):
        self.definition['tasks'] = [self.task('A', 'a')]
        task = self.definition['tasks'][0]
        command = [sys.executable, '-c', 'print("required")']
        second = [sys.executable, '-c', 'print("other-required")']
        task['checks'] = [{'id': 'required', 'command': command, 'environment': 'required-env', 'cases': ['expected result']},
                          {'id': 'other', 'command': second, 'environment': 'required-env', 'cases': ['boundary']}]
        self.init()
        path = Path(plan.mutate(self.release, 'start', 'A'))
        state = json.loads(path.read_text()); state['status'] = 'complete'; path.write_text(json.dumps(state))
        for name in ('acceptance.md', 'memory.md'): (self.root / name).write_text('explicit reception')
        def checked(name, argv, environment):
            output = self.root / (name + '.json')
            evidence.execute(self.root, ['a'], output, argv, environment=environment)
            return output.name
        good = checked('good', command, 'required-env')
        other = checked('other', second, 'required-env')
        fake = checked('fake', [sys.executable, '-c', 'print("fake")'], 'required-env')
        unknown = checked('unknown', command, None)
        failed = checked('failed', [sys.executable, '-c', 'raise SystemExit(1)'], 'required-env')
        kwargs = {'acceptance': 'acceptance.md', 'memory': 'memory.md'}
        for mapping in ({'required': good}, {'required': fake, 'other': other},
                        {'required': unknown, 'other': other}, {'required': failed, 'other': other}):
            with self.assertRaises(ValueError):
                plan.mutate(self.release, 'finish', 'A', check_proofs=mapping, **kwargs)
        plan.mutate(self.release, 'finish', 'A', check_proofs={'required': good, 'other': other}, **kwargs)
        current, _ = plan.read(self.release)
        self.assertEqual(plan.statuses(current, self.root)['A'][0], 'validated')
        (self.root / other).write_text('{}')
        self.assertEqual(plan.statuses(current, self.root)['A'][0], 'stale')


class PortableCandidates(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'; self.root.mkdir()
        self.git('init', '-q'); self.git('config', 'user.email', 'test@example.invalid'); self.git('config', 'user.name', 'Test')
        (self.root / 'module').mkdir(); (self.root / 'module/code.py').write_text('value = 1')
        self.git('add', '.'); self.git('commit', '-qm', 'fixture')
        self.worktree = self.root.parent / 'candidate'
        self.git('worktree', 'add', '--detach', '-q', str(self.worktree))

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.DEVNULL)

    def test_portable_proof_checks_same_repo_revision_content_and_logs(self):
        proof = evidence.execute(self.worktree, ['module'], self.worktree / 'proof.json', [sys.executable, '-c', 'print("ok")'])
        shutil.copy(self.worktree / 'proof.log', self.root / 'proof.log')
        evidence.verify(proof, self.root)
        clone = self.root.parent / 'clone'
        subprocess.check_call(['git', 'clone', '-q', str(self.root), str(clone)])
        with self.assertRaisesRegex(ValueError, 'autre projet'): evidence.verify(proof, clone)
        (self.root / 'module/code.py').write_text('value = 2')
        with self.assertRaisesRegex(ValueError, 'code changé'): evidence.verify(proof, self.root)
        with self.assertRaisesRegex(ValueError, 'immuable'):
            evidence.execute(self.worktree, ['module'], self.worktree / 'proof.json', [sys.executable, '-c', 'print("fake")'])

    def test_parallel_candidate_refuses_shared_resources_and_mutation(self):
        physical = {k: ('path:' + str(self.worktree / k)) for k in candidate.REQUIRED}
        frozen = {'project': str(self.worktree), 'repository': evidence.repository_identity(self.worktree),
                  'scopes': ['module'], 'sources': evidence.fingerprint(self.worktree, ['module']), 'resources': physical}
        own = {k: ('path:' + str(self.root / k)) for k in candidate.REQUIRED}
        self.assertTrue(candidate.isolated(frozen, {'resources': own}))
        self.assertFalse(candidate.isolated(frozen, {}))
        self.assertFalse(candidate.isolated(frozen, {'resources': own | {'database': physical['database']}}))
        (self.worktree / 'module/code.py').write_text('mutated during QA')
        self.assertFalse(candidate.isolated(frozen, {'resources': own}))

    def test_frozen_qa_and_development_overlap_with_real_leases(self):
        import time
        release = self.root / 'changelog/probe'; release.mkdir(parents=True)
        (release / 'README.md').write_text('# probe')
        (self.root / 'request.md').write_text('QA A, indépendant B')
        physical_a = {k: 'path:' + str(self.worktree.parent / ('qa-a-' + k)) for k in candidate.REQUIRED}
        physical_b = {k: 'path:' + str(self.root.parent / ('dev-b-' + k)) for k in candidate.REQUIRED}
        def task(identifier, resources):
            return {'id': identifier, 'title': identifier, 'request': 'request.md', 'route': 'module', 'risk': 'normal',
                    'acceptance': ['assertion ' + identifier], 'scopes': ['module'], 'depends_on': [], 'resources': resources,
                    'check_scopes': ['module/code.py'], 'selection_reason': 'B ajoute un fichier indépendant, sans lecture ni interface utilisée par A'}
        (self.root / '.odoo-agents').mkdir(exist_ok=True)
        (self.root / '.odoo-agents/resources.json').write_text(json.dumps({'schema': 1, 'registry': str(self.root.parent / 'shared-locks.json'), 'bindings': {}}))
        plan.initialise(release, {'schema': 1, 'tasks': [task('A', physical_a), task('B', physical_b)]})
        path = Path(plan.mutate(release, 'start', 'A'))
        snapshot, graph = plan.flow.load_state(path, plan.flow.DEFAULT_GRAPH)
        snapshot['start_pending'] = False
        snapshot['tokens'] = {edge['id']: 1 for edge in graph['edges'] if edge['to'] == 'module_static_qa'}
        plan.flow.write_state(path, snapshot)
        candidate.freeze(release, 'A', self.worktree, physical_a)
        definition, _ = plan.read(release)
        self.assertTrue(plan.available(definition, self.root, 'B')[0])
        definition['tasks'][1]['resources']['database'] = physical_a['database']
        self.assertFalse(plan.available(definition, self.root, 'B')[0])
        plan.flow.claim_node(path, plan.flow.DEFAULT_GRAPH, 'module_static_qa', 'Codex QA A')
        original = plan.flow.load_json(path)
        other_path = path.parent / 'competitor.json'
        other = deepcopy(original); other['run_id'] = 'competitor'; other['claims'] = {}
        plan.flow.write_state(other_path, other)
        with self.assertRaises(plan.flow.FlowError):
            plan.flow.claim_node(other_path, plan.flow.DEFAULT_GRAPH, 'module_static_qa', 'Claude QA conflicting')
        # A performs a frozen assertion while B really writes and tests an independent file.
        scripts = str(Path(__file__).resolve().parents[2] / 'scripts')
        def command(root, label, mutate):
            return [sys.executable, '-c',
                    "import json,time,sys; from pathlib import Path; sys.path.insert(0, %r); import odoo_evidence as e; "
                    "root=Path(%r); started=time.time(); time.sleep(.3); %s; "
                    "p=e.execute(root,['module/code.py'],root/(%r+'-proof.json'),[sys.executable,'-c',\"from pathlib import Path; assert 'value = 1' in Path('module/code.py').read_text()\"]); "
                    "print(json.dumps({'label':%r,'start':started,'end':time.time(),'passed':p['result']=='passed'}))"
                    % (scripts, str(root), "(root/'module/b.py').write_text('value_b = 2')" if mutate else 'None', label, label)]
        started = time.monotonic()
        processes = [subprocess.Popen(command(self.worktree, 'qa-parallel', False), stdout=subprocess.PIPE, text=True),
                     subprocess.Popen(command(self.root, 'dev-parallel', True), stdout=subprocess.PIPE, text=True)]
        records = [json.loads(p.communicate(timeout=10)[0]) for p in processes]
        parallel = time.monotonic() - started
        self.assertTrue(all(r['passed'] for r in records))
        self.assertLess(max(r['start'] for r in records), min(r['end'] for r in records))
        started = time.monotonic()
        for root, label, mutate in [(self.worktree, 'qa-sequential', False), (self.root, 'dev-sequential', True)]:
            subprocess.check_output(command(root, label, mutate), text=True)
        sequential = time.monotonic() - started
        self.assertTrue(candidate.valid(original['candidate']))
        final = evidence.execute(self.root, ['module'], self.root / 'integration-proof.json',
            [sys.executable, '-c', "from pathlib import Path; assert 'value = 1' in Path('module/code.py').read_text(); assert 'value_b = 2' in Path('module/b.py').read_text()"])
        self.assertEqual(final['result'], 'passed')
        print(json.dumps({'probe': 'real_process_overlap_synthetic_only', 'parallel_seconds': round(parallel, 3),
                          'sequential_seconds': round(sequential, 3), 'events': records, 'integration': final['result']}))

    def test_physical_registry_is_required_and_shared_across_projects(self):
        shared = self.root.parent / 'physical-shared.json'
        physical = {k: 'path:' + str(self.root.parent / ('shared-' + k)) for k in candidate.REQUIRED}
        paths = []
        for root in (self.root, self.worktree):
            release = root / 'changelog/probe'; release.mkdir(parents=True)
            (release / 'README.md').write_text('probe'); (root / 'request.md').write_text('probe')
            task = {'id': 'A', 'title': 'A', 'request': 'request.md', 'acceptance': ['result'], 'risk': 'normal',
                    'route': 'module', 'scopes': ['module'], 'resources': physical}
            plan.initialise(release, {'schema': 1, 'tasks': [task]})
            with self.assertRaisesRegex(ValueError, 'registre partagé'):
                plan.mutate(release, 'start', 'A')
            (root / '.odoo-agents/resources.json').write_text(json.dumps({'schema': 1, 'registry': str(shared), 'bindings': {}}))
            path = Path(plan.mutate(release, 'start', 'A'))
            state, graph = plan.flow.load_state(path, plan.flow.DEFAULT_GRAPH)
            state['start_pending'] = False
            state['tokens'] = {e['id']: 1 for e in graph['edges'] if e['to'] == 'module_static_qa'}
            plan.flow.write_state(path, state); paths.append(path)
        plan.flow.claim_node(paths[0], plan.flow.DEFAULT_GRAPH, 'module_static_qa', 'QA first')
        with self.assertRaises(plan.flow.FlowError):
            plan.flow.claim_node(paths[1], plan.flow.DEFAULT_GRAPH, 'module_static_qa', 'QA second')

    def test_qa_retry_restores_source_and_waits_for_other_development(self):
        release = self.root / 'changelog/retry'; release.mkdir(parents=True)
        (release / 'README.md').write_text('retry probe'); (self.root / 'request.md').write_text('probe')
        (self.root / '.odoo-agents').mkdir(exist_ok=True)
        (self.root / '.odoo-agents/resources.json').write_text(json.dumps({'schema': 1, 'registry': str(self.root.parent / 'retry-shared.json'), 'bindings': {}}))
        def task(identifier):
            return {'id': identifier, 'title': identifier, 'request': 'request.md', 'acceptance': ['result'], 'risk': 'normal',
                    'route': 'module', 'scopes': ['module'], 'resources': {k: 'path:' + str(self.root.parent / (identifier + '-' + k)) for k in candidate.REQUIRED}}
        a, b = task('A'), task('B')
        plan.initialise(release, {'schema': 1, 'tasks': [a, b]})
        path = Path(plan.mutate(release, 'start', 'A'))
        state, graph = plan.flow.load_state(path, plan.flow.DEFAULT_GRAPH)
        original_binding = state['resource_bindings']['module_code']
        state['start_pending'] = False
        state['tokens'] = {e['id']: 1 for e in graph['edges'] if e['to'] == 'module_static_qa'}
        plan.flow.write_state(path, state)
        candidate.freeze(release, 'A', self.worktree, a['resources'])
        plan.mutate(release, 'start', 'B')
        current, _ = plan.read(release)
        self.assertTrue(candidate.active_for_task(current['tasks'][0], self.root))
        state, graph = plan.flow.load_state(path, plan.flow.DEFAULT_GRAPH)
        state['tokens'] = {e['id']: 1 for e in graph['edges'] if e['to'] == 'module_task_gate'}
        plan.flow.write_state(path, state)
        self.assertFalse(candidate.active_for_task(current['tasks'][0], self.root))
        report = self.root / 'qa-red.md'; report.write_text('Synthetic control red: correct A; B independent remains in progress.')
        plan.flow.claim_node(path, plan.flow.DEFAULT_GRAPH, 'module_task_gate', 'principal')
        plan.flow.complete_claimed_node(path, plan.flow.DEFAULT_GRAPH, 'module_task_gate', 'retry', [str(report)], None, 'principal', False)
        state, graph = plan.flow.load_state(path, plan.flow.DEFAULT_GRAPH)
        self.assertNotIn('candidate', state)
        self.assertEqual(state['resource_bindings']['module_code'], original_binding)
        self.assertEqual(len(state['candidate_history']), 1)
        with self.assertRaisesRegex(plan.flow.FlowError, 'réservé par B'):
            plan.flow.claim_node(path, plan.flow.DEFAULT_GRAPH, 'module_implementation', 'developer A')
