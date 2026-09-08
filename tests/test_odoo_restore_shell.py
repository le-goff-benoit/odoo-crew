import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOCKER = '''#!/usr/bin/env python3
import os,sys
args=sys.argv[1:]
if 'shell' in args:
 sys.stdin.read()
 print('synthetic preparation')
 if os.environ.get('FAIL_STAGE')=='prepare': sys.exit(3)
if '-u' in args and 'odoo' in args and 'shell' not in args:
 print('Modules loaded')
 if os.environ.get('FAIL_STAGE')=='update': sys.exit(4)
'''


class RestoreShellTests(unittest.TestCase):
    def execute(self, failure):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ('scripts', 'stack', 'bin', 'enterprise'):
                (root / name).mkdir()
            for name in ('odoo-restore.sh', 'series-env.sh'):
                shutil.copy2(ROOT / 'scripts' / name, root / 'scripts' / name)
            docker = root / 'bin/docker'
            docker.write_text(DOCKER); docker.chmod(0o755)
            backup = root / 'synthetic.sql'; backup.write_text('-- synthetic empty dump\n')
            env = dict(os.environ, PATH=str(root / 'bin') + ':' + os.environ['PATH'],
                       ODOO_ENTERPRISE_DIR=str(root / 'enterprise'), FAIL_STAGE=failure)
            return subprocess.run(['bash', str(root / 'scripts/odoo-restore.sh'), str(backup),
                                   '--db', 'synthetic_test', '--series', '19.0', '--no-filestore', '--update', 'base'],
                                  capture_output=True, text=True, env=env, timeout=15)

    def test_failed_preparation_or_update_never_announces_ready(self):
        for failure in ('prepare', 'update'):
            with self.subTest(failure=failure):
                result = self.execute(failure)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertNotIn('Base synthetic_test prête', result.stdout)

    def test_success_with_unfiltered_output_is_ready(self):
        result = self.execute('')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Base synthetic_test prête', result.stdout)
