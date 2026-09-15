import importlib.util
from pathlib import Path
import unittest
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from odoo_bench_implementation import immutable_inputs

CASES = Path(__file__).resolve().parents[2] / 'benchmarks/qualification/implementation'

def module(name):
    spec = importlib.util.spec_from_file_location(name, CASES / (name + '.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

class ImplementationOracleTests(unittest.TestCase):
    def test_positive_references(self):
        oracle, reference = module('oracle'), module('reference')
        self.assertTrue(oracle.judge(reference.ready, 'I01'))
        self.assertTrue(oracle.judge(reference.snapshot, 'I02'))

    def test_scheduler_mutations_are_killed(self):
        oracle, reference = module('oracle'), module('reference')
        mutants = [lambda tasks, locks: reference.ready(tasks, {}),
                   lambda tasks, locks: sorted(t['id'] for t in tasks if t['status'] == 'pending'),
                   lambda tasks, locks: []]
        for mutant in mutants:
            with self.assertRaises(AssertionError):
                oracle.judge(mutant, 'I01')

    def test_quota_mutations_are_killed(self):
        oracle, reference = module('oracle'), module('reference')
        def wrong_ttl(events, now, ttl=300):
            return reference.snapshot(events, now, ttl-1)
        def wrong_order(events, now, ttl=300):
            return reference.snapshot(list(reversed(events)), now, ttl)
        for mutant in (wrong_ttl, wrong_order):
            with self.assertRaises(AssertionError):
                oracle.judge(mutant, 'I02')


class ImmutableContractTests(unittest.TestCase):
    def test_prescribed_public_test_and_contract_must_not_change(self):
        original = CASES / 'I01/project'
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'project'
            shutil.copytree(original, target)
            self.assertTrue(immutable_inputs(target, original))
            (target / 'test_public.py').write_text('# tests removed\n')
            self.assertFalse(immutable_inputs(target, original))
            shutil.copy2(original / 'test_public.py', target / 'test_public.py')
            (target / 'CONTRACT.md').write_text('weaker contract')
            self.assertFalse(immutable_inputs(target, original))
