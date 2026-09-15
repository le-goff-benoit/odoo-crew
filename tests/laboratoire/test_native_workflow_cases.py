"""La calibration refuse faux positifs, erreurs runtime et mutations sans effet ciblé."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('native_workflow_calibration', ROOT / 'benchmarks/native/oracles/N06_calibrate.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class NativeWorkflowCalibrationTests(unittest.TestCase):
    def test_full_positive_and_targeted_negative(self):
        for identifier in ('N06', 'N07'):
            checks = dict.fromkeys(MODULE.REQUIRED_CHECKS[identifier], True)
            positive = {'exit_code': 0, 'passed': True, 'checks': checks}
            self.assertTrue(MODULE.calibrated(identifier, 'reference', positive))
            for label, _, expected in MODULE.variants(identifier):
                if expected:
                    continue
                mutant = {'exit_code': 0, 'passed': False, 'checks': dict(checks, **{MODULE.MUTATION_CHECKS[label]: False})}
                self.assertTrue(MODULE.calibrated(identifier, label, mutant))

    def test_empty_or_partial_oracle_never_calibrates(self):
        for checks in ({}, {'legacy_drafts_repaired': True}):
            self.assertFalse(MODULE.calibrated('N06', 'reference', {'exit_code': 0, 'passed': True, 'checks': checks}))

    def test_exception_is_not_a_successful_mutation(self):
        checks = dict.fromkeys(MODULE.REQUIRED_CHECKS['N07'], True)
        checks['copy_resets_operational_state'] = False
        self.assertFalse(MODULE.calibrated('N07', 'copy_inherits_state', {'exit_code': 1, 'passed': False, 'checks': checks}))

    def test_unrelated_failure_does_not_prove_target_sensitivity(self):
        checks = dict.fromkeys(MODULE.REQUIRED_CHECKS['N06'], True)
        checks['idempotent'] = False
        self.assertFalse(MODULE.calibrated('N06', 'issued_rewritten', {'exit_code': 0, 'passed': False, 'checks': checks}))


if __name__ == '__main__':
    unittest.main()
