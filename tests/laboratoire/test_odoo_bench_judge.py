from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import odoo_bench_judge as j


class JudgeTests(unittest.TestCase):
    def test_fabricated_quote_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'citation'):
            j.validate_grades({'A': {'c': {'grade': 'pass', 'quote': 'invented', 'reason': 'checked'}}}, {'A': 'actual answer'}, [{'id': 'c'}])

    def test_missing_criteria_and_extra_identity_are_rejected(self):
        for result in ({'A': {}}, {'A': {}, 'B': {}}):
            with self.assertRaises(ValueError): j.validate_grades(result, {'A': 'answer'}, [{'id': 'c'}])

    def test_absence_may_have_empty_quote_with_reason(self):
        j.validate_grades({'A': {'c': {'grade': 'fail', 'quote': '', 'reason': 'missing threshold'}}}, {'A': 'answer'}, [{'id': 'c'}])

    def test_resume_reuses_unchanged_review_without_provider_call(self):
        import json
        import tempfile
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / 'review'
            grades = {'A': {'c': {'grade': 'pass', 'quote': 'answer', 'reason': 'present'}}}
            event = {'type': 'result', 'subtype': 'success', 'result': json.dumps(grades)}
            cmd = [sys.executable, '-c', 'print(' + repr(json.dumps(event)) + ')']
            case = {'rubric': [{'id': 'c'}]}
            with patch.object(j.bench, 'isolated_command', return_value=cmd):
                j.evaluate(folder, case, {'A': 'answer'})
            with patch.object(j.subprocess, 'Popen', side_effect=AssertionError('no replay')):
                self.assertEqual(j.evaluate(folder, case, {'A': 'answer'}, resume=True), grades)
                with self.assertRaises(ValueError):
                    j.evaluate(folder, case, {'A': 'changed'}, resume=True)
