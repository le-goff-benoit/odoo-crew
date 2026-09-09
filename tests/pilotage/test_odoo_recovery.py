"""Reprise mémoire sur projets jetables ; les jetons initiaux sont des fixtures QA."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from . import test_odoo_reception as fixtures

flow = fixtures.flow
reception = fixtures.reception


class RecoveryTests(unittest.TestCase):
    setUp = fixtures.ReceptionTests.setUp
    ready = fixtures.ReceptionTests.ready
    prepare = fixtures.ReceptionTests.prepare
    receipt = fixtures.ReceptionTests.receipt
    finish = fixtures.ReceptionTests.finish
    assert_rejected_unchanged = fixtures.ReceptionTests.assert_rejected_unchanged

    def accepted(self, gate='module_task_gate'):
        path = self.ready(gate)
        review, _ = self.receipt(self.prepare(path))
        self.finish(path, gate, [review])
        flow.claim_node(path, self.graph, 'journal_task', self.owner)
        return path, review

    def retry(self, path):
        self.finish(path, 'journal_task', [self.root / 'runtime.log'], 'retry')
        flow.claim_node(path, self.graph, flow.RECOVERY_GATE, self.owner)

    def renew(self, path, number=1):
        # Nouveaux fichiers : l'ancien dossier et ses propositions restent archivés.
        for prefix, target in [('project', 'PROJECT'), ('journal', 'JOURNAL')]:
            (self.root / f'{prefix}-{number}.md').write_text(
                (self.root / f'.odoo-agents/{target}.md').read_text() + f'\nTâche reprise {number}.')
        pin = self.prepare(path, f'bundle-{number}.json', memories=[
            f'.odoo-agents/PROJECT.md=project-{number}.md',
            f'.odoo-agents/JOURNAL.md=journal-{number}.md'])
        review_path, review = self.receipt(pin, f'review-{number}.json')
        bundle = json.loads((self.root / pin['path']).read_text())
        review['checks']['source_memory']['citations'] = [
            {'path': name, 'quote': (self.root / name).read_text()} for name in
            ['request.md'] + [row['draft']['path'] for row in bundle['memory']] +
            [row['base']['path'] for row in bundle['memory'] if row.get('base')]]
        review_path.write_text(json.dumps(review))
        return review_path

    def test_conflict_three_gates_reception_preserves_other_task(self):
        for gate in sorted(fixtures.GATES):
            with self.subTest(gate=gate):
                path, old = self.accepted(gate)
                for target in reception.TARGETS:
                    (self.root / target).write_text('Mémoire publiée par tâche B.')
                before = {target: (self.root / target).read_bytes() for target in reception.TARGETS}
                with self.assertRaises(flow.FlowError): flow.publish_memory(path, self.graph, self.owner)
                self.assertEqual(before, {target: (self.root / target).read_bytes() for target in reception.TARGETS})
                self.retry(path)
                fresh = self.renew(path)
                self.assert_rejected_unchanged(path, flow.RECOVERY_GATE, [old])
                self.finish(path, flow.RECOVERY_GATE, [fresh])
                self.assertEqual(len(flow.load_json(path)['accepted_reception_history']), 1)
                flow.claim_node(path, self.graph, 'journal_task', self.owner)
                flow.publish_memory(path, self.graph, self.owner)
                self.assertTrue(all((self.root / t).read_text().startswith('Mémoire publiée par tâche B.') for t in reception.TARGETS))
                self.finish(path, 'journal_task', [fresh], 'done')
                # Les noms suivants sont nouveaux dans chaque sous-cas.
                for p in self.root.glob('bundle*'): p.unlink()
                for p in self.root.glob('review*'): p.unlink()

    def test_publish_interruption_is_idempotent_without_state_edit(self):
        path, _ = self.accepted()
        before_state = path.read_bytes()
        original = reception.atomic_publish
        calls = []
        def interrupt(target, content):
            original(target, content)
            calls.append(target)
            raise OSError('interruption après premier replace')
        with patch.object(reception, 'atomic_publish', interrupt):
            with self.assertRaises(flow.FlowError): flow.publish_memory(path, self.graph, self.owner)
        self.assertEqual(path.read_bytes(), before_state)
        self.assertEqual(len(calls), 1)
        result = flow.publish_memory(path, self.graph, self.owner)
        self.assertEqual([r['action'] for r in result], ['already_published', 'published'])
        self.assertTrue(all(r['action'] == 'already_published' for r in flow.publish_memory(path, self.graph, self.owner)))
        self.assertEqual(path.read_bytes(), before_state)
        self.finish(path, 'journal_task', [self.root / '.odoo-agents/JOURNAL.md'], 'done')

    def test_prevalidation_all_targets_and_bad_owner_never_write(self):
        path, _ = self.accepted()
        (self.root / '.odoo-agents/JOURNAL.md').write_text('Valeur tierce.')
        before = {target: (self.root / target).read_bytes() for target in reception.TARGETS}
        state = path.read_bytes()
        for owner in [self.owner, 'autre propriétaire']:
            with self.assertRaises(flow.FlowError): flow.publish_memory(path, self.graph, owner)
            self.assertEqual(before, {target: (self.root / target).read_bytes() for target in reception.TARGETS})
            self.assertEqual(path.read_bytes(), state)

    def test_changed_sources_contract_proof_code_never_recovery(self):
        path, _ = self.accepted()
        for name in ['request.md', 'spec.md', 'runtime.log', 'module/business.py']:
            target = self.root / name
            original = target.read_bytes(); target.write_bytes(original + b'\nchange')
            self.assert_rejected_unchanged(path, 'journal_task', [self.root / 'runtime.log'], 'retry')
            target.write_bytes(original)
        self.retry(path)
        for name in ['request.md', 'spec.md', 'runtime.log', 'module/business.py']:
            target = self.root / name
            original = target.read_bytes(); target.write_bytes(original + b'\nchange')
            before = path.read_bytes()
            with self.assertRaises(flow.FlowError): self.prepare(path, 'refused.json')
            self.assertFalse((self.root / 'refused.json').exists())
            self.assertEqual(path.read_bytes(), before)
            target.write_bytes(original)
        with self.assertRaises(flow.FlowError): self.prepare(path, 'refused.json', scopes=[])
        fresh = self.renew(path)
        (self.root / 'runtime.log').write_text('preuve remplacée après préparation')
        self.assert_rejected_unchanged(path, flow.RECOVERY_GATE, [fresh])
        self.finish(path, flow.RECOVERY_GATE, [self.root / 'runtime.log'], 'blocked')

    def test_previous_drafts_may_be_stale_but_bases_stay_pinned(self):
        path, _ = self.accepted()
        (self.root / 'project-draft.md').write_text('ancien brouillon périmé')
        self.retry(path)
        fresh = self.renew(path)
        self.finish(path, flow.RECOVERY_GATE, [fresh])
        flow.claim_node(path, self.graph, 'journal_task', self.owner)
        flow.publish_memory(path, self.graph, self.owner)
        base = self.root / 'bundle-1.json.PROJECT.md.base'
        base.write_text('base falsifiée')
        self.assert_rejected_unchanged(path, 'journal_task', [fresh], 'retry')

    def test_receipt_requires_all_preserved_bases(self):
        path = self.ready()
        review_path, review = self.receipt(self.prepare(path))
        review['checks']['source_memory']['citations'] = [c for c in review['checks']['source_memory']['citations'] if not c['path'].endswith('.base')]
        review_path.write_text(json.dumps(review))
        self.assert_rejected_unchanged(path, 'module_task_gate', [review_path])

    def test_two_retries_then_real_block_allows_plan_reopen(self):
        import odoo_plan as plan
        release = self.root / 'changelog/test'; release.mkdir(parents=True)
        (release / 'README.md').write_text('<!-- release ouverte -->')
        definition = {'schema': 1, 'tasks': [{'id': 'A', 'title': 'A', 'request': 'request.md',
            'route': 'module', 'risk': 'normal', 'acceptance': ['calcul conservé'], 'scopes': ['module'], 'depends_on': []}]}
        plan.initialise(release, definition)
        path = Path(plan.mutate(release, 'start', 'A'))
        state = flow.load_json(path)
        state['start_pending'] = False
        state['tokens'] = {e['id']: 1 for e in flow.incoming_edges(state['graph_snapshot'], 'module_task_gate')}
        flow.write_state(path, state)  # Seule fixture : entrée QA, puis transitions publiques.
        flow.claim_node(path, self.graph, 'module_task_gate', self.owner)
        review, _ = self.receipt(self.prepare(path))
        self.finish(path, 'module_task_gate', [review])
        flow.claim_node(path, self.graph, 'journal_task', self.owner)
        for number in (1, 2):
            self.retry(path)
            with self.assertRaises(ValueError): plan.mutate(release, 'reopen', 'A', reason='encore actif')
            fresh = self.renew(path, number)
            self.finish(path, flow.RECOVERY_GATE, [fresh])
            flow.claim_node(path, self.graph, 'journal_task', self.owner)
        self.assert_rejected_unchanged(path, 'journal_task', [review], 'retry')
        self.finish(path, 'journal_task', [review], 'blocked')
        flow.claim_node(path, self.graph, 'memory_task_blocked', self.owner)
        self.finish(path, 'memory_task_blocked', [review], 'done')
        self.assertEqual(plan.task_status(plan.read(release)[0]['tasks'][0], self.root)[0], 'blocked')
        plan.mutate(release, 'reopen', 'A', reason='nouvelle tentative explicite')
        current = plan.read(release)[0]
        self.assertEqual(plan.task_status(current['tasks'][0], self.root)[0], 'pending')
        self.assertTrue(any(e['action'] == 'previous_attempt' for e in current['history']))

    def test_legacy_guard_absent_cannot_take_new_exits(self):
        path = self.ready()
        self.finish(path, 'module_task_gate', [self.root / 'runtime.log'])
        flow.claim_node(path, self.graph, 'journal_task', self.owner)
        for outcome in ['retry', 'blocked']:
            self.assert_rejected_unchanged(path, 'journal_task', [self.root / 'runtime.log'], outcome)
        with self.assertRaises(flow.FlowError): flow.publish_memory(path, self.graph, self.owner)
        self.finish(path, 'journal_task', [self.root / 'runtime.log'], 'done')

    def test_two_flow_memory_claims_and_owner_transfer(self):
        first, _ = self.accepted()
        second = self.ready('studio_task_gate')
        review, _ = self.receipt(self.prepare(second, 'second-bundle.json'), 'second-review.json')
        self.finish(second, 'studio_task_gate', [review])
        with self.assertRaises(flow.FlowError): flow.claim_node(second, self.graph, 'journal_task', self.owner)
        flow.release_claim(first, self.graph, 'journal_task', self.owner, 'transfert explicite')
        with self.assertRaises(flow.FlowError): flow.publish_memory(first, self.graph, self.owner)
        new_owner = 'codex-reprise'
        flow.claim_node(first, self.graph, 'journal_task', new_owner)
        with self.assertRaises(flow.FlowError): flow.publish_memory(first, self.graph, self.owner)
        flow.publish_memory(first, self.graph, new_owner)
        flow.complete_claimed_node(first, self.graph, 'journal_task', 'done',
            [str(self.root / '.odoo-agents/JOURNAL.md')], None, new_owner, False)
        flow.claim_node(second, self.graph, 'journal_task', self.owner)
        # Les deux intentions sont identiques dans cette fixture : rien à réécrire.
        self.assertTrue(all(row['action'] == 'already_published' for row in flow.publish_memory(second, self.graph, self.owner)))
        self.retry(second)

    def test_new_recovery_graph_cannot_weaken_extension(self):
        old = self.old_graph()
        path = self.root / 'historical.json'
        state = flow.new_state(self.root, 'development', 'old', old)
        flow.write_state(path, state)
        for kind in ['lock', 'limit', 'edge', 'description']:
            candidate = flow.load_json(self.graph)
            if kind == 'lock': candidate['nodes'][flow.RECOVERY_GATE]['locks'] = []
            if kind == 'limit': candidate['nodes'][flow.RECOVERY_GATE]['max_outcome_uses']['pass'] = 3
            if kind == 'description': candidate['nodes']['memory_task_blocked']['description'] = 'QA rouge'
            if kind == 'edge':
                for edge in candidate['edges']:
                    if edge['id'] == 'reception-memory-blocked': edge['to'] = 'task_done'
            wrong = self.root / 'weakened.json'; wrong.write_text(json.dumps(candidate))
            before = path.read_bytes()
            with self.assertRaises(flow.FlowError): flow.upgrade_recovery(path, wrong, self.owner)
            self.assertEqual(path.read_bytes(), before)

    def test_cli_publish_requires_accepted_claim_and_keeps_journal_active(self):
        path, _ = self.accepted()
        self.assertEqual(flow.main(['--graph', str(self.graph), 'publish-memory', str(path), '--owner', self.owner]), 0)
        self.assertIn('journal_task', flow.load_json(path)['claims'])

    def test_empty_and_whitespace_memory_have_preserved_bases_without_impossible_quote(self):
        for name, text in zip(sorted(reception.TARGETS), ['', ' \n\t ']):
            (self.root / name).write_text(text)
        path = self.ready()
        pinned = self.prepare(path)
        review_path, review = self.receipt(pinned)
        review['checks']['source_memory']['citations'] = [citation for citation in review['checks']['source_memory']['citations'] if citation['quote'].strip()]
        review_path.write_text(json.dumps(review))
        self.finish(path, 'module_task_gate', [review_path])
        flow.claim_node(path, self.graph, 'journal_task', self.owner)
        flow.publish_memory(path, self.graph, self.owner)

    def test_old_accepted_flow_upgrades_then_recovers_without_replaying_qa(self):
        new = self.graph
        self.graph = self.old_graph()
        path, _ = self.accepted()
        flow.release_claim(path, self.graph, 'journal_task', self.owner, 'migration explicite')
        old_events = flow.load_json(path)['events']
        flow.upgrade_recovery(path, new, self.owner, self.graph)
        self.graph = new
        flow.claim_node(path, self.graph, 'journal_task', self.owner)
        (self.root / '.odoo-agents/PROJECT.md').write_text('autre tâche préservée')
        self.retry(path)
        fresh = self.renew(path)
        self.finish(path, flow.RECOVERY_GATE, [fresh])
        flow.claim_node(path, self.graph, 'journal_task', self.owner)
        flow.publish_memory(path, self.graph, self.owner)
        self.finish(path, 'journal_task', [fresh], 'done')
        self.assertEqual(flow.load_json(path)['events'][:len(old_events)], old_events)
        self.assertEqual(flow.load_json(path)['node_counts']['module_task_gate'], 1)

    def test_old_graph_plan_guard_still_refused(self):
        self.graph = self.old_graph()
        path = self.ready()
        state = flow.load_json(path)
        state['plan_task'] = {'id': 'A'}
        flow.write_state(path, state)
        before = path.read_bytes()
        with self.assertRaises(flow.FlowError): self.prepare(path)
        self.assertEqual(path.read_bytes(), before)

    def old_graph(self):
        graph = copy.deepcopy(flow.load_json(self.graph))
        for node in flow.RECOVERY_NODES: graph['nodes'].pop(node)
        graph['edges'] = [e for e in graph['edges'] if e['id'] not in flow.RECOVERY_EDGES]
        path = self.root / 'old-graph.json'; path.write_text(json.dumps(graph))
        return path

    def test_upgrade_exact_addition_preserves_tokens_events_and_contract(self):
        old = self.old_graph()
        path = self.root / 'historical.json'
        state = flow.new_state(self.root, 'development', 'old', old)
        state['start_pending'] = False; state['tokens'] = {'module-gate-pass': 1}
        state['events'] = [{'node': 'module_task_gate', 'outcome': 'pass'}]
        flow.write_state(path, state)
        with self.assertRaises(flow.FlowError): flow.validate_migration(state, flow.load_json(self.graph))
        changed = flow.upgrade_recovery(path, self.graph, self.owner)
        self.assertEqual(changed['events'], state['events'])
        self.assertEqual(changed['tokens'], state['tokens'])
        self.assertEqual(changed['migrations'][-1]['from'], flow.graph_hash(old))
        self.assertEqual(flow.ready_nodes(changed, changed['graph_snapshot']), ['journal_task'])

    def test_upgrade_rejects_tampered_claimed_finished_and_other_delta(self):
        old = self.old_graph()
        state = flow.new_state(self.root, 'development', 'old', old)
        variants = []
        item = copy.deepcopy(state); item['status'] = 'complete'; variants.append(item)
        item = copy.deepcopy(state); item['claims'] = {'x': {'owner': self.owner}}; variants.append(item)
        item = copy.deepcopy(state); item['events'] = [{'node': 'journal_task', 'outcome': 'done'}]; variants.append(item)
        item = copy.deepcopy(state); item['graph_snapshot']['nodes']['journal_task']['locks'] = []; variants.append(item)
        item = copy.deepcopy(state); item['graph_sha256'] = 'wrong'; variants.append(item)
        path = self.root / 'historical.json'
        for item in variants:
            flow.write_state(path, item); before = path.read_bytes()
            with self.assertRaises(flow.FlowError): flow.upgrade_recovery(path, self.graph, self.owner)
            self.assertEqual(path.read_bytes(), before)
        candidate = flow.load_json(self.graph)
        candidate['nodes']['module_task_gate']['description'] += ' changed'
        wrong = self.root / 'wrong-graph.json'; wrong.write_text(json.dumps(candidate))
        flow.write_state(path, state); before = path.read_bytes()
        with self.assertRaises(flow.FlowError): flow.upgrade_recovery(path, wrong, self.owner)
        self.assertEqual(path.read_bytes(), before)
