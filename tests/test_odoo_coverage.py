import copy
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import odoo_coverage as coverage
import odoo_flow as flow


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.spec = self.root / 'spec.md'
        self.spec.write_text("## 8. Critères d'acceptation\n- [ ] **A1** — Zéro permis.\n- [ ] **A8** — Message reçu par l'utilisateur,\n      et aucune ancienne contrainte.\n\n## Hors contrat\nAucun PDF.\n")
        self.pinned = coverage.contract(self.root, self.spec)
        self.proof = self.root / 'runtime.log'
        self.proof.write_text('Scénarios synthétiques exécutés : zéro accepté, message reçu, code relu.')
        self.receipt = coverage.draft(self.pinned)
        for row in self.receipt['criteria']:
            row.update(status='covered', evidence=[{'path': 'runtime.log', 'sha256': hashlib.sha256(self.proof.read_bytes()).hexdigest()}])

    def test_complete_contract_preserves_multiline_and_excludes_outside(self):
        self.assertEqual(len(self.pinned['criteria']), 2)
        self.assertIn("Message reçu par l'utilisateur,\n      et", self.pinned['criteria'][1]['text'])
        coverage.verify(self.receipt, self.pinned, self.root)
        self.assertEqual([r['status'] for r in coverage.draft(self.pinned)['criteria']], ['missing', 'missing'])

    def test_partial_omitted_rewritten_added_or_reordered_never_pass(self):
        mutations = []
        partial = copy.deepcopy(self.receipt); partial['criteria'][1]['status'] = 'partial'; mutations.append(partial)
        omitted = copy.deepcopy(self.receipt); omitted['criteria'].pop(); mutations.append(omitted)
        rewritten = copy.deepcopy(self.receipt); rewritten['criteria'][1]['text'] = 'Message présent dans le code'; mutations.append(rewritten)
        added = copy.deepcopy(self.receipt); added['criteria'].append(added['criteria'][0]); mutations.append(added)
        reordered = copy.deepcopy(self.receipt); reordered['criteria'].reverse(); mutations.append(reordered)
        for proof in mutations:
            with self.subTest(proof=proof), self.assertRaises(ValueError):
                coverage.verify(proof, self.pinned, self.root)

    def test_changed_source_or_evidence_and_empty_proof_rejected(self):
        self.proof.write_text('Autre exécution')
        with self.assertRaisesRegex(ValueError, 'preuve modifiée'): coverage.verify(self.receipt, self.pinned, self.root)
        self.spec.write_text(self.spec.read_text().replace('Zéro permis', 'Zéro interdit'))
        with self.assertRaisesRegex(ValueError, 'spécification modifiée'): coverage.verify(self.receipt, self.pinned, self.root)

    def test_uninterpretable_or_duplicate_criteria_fail_closed(self):
        for text in ["## Critères d'acceptation\n| Critère | État |\n", "## Critères d'acceptation\n", "## Critères d'acceptation\n- [ ] **A1** — x\n- [ ] **A1** — y\n", "## Critères d'acceptation\n- [ ] x\nTexte non indenté\n"]:
            self.spec.write_text(text)
            with self.subTest(text=text), self.assertRaises(ValueError): coverage.contract(self.root, self.spec)

    def test_nested_execution_proof_keeps_code_freshness_check(self):
        import odoo_evidence
        code = self.root / 'module'; code.mkdir(); (code / 'main.py').write_text('x=1')
        execution = self.root / 'execution.json'
        odoo_evidence.execute(self.root, ['module'], execution, [sys.executable, '-c', 'print("ok")'])
        for row in self.receipt['criteria']:
            row['evidence'] = [{'path': 'execution.json', 'sha256': hashlib.sha256(execution.read_bytes()).hexdigest()}]
        coverage.verify(self.receipt, self.pinned, self.root)
        (code / 'main.py').write_text('x=2')
        with self.assertRaisesRegex(ValueError, 'code changé'): coverage.verify(self.receipt, self.pinned, self.root)

    def ready_gate(self, gate):
        graph_path = ROOT / 'workflows/odoo-workflow.json'
        state = flow.new_state(self.root, 'development', gate, graph_path)
        state['start_pending'] = False
        graph = state['graph_snapshot']
        state['tokens'] = {edge['id']: 1 for edge in flow.incoming_edges(graph, gate)}
        path = self.root / f'{gate}.json'
        flow.write_state(path, state)
        flow.claim_node(path, graph_path, gate, 'codex-qa')
        return path, graph_path

    def finish(self, path, graph_path, gate, evidence, outcome='pass', owner='codex-qa'):
        return flow.complete_claimed_node(path, graph_path, gate, outcome, [str(e) for e in evidence], None, owner, False)

    def test_each_bound_gate_rejects_missing_partial_without_releasing_claim(self):
        for gate in sorted(coverage.GATES):
            with self.subTest(gate=gate):
                path, graph = self.ready_gate(gate)
                output = self.root / f'{gate}-coverage.json'
                flow.bind_criteria(path, graph, self.spec, output, 'codex-qa')
                before = path.read_bytes()
                registry = flow.registry_path(flow.load_json(path)); locks = registry.read_bytes()
                for evidence in ([self.proof], [output]):
                    with self.assertRaises(flow.FlowError): self.finish(path, graph, gate, evidence)
                    self.assertEqual(path.read_bytes(), before)
                    self.assertEqual(registry.read_bytes(), locks)
                output.write_text(json.dumps(self.receipt))
                result = self.finish(path, graph, gate, [self.proof, output])
                self.assertEqual(result['events'][-1]['outcome'], 'pass')
                self.assertNotIn(gate, result['claims'])

    def test_legacy_flow_and_bound_blocked_remain_available(self):
        for gate, bind, outcome in [('module_task_gate', False, 'pass'), ('module_high_gate', True, 'blocked'), ('studio_task_gate', True, 'retry')]:
            path, graph = self.ready_gate(gate)
            if bind: flow.bind_criteria(path, graph, self.spec, self.root / f'{gate}-coverage.json', 'codex-qa')
            self.assertEqual(self.finish(path, graph, gate, [self.proof], outcome)['events'][-1]['outcome'], outcome)

    def test_binding_cannot_replace_contract_or_cross_owners(self):
        path, graph = self.ready_gate('module_high_gate')
        before = path.read_bytes()
        with self.assertRaises(flow.FlowError): flow.bind_criteria(path, graph, self.spec, self.root / 'bad.json', 'other')
        self.assertEqual(path.read_bytes(), before)
        flow.bind_criteria(path, graph, self.spec, self.root / 'coverage.json', 'codex-qa')
        before = path.read_bytes()
        self.spec.write_text(self.spec.read_text().replace('Zéro permis', 'Zéro interdit'))
        with self.assertRaises(flow.FlowError): flow.bind_criteria(path, graph, self.spec, self.root / 'new.json', 'codex-qa')
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse((self.root / 'new.json').exists())

    def test_execution_freshness_does_not_depend_on_filename(self):
        import odoo_evidence
        code = self.root / 'module'; code.mkdir(); (code / 'main.py').write_text('x=1')
        execution = self.root / 'execution.json'
        odoo_evidence.execute(self.root, ['module'], execution, [sys.executable, '-c', 'print("ok")'])
        (code / 'main.py').write_text('x=2')
        for name in ['receipt.log', 'receipt.JSON']:
            renamed = self.root / name; renamed.write_bytes(execution.read_bytes())
            for row in self.receipt['criteria']:
                row['evidence'] = [{'path': name, 'sha256': hashlib.sha256(renamed.read_bytes()).hexdigest()}]
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'code changé'):
                coverage.verify(self.receipt, self.pinned, self.root)

    def test_same_binding_is_repeatable_but_cannot_be_added_after_pass(self):
        path, graph = self.ready_gate('module_high_gate')
        first = self.root / 'first.json'; second = self.root / 'second.json'
        flow.bind_criteria(path, graph, self.spec, first, 'codex-qa')
        bound = flow.load_json(path)['qa_contract_binding']
        flow.bind_criteria(path, graph, self.spec, second, 'codex-qa')
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertEqual(flow.load_json(path)['qa_contract_binding'], bound)
        first.write_text(json.dumps(self.receipt))
        self.finish(path, graph, 'module_high_gate', [first])
        with self.assertRaises(flow.FlowError): flow.bind_criteria(path, graph, self.spec, self.root / 'third.json', 'codex-qa')

    def test_two_completions_of_bound_gate_record_one_pass(self):
        path, graph = self.ready_gate('module_high_gate')
        output = self.root / 'coverage.json'
        flow.bind_criteria(path, graph, self.spec, output, 'codex-qa')
        output.write_text(json.dumps(self.receipt))
        def complete(_):
            try:
                self.finish(path, graph, 'module_high_gate', [output])
                return True
            except flow.FlowError:
                return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sorted(pool.map(complete, range(2))), [False, True])
        self.assertEqual(len(flow.load_json(path)['events']), 1)
