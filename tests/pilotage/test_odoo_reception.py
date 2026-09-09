import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import odoo_flow as flow
import odoo_reception as reception
from odoo_coverage import GATES


class ReceptionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.graph = ROOT / 'workflows/odoo-workflow.json'
        self.owner = 'codex-orchestration'
        for name, text in {'request.md': 'Aucun frais de préparation ; jours multipliés par tarif.',
                           'spec.md': 'Le calcul conserve jours multipliés par tarif.',
                           'runtime.log': 'Le prêt de 2 jours à 10 vaut 20, sans frais de préparation.',
                           'project-draft.md': 'Le prêt conserve jours multipliés par tarif.',
                           'journal-draft.md': 'Calcul vérifié : 20 pour 2 jours à 10.',
                           'module/business.py': 'amount = days * rate',
                           '.odoo-agents/PROJECT.md': 'Ancienne compréhension.',
                           '.odoo-agents/JOURNAL.md': 'Intervention précédente.'}.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)

    def ready(self, gate='module_task_gate'):
        state = flow.new_state(self.root, 'development', gate, self.graph)
        state['start_pending'] = False
        state['tokens'] = {edge['id']: 1 for edge in flow.incoming_edges(state['graph_snapshot'], gate)}
        path = self.root / (gate + '.json')
        flow.write_state(path, state)
        flow.claim_node(path, self.graph, gate, self.owner)
        return path

    def prepare(self, path, name='bundle.json', owner=None, **kwargs):
        defaults = dict(sources=['request.md'], spec='spec.md', evidence=['runtime.log'],
                        memories=['.odoo-agents/PROJECT.md=project-draft.md',
                                  '.odoo-agents/JOURNAL.md=journal-draft.md'],
                        scopes=['module'], output=Path(name), owner=owner or self.owner)
        defaults.update(kwargs)
        return flow.prepare_reception(path, self.graph, **defaults)

    def receipt(self, pinned, name='review.log'):
        review = reception.draft(pinned['sha256'], 'codex-independent-tester')
        review['verdict'] = 'pass'
        groups = {'request_contract': ['request.md', 'spec.md'],
                  'contract_evidence': ['spec.md', 'runtime.log'],
                  'source_memory': ['request.md', 'project-draft.md', 'journal-draft.md']}
        bundle = json.loads((self.root / pinned['path']).read_text())
        groups['source_memory'].extend(row['base']['path'] for row in bundle['memory'] if row.get('base'))
        for axis, names in groups.items():
            review['checks'][axis] = {'status': 'pass', 'explanation': 'Portée conservée dans les passages cités.',
                                     'citations': [{'path': p, 'quote': (self.root / p).read_text()} for p in names]}
        output = self.root / name
        output.write_text(json.dumps(review))
        return output, review

    def finish(self, path, gate, proofs, outcome='pass'):
        return flow.complete_claimed_node(path, self.graph, gate, outcome, [str(p) for p in proofs], None, self.owner, False)

    def assert_rejected_unchanged(self, path, gate, proofs, outcome='pass'):
        before = path.read_bytes()
        registry = flow.registry_path(flow.load_json(path))
        before_registry = registry.read_bytes()
        with self.assertRaises(flow.FlowError):
            self.finish(path, gate, proofs, outcome)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(registry.read_bytes(), before_registry)

    def publish(self):
        for target, draft in [('PROJECT.md', 'project-draft.md'), ('JOURNAL.md', 'journal-draft.md')]:
            (self.root / '.odoo-agents' / target).write_bytes((self.root / draft).read_bytes())

    def test_three_gates_require_receipt_and_accept_independent_content_in_log(self):
        for gate in sorted(GATES):
            with self.subTest(gate=gate):
                path = self.ready(gate)
                pinned = self.prepare(path, gate + '-bundle.json')
                self.assert_rejected_unchanged(path, gate, [self.root / 'runtime.log'])
                review, _ = self.receipt(pinned, gate + '-review.log')
                state = self.finish(path, gate, [review])
                self.assertEqual(state['events'][-1]['outcome'], 'pass')
                self.assertEqual(state['accepted_reception']['path'], review.name)

    def test_negative_axes_self_review_forged_quotes_or_omission_never_pass(self):
        path = self.ready()
        review_path, review = self.receipt(self.prepare(path))
        variants = []
        for axis in reception.AXES:
            item = copy.deepcopy(review); item['checks'][axis]['status'] = 'fail'; variants.append(item)
        item = copy.deepcopy(review); item['mode'] = 'self'; variants.append(item)
        item = copy.deepcopy(review); item['reviewer'] = self.owner; variants.append(item)
        item = copy.deepcopy(review); item['verdict'] = 'revise'; variants.append(item)
        item = copy.deepcopy(review); item['checks']['request_contract']['citations'][0]['quote'] = 'GRATUIT'; variants.append(item)
        item = copy.deepcopy(review); item['checks']['request_contract']['citations'].pop(); variants.append(item)
        item = copy.deepcopy(review); item['checks'].pop('source_memory'); variants.append(item)
        item = copy.deepcopy(review); item['checks']['source_memory']['explanation'] = ''; variants.append(item)
        for item in variants:
            review_path.write_text(json.dumps(item))
            self.assert_rejected_unchanged(path, 'module_task_gate', [review_path])
        review_path.write_text(json.dumps(review))
        extra = self.root / 'duplicate.JSON'; extra.write_bytes(review_path.read_bytes())
        self.assert_rejected_unchanged(path, 'module_task_gate', [review_path, extra])

    def test_reception_spec_must_match_bound_coverage_before_preparation_or_pass(self):
        import odoo_coverage
        other = self.root / 'bound-spec.md'
        other.write_text("## Critères d'acceptation\n- [ ] Le prêt conserve jours multipliés par tarif.\n")
        for order in ('binding-first', 'reception-first'):
            with self.subTest(order=order):
                gate = 'module_task_gate' if order == 'binding-first' else 'module_high_gate'
                path = self.ready(gate)
                receipt = None
                if order == 'reception-first':
                    receipt, _ = self.receipt(self.prepare(path, gate + '-bundle.json'))
                coverage_path = self.root / (gate + '-coverage.json')
                contract = flow.bind_criteria(path, self.graph, other, coverage_path, self.owner)
                if order == 'binding-first':
                    before = path.read_bytes()
                    with self.assertRaisesRegex(flow.FlowError, 'différente du contrat'):
                        self.prepare(path, gate + '-bundle.json')
                    self.assertEqual(path.read_bytes(), before)
                    self.assertFalse((self.root / (gate + '-bundle.json')).exists())
                    flow.release_claim(path, self.graph, gate, self.owner, 'Fin de sous-cas synthétique')
                else:
                    coverage = odoo_coverage.draft(contract)
                    for row in coverage['criteria']:
                        row.update(status='covered', evidence=[reception.ref(self.root, 'runtime.log')])
                    coverage_path.write_text(json.dumps(coverage))
                    self.assert_rejected_unchanged(path, gate, [coverage_path, receipt])
                    # Repréparer avec la véritable spec liée permet la réception.
                    pinned = self.prepare(path, gate + '-fixed-bundle.json', spec='bound-spec.md')
                    receipt, review = self.receipt(pinned)
                    for axis in ('request_contract', 'contract_evidence'):
                        for citation in review['checks'][axis]['citations']:
                            if citation['path'] == 'spec.md':
                                citation.update(path='bound-spec.md', quote=other.read_text())
                    receipt.write_text(json.dumps(review))
                    self.finish(path, gate, [coverage_path, receipt])

    def test_new_completing_owner_cannot_receive_own_review(self):
        path = self.ready()
        review_path, review = self.receipt(self.prepare(path))
        flow.release_claim(path, self.graph, 'module_task_gate', self.owner, 'Transfert de responsabilité synthétique')
        self.owner = review['reviewer']
        flow.claim_node(path, self.graph, 'module_task_gate', self.owner)
        self.assert_rejected_unchanged(path, 'module_task_gate', [review_path])
        review['reviewer'] = 'codex-third-independent'
        review_path.write_text(json.dumps(review))
        self.finish(path, 'module_task_gate', [review_path])

    def test_check_bases_cli_is_read_only_and_refuses_concurrent_memory_change(self):
        path = self.ready(); review, _ = self.receipt(self.prepare(path))
        self.finish(path, 'module_task_gate', [review])
        flow.claim_node(path, self.graph, 'journal_task', self.owner)
        command = ['check-bases', str(self.root / 'bundle.json')]
        before = path.read_bytes()
        self.assertEqual(reception.main(command), 0)
        self.assertEqual(path.read_bytes(), before)
        target = self.root / '.odoo-agents/JOURNAL.md'
        target.write_text('Une autre tâche a ajouté son compte rendu.')
        with self.assertRaises(SystemExit) as error:
            reception.main(command)
        self.assertEqual(error.exception.code, 2)
        self.assertEqual(target.read_text(), 'Une autre tâche a ajouté son compte rendu.')
        self.assertEqual(path.read_bytes(), before)

    def test_every_frozen_group_code_and_old_memory_stays_fresh(self):
        path = self.ready()
        review, _ = self.receipt(self.prepare(path))
        for name in ['request.md', 'spec.md', 'runtime.log', 'project-draft.md', 'journal-draft.md',
                     'module/business.py', '.odoo-agents/PROJECT.md', '.odoo-agents/JOURNAL.md', 'bundle.json']:
            target = self.root / name
            original = target.read_bytes()
            target.write_bytes(original + b'\nchanged')
            with self.subTest(name=name):
                self.assert_rejected_unchanged(path, 'module_task_gate', [review])
            target.write_bytes(original)

    def test_new_code_file_is_detected(self):
        path = self.ready(); review, _ = self.receipt(self.prepare(path))
        (self.root / 'module/new.py').write_text('new = True')
        self.assert_rejected_unchanged(path, 'module_task_gate', [review])

    def test_exact_published_memory_required_at_journal_and_review_still_fresh(self):
        path = self.ready(); review, _ = self.receipt(self.prepare(path))
        self.finish(path, 'module_task_gate', [review])
        flow.claim_node(path, self.graph, 'journal_task', self.owner)
        self.assert_rejected_unchanged(path, 'journal_task', [self.root / 'runtime.log'], 'done')
        self.publish()
        for target in [review, self.root / 'request.md', self.root / '.odoo-agents/PROJECT.md', self.root / 'module/business.py']:
            original = target.read_bytes(); target.write_bytes(original + b'\nchanged')
            self.assert_rejected_unchanged(path, 'journal_task', [self.root / 'runtime.log'], 'done')
            target.write_bytes(original)
        state = self.finish(path, 'journal_task', [self.root / '.odoo-agents/JOURNAL.md'], 'done')
        self.assertEqual(state['events'][-1]['node'], 'journal_task')

    def test_absent_memory_can_be_created_only_after_qa(self):
        for name in reception.TARGETS:
            (self.root / name).unlink()
        path = self.ready(); review, _ = self.receipt(self.prepare(path))
        self.assertTrue(all(row['before_sha256'] is None for row in json.loads((self.root / 'bundle.json').read_text())['memory']))
        self.finish(path, 'module_task_gate', [review])
        flow.claim_node(path, self.graph, 'journal_task', self.owner)
        self.publish()
        self.finish(path, 'journal_task', [self.root / '.odoo-agents/JOURNAL.md'], 'done')

    def test_reprepare_keeps_history_and_does_not_allow_stale_receipt(self):
        path = self.ready(); old, _ = self.receipt(self.prepare(path))
        (self.root / 'project-draft.md').write_text('Le prêt est facturé sans préparation.')
        new_pin = self.prepare(path, 'bundle-v2.json')
        self.assertEqual(len(flow.load_json(path)['task_reception_history']), 1)
        self.assertTrue((self.root / 'bundle.json').exists())
        self.assert_rejected_unchanged(path, 'module_task_gate', [old])
        fresh, _ = self.receipt(new_pin, 'fresh.json')
        self.finish(path, 'module_task_gate', [fresh])
        with self.assertRaises(flow.FlowError): self.prepare(path, 'too-late.json')
        self.assertFalse((self.root / 'too-late.json').exists())

    def test_planned_task_enabled_with_recovery_graph(self):
        path = self.ready()
        state = flow.load_json(path)
        state['plan_task'] = {'release': str(self.root / 'changelog/release'), 'id': 'T01', 'risk': 'normal'}
        flow.write_state(path, state)
        review, _ = self.receipt(self.prepare(path))
        self.finish(path, 'module_task_gate', [review])
        flow.claim_node(path, self.graph, 'journal_task', self.owner)
        flow.publish_memory(path, self.graph, self.owner)
        self.finish(path, 'journal_task', [self.root / '.odoo-agents/JOURNAL.md'], 'done')

    def test_prepare_rejects_owner_aliases_missing_targets_and_overwrites(self):
        path = self.ready()
        invalid = [dict(owner='someone-else'), dict(memories=['.odoo-agents/PROJECT.md=project-draft.md']),
                   dict(memories=['.odoo-agents/PROJECT.md=spec.md', '.odoo-agents/JOURNAL.md=journal-draft.md']),
                   dict(memories=['.odoo-agents/PROJECT.md=project-draft.md', '.odoo-agents/JOURNAL.md=project-draft.md']),
                   dict(output=Path('spec.md')), dict(output=Path('module/bundle.json')),
                   dict(sources=['.odoo-agents/PROJECT.md']), dict(scopes=['.'])]
        for options in invalid:
            before = path.read_bytes()
            with self.subTest(options=options), self.assertRaises(flow.FlowError): self.prepare(path, **options)
            self.assertEqual(path.read_bytes(), before)
            self.assertFalse((self.root / 'bundle.json').exists())
        target = self.root / '.odoo-agents/PROJECT.md'; target.unlink(); target.symlink_to(self.root / 'request.md')
        with self.assertRaises(flow.FlowError): self.prepare(path)

    def test_legacy_and_failure_escape_do_not_require_review(self):
        for gate, bound, outcome in [('module_task_gate', False, 'pass'), ('module_high_gate', True, 'blocked'), ('studio_task_gate', True, 'retry')]:
            path = self.ready(gate)
            if bound:
                self.prepare(path, gate + '-bundle.json')
                (self.root / 'request.md').write_text('Changed after preparation')
            state = self.finish(path, gate, [self.root / 'runtime.log'], outcome)
            self.assertEqual(state['events'][-1]['outcome'], outcome)
            if outcome == 'blocked':
                flow.claim_node(path, self.graph, 'journal_task_blocked', self.owner)
                self.finish(path, 'journal_task_blocked', [self.root / 'runtime.log'], 'done')

    def test_nested_structured_evidence_checks_underlying_log_even_with_other_extension(self):
        import odoo_evidence
        proof = self.root / 'execution.json'
        odoo_evidence.execute(self.root, ['module'], proof, [sys.executable, '-c', 'print("ok")'])
        proof.rename(self.root / 'execution.receipt')
        path = self.ready()
        review, _ = self.receipt(self.prepare(path, evidence=['runtime.log', 'execution.receipt']))
        reception.verify(json.loads(review.read_text()), flow.load_json(path)['task_reception'], self.root)
        (self.root / 'execution.log').write_text('raw execution log changed')
        self.assert_rejected_unchanged(path, 'module_task_gate', [review])

    def test_cli_prepares_bundle_in_project_and_draft_never_claims_success(self):
        path = self.ready()
        self.assertEqual(flow.main(['--graph', str(self.graph), 'prepare-reception', str(path),
                                    '--source', 'request.md', '--spec', 'spec.md', '--evidence', 'runtime.log',
                                    '--memory', '.odoo-agents/PROJECT.md=project-draft.md',
                                    '--memory', '.odoo-agents/JOURNAL.md=journal-draft.md', '--scope', 'module',
                                    '--output', 'bundle.json', '--owner', self.owner]), 0)
        result = reception.draft(flow.load_json(path)['task_reception']['sha256'], 'tester')
        self.assertEqual(result['verdict'], 'blocked')
        self.assertTrue(all(row['status'] == 'fail' for row in result['checks'].values()))
