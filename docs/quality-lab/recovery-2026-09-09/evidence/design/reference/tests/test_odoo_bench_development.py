from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from odoo_bench_development import extract


class ExtractionTests(unittest.TestCase):
    def test_preserves_code_exactly(self):
        self.assertEqual(extract('{"code":"# synthetic\\nvalue = 1\\n"}'), '# synthetic\nvalue = 1\n')

    def test_invalid_answer_is_not_repaired(self):
        for answer in ('not json', '{}', '{"code":"def broken("}', '{"code":12}', '{"code":"pass", "claim":"tested"}'):
            with self.subTest(answer=answer):
                with self.assertRaises((ValueError, SyntaxError)): extract(answer)
