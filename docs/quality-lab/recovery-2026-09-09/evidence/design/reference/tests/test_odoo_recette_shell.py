import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RecetteShellTests(unittest.TestCase):
    def execute(self, args):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ('scripts', 'stack', 'addons/synthetic', 'enterprise'):
                (root / name).mkdir(parents=True)
            for name in ('odoo-recette.sh', 'series-env.sh', 'odoo_test_result.py'):
                shutil.copy2(ROOT / 'scripts' / name, root / 'scripts' / name)
            (root / 'addons/synthetic/__manifest__.py').write_text("{'version': '19.0.1.0.0'}")
            log = root / 'tests.log'
            log.write_text('odoo.tests.result: 0 failed, 0 error(s) of 2 tests\nodoo.tests.stats: synthetic: 2 tests\n')
            for name, body in {
                'odoo-lint.sh': 'echo "0 erreur"',
                'odoo-test.sh': f'echo "Log complet : {log}"\necho "✅ installation OK"\necho "✅ mise à jour OK"\necho "✅ tests OK"\necho "✅ désinstallation OK"\necho "RECETTE synthetic db=synthetic_test tests=1s"',
            }.items():
                script = root / 'scripts' / name
                script.write_text('#!/bin/bash\n' + body + '\n'); script.chmod(0o755)
            env = dict(os.environ, ODOO_ADDONS_DIR=str(root / 'addons'), ODOO_ENTERPRISE_DIR=str(root / 'enterprise'), ODOO_SERIES='19.0')
            return subprocess.run(['bash', str(root / 'scripts/odoo-recette.sh'), 'synthetic', *args],
                                  capture_output=True, text=True, env=env, timeout=15)

    def test_missing_copy_cannot_be_green(self):
        result = self.execute([])
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('aucune copie fournie', result.stdout)

    def test_explicit_normal_waiver_is_visible(self):
        result = self.execute(['--without-client-copy', 'fixture synthétique sans historique'])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('dispensée explicitement', result.stdout)

    def test_high_risk_refuses_waiver(self):
        result = self.execute(['--risk', 'high', '--without-client-copy', 'aucune sauvegarde'])
        self.assertEqual(result.returncode, 2)
        self.assertIn('dispense refusée', result.stderr)
