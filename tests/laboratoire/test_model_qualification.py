import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('model_qualification', ROOT / 'benchmarks/qualification/models/run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class ModelOracleTests(unittest.TestCase):
    def test_correct_references_and_every_critical_mutation(self):
        for case, expected in runner.EXPECTED.items():
            self.assertTrue(runner.judge(json.dumps(expected), case))
            for key, value in expected.items():
                mutant = dict(expected)
                mutant[key] = not value if isinstance(value, bool) else ['wrong'] if isinstance(value, list) else 'wrong'
                with self.subTest(case=case, key=key):
                    self.assertFalse(runner.judge(json.dumps(mutant), case))
            self.assertFalse(runner.judge('{}', case))
            self.assertFalse(runner.judge('pas un résultat', case))
