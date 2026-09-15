from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import odoo_evidence as e


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'module').mkdir()
        self.code = self.root / 'module/model.py'
        self.code.write_text('value = 1\n')

    def run_proof(self, code='print("checked")'):
        return e.execute(self.root, ['module'], self.root / ('proof' + str(len(list(self.root.glob('proof*.json')))) + '.json'), [sys.executable, '-c', code])

    def test_changed_code_or_new_file_invalidates_proof(self):
        proof = self.run_proof()
        e.verify(proof)
        (self.root / 'module/new.py').write_text('added = True')
        with self.assertRaisesRegex(ValueError, 'code changé'): e.verify(proof)

    def test_changes_during_execution_are_not_a_success(self):
        proof = self.run_proof("from pathlib import Path; Path('module/model.py').write_text('changed')")
        self.assertEqual(proof['result'], 'failed')
        with self.assertRaises(ValueError): e.verify(proof)

    def test_changed_log_or_failed_exit_cannot_be_validated(self):
        proof = self.run_proof()
        Path(proof['log']['path']).write_text('altered log')
        with self.assertRaisesRegex(ValueError, 'log changé'): e.verify(proof)
        proof = self.run_proof('raise SystemExit(1)')
        with self.assertRaises(ValueError): e.verify(proof)

    def test_bytecode_does_not_invalidate_code_proof(self):
        proof = self.run_proof()
        cache = self.root / 'module/__pycache__'; cache.mkdir()
        (cache / 'model.pyc').write_bytes(b'cache')
        e.verify(proof)

    def test_proof_of_other_project_is_refused(self):
        proof = self.run_proof()
        with self.assertRaises(ValueError): e.verify(proof, '/other/project')

    def test_deleted_scope_during_control_records_failed_proof(self):
        proof = self.run_proof("import shutil; shutil.rmtree('module')")
        self.assertEqual(proof['result'], 'failed')
        self.assertTrue((self.root / 'proof0.json').is_file())

    def test_timeout_is_not_a_success(self):
        proof = e.execute(self.root, ['module'], self.root / 'proof.json',
                          [sys.executable, '-c', 'import time; time.sleep(30)'], timeout=0.1)
        self.assertEqual(proof['result'], 'failed')
        self.assertEqual(proof['error'], 'TimeoutExpired')

    def test_failed_proof_is_valid_evidence_of_failure_only(self):
        proof = self.run_proof('raise SystemExit(1)')
        e.verify(proof, require_success=False)
        with self.assertRaises(ValueError): e.verify(proof)

    def test_environment_unknown_or_changed_is_not_compatible(self):
        proof = self.run_proof()
        with self.assertRaisesRegex(ValueError, 'environnement'):
            e.verify(proof, expected_environment='odoo-image-v1:neutralized-snapshot-1')
        proof = e.execute(self.root, ['module'], self.root / 'environment-proof.json',
                          [sys.executable, '-c', 'print("checked")'], environment='image-v1:data-v1')
        e.verify(proof, expected_environment='image-v1:data-v1')
        with self.assertRaisesRegex(ValueError, 'environnement'):
            e.verify(proof, expected_environment='image-v2:data-v1')
