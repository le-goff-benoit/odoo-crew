"""Asset declarations use the recursive glob semantics used by Odoo, including zero directories."""
import glob
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from odoo_delivery_guard import check_module

class AssetGlobTests(unittest.TestCase):
    def errors(self, pattern, files):
        entries = {'sample/__manifest__.py': {'mode': '100644', 'data': repr({'assets': {'web.assets_tests': [pattern]}}).encode()}}
        entries.update({name: {'mode': '100644', 'data': b''} for name in files})
        errors = []
        check_module(entries, 'sample', errors)
        return errors

    def test_recursive_glob_accepts_file_at_zero_directory_depth(self):
        self.assertEqual(self.errors('sample/static/tests/tours/**/*', ['sample/static/tests/tours/tour.js']), [])

    def test_recursive_glob_accepts_nested_file_and_rejects_absence(self):
        self.assertEqual(self.errors('sample/static/tests/tours/**/*.js', ['sample/static/tests/tours/nested/tour.js']), [])
        self.assertTrue(self.errors('sample/static/tests/tours/**/*.js', ['sample/static/tests/other/tour.js']))

    def test_same_result_as_odoo_stdlib_glob_on_reserved_patterns(self):
        files = ['sample/static/js/a.js', 'sample/static/js/nested/b.js', 'sample/static/js/nested/deeper/c.js', 'sample/static/js/.hidden.js', 'sample/static/js/.hidden/d.js', 'sample/static/css/a.css']
        patterns = ['sample/static/js/*.js', 'sample/static/js/**/*.js', 'sample/static/**/*.js', 'sample/static/js/?.js', 'sample/static/js/[ab].js', 'sample/static/js/missing/**/*.js', 'sample/static/js/.hidden.js', 'sample/static/js/**/absent.js']
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in files:
                p = root/name;p.parent.mkdir(parents=True, exist_ok=True);p.write_text('')
            for pattern in patterns:
                for name in files:
                    with self.subTest(pattern=pattern, file=name):
                        expected = str(root/name) in glob.glob(str(root/pattern), recursive=True)
                        self.assertEqual(not self.errors(pattern, [name]), expected)
