import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from odoo_models import resolve, codex_agent


class ModelPolicyTests(unittest.TestCase):
    def test_orchestrator_never_downgraded(self):
        for provider in ('codex', 'claude'):
            with self.assertRaises(ValueError):
                resolve(provider, 'orchestrator', 'normal', candidate=True)
            self.assertEqual(resolve(provider, 'orchestrator', principal='session-model')['requested_model'], 'session-model')

    def test_critical_roles_and_risks_retain_principal(self):
        for role in ('odoo-tester', 'odoo-analyst', 'odoo-developer'):
            with self.assertRaises(ValueError):
                resolve('codex', role, 'high', candidate=True)
        self.assertEqual(resolve('codex', 'odoo-developer', 'normal')['policy'], 'principal')

    def test_candidate_unavailable_does_not_fall_back_or_claim_observation(self):
        result = resolve('codex', 'odoo-developer', 'normal', candidate=True, available=['gpt-6-astra'])
        self.assertEqual(result['availability'], 'unavailable')
        self.assertEqual(result['requested_model'], 'gpt-5.6-terra')
        self.assertIsNone(result['observed_model'])
        self.assertEqual(result['policy'], 'experimental')

    @unittest.skipIf(sys.version_info < (3, 11), 'TOML parser standard à partir de Python 3.11')
    def test_native_profile_inherits_and_roundtrips_quoted_instruction(self):
        import tomllib
        data = tomllib.loads(codex_agent('test', 'description', 'a "quote"\nnext'))
        self.assertEqual(data['developer_instructions'], 'a "quote"\nnext')
        self.assertNotIn('model', data)
