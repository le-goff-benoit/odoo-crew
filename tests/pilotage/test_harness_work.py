import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import odoo_plan as plan
import odoo_work as work
import odoo_evidence as evidence


class WorkTests(unittest.TestCase):
    def test_facade_preserves_reservations_and_refuses_unreceived_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); release = root / 'changelog/test'; release.mkdir(parents=True)
            (release / 'README.md').write_text('# Release')
            (root / 'request.md').write_text('Demande originale')
            (root / 'code.py').write_text('result = 1')
            plan.initialise(release, {'schema': 1, 'tasks': [{'id': 'T1', 'title': 'Résultat', 'request': 'request.md',
                'route': 'module', 'risk': 'normal', 'acceptance': ['résultat = 1'], 'scopes': ['code.py'], 'depends_on': []}]})
            self.assertTrue(work.status(root, 'test', 'T1')['tasks'][0]['ready'])
            import odoo_effort as effort
            effort.init(release)
            effort.estimate(release, {'lines': [{'task':'T1','agent':'odoo-developer','optimistic_minutes':1,
                'likely_minutes':2,'pessimistic_minutes':3,'basis':'Synthetic','confidence':'low','assumptions':['Local copy']},
                {'task':'RELEASE','title':'Livraison','agent':'orchestrator','optimistic_minutes':1,'likely_minutes':2,'pessimistic_minutes':3,
                 'basis':'Synthetic','confidence':'low','assumptions':['Local copy']}]})
            command = [sys.executable, work.__file__]
            first = subprocess.run(command + ['start', str(root), '--release', 'test', '--task', 'T1'], capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertTrue(Path(first.stdout.strip()).is_file())
            second = subprocess.run(command + ['start', str(root), '--release', 'test', '--task', 'T1'], capture_output=True)
            self.assertNotEqual(second.returncode, 0)
            receipt = subprocess.run(command + ['receive', str(root), '--release', 'test', '--task', 'T1'], capture_output=True)
            self.assertNotEqual(receipt.returncode, 0)
            self.assertFalse(work.status(root, 'test', 'T1')['tasks'][0]['ready'])
            with self.assertRaises(ValueError): work.status(root, 'test', 'unknown')
            proof = root / 'proof.json'
            evidence.execute(root, ['code.py'], proof, [sys.executable, '-c', 'print(1)'], environment={'database': 'synthetic'})
            env = root / 'environment.json'; env.write_text('{"database":"synthetic"}')
            args = command + ['preflight', str(root), '--proof', 'proof.json', '--environment', str(env)]
            self.assertEqual(subprocess.run(args, capture_output=True).returncode, 0)
            env.write_text('{"database":"changed"}')
            self.assertNotEqual(subprocess.run(args, capture_output=True).returncode, 0)
