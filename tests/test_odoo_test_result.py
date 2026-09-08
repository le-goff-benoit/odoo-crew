import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('result', ROOT / 'scripts/odoo_test_result.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class ResultTests(unittest.TestCase):
    def test_no_summary_or_zero_tests_is_red(self):
        for text in ('mise à jour OK', 'odoo.tests.result: 0 failed, 0 error(s) of 0 tests'):
            self.assertFalse(r.inspect_log(text)['valid'])

    def test_dependency_tests_cannot_validate_target(self):
        text = 'odoo.tests.result: 0 failed, 0 error(s) of 8 tests\nodoo.tests.stats: base: 8 tests'
        self.assertFalse(r.inspect_log(text, 'quality_candidate')['valid'])

    def test_any_failed_stage_stays_red(self):
        text = 'odoo.tests.result: 1 failed, 0 error(s) of 2 tests\nodoo.tests.result: 0 failed, 0 error(s) of 2 tests'
        self.assertFalse(r.inspect_log(text)['valid'])

    def test_positive_target_tests(self):
        text = 'odoo.tests.result: 0 failed, 0 error(s) of 2 tests\nodoo.tests.stats: quality_candidate: 2 tests 1.2s 30 queries'
        self.assertTrue(r.inspect_log(text, 'quality_candidate')['valid'])
