"""Exécuter le vrai script QA contre une frontière Docker simulée, sans base réelle."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOCKER = '''#!/usr/bin/env python3
import os,sys,json
args=sys.argv[1:]
with open(os.environ['CALLS'],'a') as stream: stream.write(json.dumps(args)+'\\n')
if 'ps' in args: print('db running')
elif 'psql' in args:
 q=args[-1]
 if 'pg_database' in q: print('1')
 elif 'to_regclass' in q: print(os.environ.get('TABLE_PRESENT','t'))
 elif 'SELECT state' in q: print(os.environ.get('MODULE_STATE','uninstalled'))
elif 'run' in args:
 n=os.environ.get('TEST_COUNT','1')
 print('odoo.tests.result: 0 failed, 0 error(s) of '+n+' tests')
 print('odoo.tests.stats: quality_stub: '+n+' tests 0.1s 10 queries')
'''


class ShellTests(unittest.TestCase):
    def execute(self, **settings):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ('scripts', 'stack', 'bin', 'addons', 'enterprise'):
                (root / name).mkdir()
            for name in ('odoo-test.sh', 'series-env.sh', 'odoo_test_result.py'):
                shutil.copy2(ROOT / 'scripts' / name, root / 'scripts' / name)
            docker = root / 'bin/docker'
            docker.write_text(DOCKER)
            docker.chmod(0o755)
            env = dict(os.environ, PATH=str(root / 'bin') + ':' + os.environ['PATH'],
                       ODOO_SERIES='19.0', ODOO_TEST_DB='quality_stub_db', ODOO_TEST_DB_EXPLICIT='1',
                       ODOO_ADDONS_DIR=str(root / 'addons'), ODOO_ENTERPRISE_DIR=str(root / 'enterprise'),
                       CALLS=str(root / 'calls.jsonl'), XDG_CACHE_HOME=str(root / 'cache'), **settings)
            result = subprocess.run(['bash', str(root / 'scripts/odoo-test.sh'), 'quality_stub', '--quick'],
                                    env=env, capture_output=True, text=True, timeout=15)
            calls = [json.loads(line) for line in (root / 'calls.jsonl').read_text().splitlines()]
            return result, calls

    def test_existing_empty_database_installs(self):
        result, calls = self.execute(TABLE_PRESENT='f')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        run = next(c for c in calls if 'run' in c)
        self.assertIn('-i', run)
        self.assertNotIn('-u', run)
        self.assertFalse(any('stop' in c for c in calls), 'existing PostgreSQL must remain running')

    def test_existing_uninstalled_module_installs(self):
        result, calls = self.execute(MODULE_STATE='uninstalled')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('-i', next(c for c in calls if 'run' in c))

    def test_installed_module_updates(self):
        result, calls = self.execute(MODULE_STATE='installed')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('-u', next(c for c in calls if 'run' in c))

    def test_successful_process_with_zero_tests_is_failure(self):
        result, _ = self.execute(TEST_COUNT='0')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('preuve de tests absente ou invalide', result.stdout)
