"""Offline oracle calibration; this suite never starts a provider."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import odoo_bench_profiles as bench


class ProfileOracleTests(unittest.TestCase):
    def setUp(self):
        self.oracle = json.loads((bench.CORPUS / 'oracles.json').read_text())

    def example(self, case):
        expected = self.oracle[case]
        inputs = {p.name: p.read_text() for p in (bench.CORPUS / 'cases' / case / 'input').glob('*.md')}
        result = {k: deepcopy(v) for k, v in expected.items() if k != 'semantic_requirements'}
        result['limitations'] = 'Dossier documentaire, résultat local uniquement.'
        pairs = {'request_contract': ('demande.md', 'contrat.md'),
                 'contract_evidence': ('contrat.md', 'preuves.md'),
                 'source_memory': ('memoire-base.md', 'memoire-draft.md')}
        result['findings'] = [{'axis': axis, 'explanation': 'Explication témoin à soumettre à réception sémantique.',
                               'references': [{'file': name, 'quote': inputs[name]} for name in names]}
                              for axis, names in pairs.items()]
        return result, inputs

    def test_reference_facts_pass_and_every_critical_mutation_fails(self):
        for case in ('positive', 'holdout'):
            result, inputs = self.example(case)
            self.assertEqual(bench.judge(result, self.oracle[case], inputs), [])
            for key in ('decision', 'axes', 'local_scope_received', 'deployment_verified', 'prior_memory_preserved', 'preserved_observations'):
                value = deepcopy(result)
                value[key] = not value[key] if isinstance(value[key], bool) else [] if isinstance(value[key], list) else 'wrong'
                with self.subTest(case=case, key=key):
                    self.assertTrue(bench.judge(value, self.oracle[case], inputs))

    def test_words_without_grounded_comparison_do_not_pass(self):
        result, inputs = self.example('holdout')
        result['findings'] = [{'axis': 'request_contract', 'explanation': 'Exception prêt production conflit mémoire refusé',
                               'references': [{'file': 'demande.md', 'quote': 'citation inventée'}]}]
        self.assertTrue(bench.judge(result, self.oracle['holdout'], inputs))
        self.assertTrue(bench.judge(None, self.oracle['holdout'], inputs))

    def test_native_output_audit_detects_truncation_in_both_providers(self):
        with tempfile.TemporaryDirectory() as folder:
            raw = Path(folder) / 'raw.jsonl'
            text = 'Règle complète : location facturée, sauf prêt prolongé.\n'
            reads = [{'path': 'rule', 'sha256': bench.digest(text.encode())}]
            for event in [
                {'type': 'item.completed', 'item': {'type': 'command_execution', 'aggregated_output': text}},
                {'type': 'user', 'message': {'content': [{'type': 'tool_result', 'content': text.strip()}]}},
            ]:
                raw.write_text(json.dumps(event))
                self.assertTrue(bench.audit_read_outputs(raw, reads, {'rule': text})[0]['full_text_in_native_tool_result'])
            raw.write_text(json.dumps({'type': 'item.completed', 'item': {'type': 'command_execution', 'aggregated_output': text[:20]}}))
            self.assertFalse(bench.audit_read_outputs(raw, reads, {'rule': text})[0]['full_text_in_native_tool_result'])

    def test_snapshot_refuses_symbolic_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ('roles', 'scripts', 'docs', 'workflows', 'tests', 'benchmarks'):
                (root / name).mkdir()
            (root / 'docs/external').symlink_to(root / 'outside')
            with self.assertRaisesRegex(ValueError, 'symbolique'):
                bench.snapshot_candidate(root, root / 'snapshot')

    def test_reader_refuses_oracles_and_traversal(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ('home', 'work/input', 'pack/docs'):
                (root / name).mkdir(parents=True)
            (root / 'work/input/demande.md').write_text('demande synthétique')
            server = bench.SourceServer(str(root / 's'), root/'home', root/'work', root/'pack', root/'reads')
            try:
                self.assertEqual(server.read_source('/work/input/demande.md'), 'demande synthétique')
                for name in ('/work/input/../../oracles.json', str(bench.CORPUS/'oracles.json'), '~/.codex/auth.json'):
                    with self.assertRaises(ValueError): server.read_source(name)
            finally:
                server.server_close()


if __name__ == '__main__':
    unittest.main()
