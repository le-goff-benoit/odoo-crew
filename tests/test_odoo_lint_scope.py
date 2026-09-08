from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LintScopeTests(unittest.TestCase):
    def test_missing_test_init_remains_error_with_changed_file_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            module = Path(tmp) / 'quality_lint'
            (module / 'tests').mkdir(parents=True)
            (module / '__manifest__.py').write_text("{'name': 'Fixture', 'version': '19.0.1.0.0', 'license': 'LGPL-3', 'depends': ['base']}\n")
            changed = module / '__init__.py'
            changed.write_text('')
            (module / 'tests/test_fixture.py').write_text('# A synthetic test file, intentionally not imported.\n')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/odoo_lint.py'), '--series', '19.0',
                                     '--only-files', str(changed), str(module)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('tests/__init__.py', result.stdout)
            self.assertIn('absent', result.stdout)
