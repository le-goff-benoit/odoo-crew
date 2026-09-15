import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from odoo_delivery_guard import digest, prepare, evaluate
from odoo_evidence import execute


class DeliveryGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.email', 'synthetic@example.invalid')
        self.git('config', 'user.name', 'Synthetic')
        self.put('sample/__manifest__.py', "{'name': 'Sample', 'version': '19.0.1.0.0', 'data': []}")
        self.put('sample/__init__.py', 'from . import models\n')
        self.put('sample/models/__init__.py', 'from . import item\n')
        self.put('sample/models/item.py', 'from odoo import models, fields\nclass Item(models.Model):\n    name = fields.Char()\n')
        self.base = self.commit()
        self.put('sample/__manifest__.py', "{'name': 'Sample', 'version': '19.0.1.1.0', 'data': []}")
        self.target = self.commit()
        # A synthetic command verifies bytes; it does not pretend to execute Odoo.
        self.command = [sys.executable, '-c', "from pathlib import Path; assert '19.0.1.1.0' in Path('sample/__manifest__.py').read_text(); print('synthetic build')"]

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], stderr=subprocess.DEVNULL).decode().strip()

    def put(self, path, text):
        dest = self.repo / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')
        return self.git('rev-parse', 'HEAD')

    def contract(self):
        return prepare(self.repo, self.base, self.target, ['sample'], self.command,
                       'synthetic-build-v1', 'synthetic-target-v1', {'column_present': True})

    def reference(self, path):
        return {'path': str(path), 'sha256': digest(path.read_bytes())}

    def build(self):
        path = self.root / 'build.json'
        execute(self.repo, ['sample'], path, self.command, environment='synthetic-build-v1')
        return self.reference(path)

    def observation(self, contract):
        before_path = self.root / 'before.json'
        before_path.write_text(json.dumps({'format': 'odoo-deployment-baseline/1', 'commit': self.base,
                                          'target_environment': 'synthetic-target-v1',
                                          'observed_at': datetime.now(timezone.utc).isoformat(),
                                          'installed_modules': {'sample': {'version': '19.0.1.0.0', 'state': 'installed'}}}))
        effect_path = self.root / 'effect.json'
        effect_path.write_text(json.dumps({'target_environment': 'synthetic-target-v1', 'commit': self.target,
                                          'effect': 'column_present', 'actual': True}))
        capture = {'format': 'odoo-deployment-observation/1', 'commit': self.target,
                   'before': self.reference(before_path),
                   'target_environment': 'synthetic-target-v1', 'build_id': 'scratch-42', 'build_status': 'success',
                   'observed_at': datetime.now(timezone.utc).isoformat(),
                   'installed_modules': {'sample': {'version': '19.0.1.1.0', 'state': 'installed'}},
                   'effects': {'column_present': {'passed': True, 'read_command': ['synthetic-read'],
                                                  'actual': True, 'source': self.reference(effect_path)}}}
        return capture

    def test_ready_is_not_deployed_and_sourced_read_closes_contract(self):
        contract, proof = self.contract(), self.build()
        self.assertEqual(evaluate(contract, proof)['status'], 'ready_to_deliver')
        path = self.root / 'deployment.json'
        path.write_text(json.dumps(self.observation(contract)))
        self.assertEqual(evaluate(contract, proof, self.reference(path))['status'], 'deployed_verified')

    def test_actual_previous_version_required_not_just_git_base(self):
        contract, proof = self.contract(), self.build()
        capture = self.observation(contract)
        path = self.root / 'deployment.json'
        del capture['before']
        path.write_text(json.dumps(capture))
        with self.assertRaisesRegex(ValueError, 'non sourcée'):
            evaluate(contract, proof, self.reference(path))
        capture = self.observation(contract)
        before = self.root / 'before.json'
        data = json.loads(before.read_text())
        data['installed_modules']['sample']['version'] = '19.0.0.9.0'
        before.write_text(json.dumps(data))
        capture['before'] = self.reference(before)
        path.write_text(json.dumps(capture))
        with self.assertRaisesRegex(ValueError, 'avant livraison différente'):
            evaluate(contract, proof, self.reference(path))

    def test_relative_module_paths_normalize_shell_completion(self):
        for name in ['sample/', './sample']:
            contract = prepare(self.repo, self.base, self.target, [name], self.command,
                               'synthetic-build-v1', 'synthetic-target-v1', {'column_present': True})
            self.assertEqual(contract['errors'], [])
            self.assertEqual(contract['modules']['sample']['path'], 'sample')

    def test_untracked_import_is_missing_from_exact_commit(self):
        self.put('sample/__init__.py', 'from . import models, extra\n')
        self.target = self.commit()
        self.put('sample/extra.py', '# deliberately untracked\n')
        self.assertTrue(any('import local absent' in x for x in self.contract()['errors']))

    def test_submodule_inside_module_is_not_silently_excluded(self):
        self.git('update-index', '--add', '--cacheinfo', '160000,' + self.base + ',sample/vendor')
        self.git('commit', '-qm', 'synthetic gitlink')
        self.target = self.git('rev-parse', 'HEAD')
        self.assertTrue(any('non régulier : sample/vendor' in error for error in self.contract()['errors']))

    def test_manifest_missing_file_blocks_delivery(self):
        self.put('sample/__manifest__.py', "{'version': '19.0.1.1.0', 'data': ['views/missing.xml']}")
        self.target = self.commit()
        self.assertTrue(any('fichier déclaré absent' in x for x in self.contract()['errors']))

    def test_schema_change_without_version_bump(self):
        self.put('sample/__manifest__.py', "{'version': '19.0.1.0.0'}")
        self.put('sample/models/item.py', 'from odoo import fields\nclass Item:\n    name = fields.Char()\n    active = fields.Boolean(store=True)\n')
        self.target = self.commit()
        self.assertTrue(any('schéma sans hausse' in x for x in self.contract()['errors']))

    def test_migration_must_be_in_target_range_and_have_entrypoint(self):
        for directory, body, fragment in [('19.0.1.0.0', 'def migrate(cr, version): pass', 'hors plage'),
                                           ('19.0.2.0.0', 'def migrate(cr, version): pass', 'hors plage'),
                                           ('19.0.1.1.0', '# no function', 'migrate absente')]:
            with self.subTest(directory=directory):
                self.put('sample/migrations/' + directory + '/post-check.py', body)
                self.target = self.commit()
                self.assertTrue(any(fragment in x for x in self.contract()['errors']))

    def test_valid_migration_and_old_unchanged_history(self):
        self.put('sample/migrations/19.0.1.1.0/post-check.py', 'def migrate(cr, version): pass\n')
        self.target = self.commit()
        self.assertEqual(self.contract()['errors'], [])

    def test_migration_file_presence_does_not_prove_execution(self):
        migration = 'sample/migrations/19.0.1.1.0/post-check.py'
        self.put(migration, 'def migrate(cr, version): pass\n')
        self.target = self.commit()
        contract, proof = self.contract(), self.build()
        capture = self.observation(contract)
        path = self.root / 'deployment.json'
        path.write_text(json.dumps(capture))
        with self.assertRaisesRegex(ValueError, 'non sourcée'):
            evaluate(contract, proof, self.reference(path))
        run = self.root / 'migration.json'
        run.write_text(json.dumps({'commit': self.target, 'target_environment': 'synthetic-target-v1',
                                   'migration': migration, 'executed': True}))
        capture['migrations'] = {migration: self.reference(run)}
        path.write_text(json.dumps(capture))
        self.assertEqual(evaluate(contract, proof, self.reference(path))['status'], 'deployed_verified')

    def test_unchanged_migration_in_version_range_still_requires_execution(self):
        migration = 'sample/migrations/19.0.1.1.0/post-check.py'
        self.put('sample/__manifest__.py', "{'version': '19.0.1.0.0'}")
        self.put(migration, 'def migrate(cr, version): pass\n')
        self.base = self.commit()
        self.put('sample/__manifest__.py', "{'version': '19.0.1.1.0'}")
        self.target = self.commit()
        contract, proof = self.contract(), self.build()
        self.assertEqual(contract['modules']['sample']['changed_migrations'], [])
        self.assertEqual(contract['modules']['sample']['expected_migrations'], [migration])
        capture = self.observation(contract)
        path = self.root / 'deployment.json'
        path.write_text(json.dumps(capture))
        with self.assertRaisesRegex(ValueError, 'non sourcée'):
            evaluate(contract, proof, self.reference(path))
        run = self.root / 'migration.json'
        run.write_text(json.dumps({'commit': self.target, 'target_environment': 'synthetic-target-v1',
                                   'migration': migration, 'executed': True}))
        capture['migrations'] = {migration: self.reference(run)}
        path.write_text(json.dumps(capture))
        self.assertEqual(evaluate(contract, proof, self.reference(path))['status'], 'deployed_verified')

    def test_failed_build_and_changed_log_rejected(self):
        self.command = [sys.executable, '-c', 'raise SystemExit(1)']
        contract, proof = self.contract(), self.build()
        with self.assertRaisesRegex(ValueError, 'non réussi'):
            evaluate(contract, proof)
        (self.root / 'build.log').write_text('forged success')
        with self.assertRaises(ValueError):
            evaluate(contract, proof)

    def test_proof_command_and_environment_cannot_be_substituted(self):
        contract, proof = self.contract(), self.build()
        contract['build_command'] = ['not-the-measured-build']
        with self.assertRaisesRegex(ValueError, 'commande de build'):
            evaluate(contract, proof)
        contract['build_command'] = self.command
        contract['build_environment'] = 'different'
        with self.assertRaisesRegex(ValueError, 'environnement'):
            evaluate(contract, proof)

    def test_deployment_mutations_old_version_wrong_target_unsourced_effect_failed_build(self):
        contract, proof = self.contract(), self.build()
        for mutation, fragment in [
                (lambda c: c['installed_modules']['sample'].update(version='19.0.1.0.0'), 'version installée'),
                (lambda c: c.update(target_environment='another'), 'environnement/commit'),
                (lambda c: c.update(build_status='failed'), 'build distant'),
                (lambda c: c['effects']['column_present'].pop('source'), 'non sourcée'),
                (lambda c: c['effects']['column_present'].update(actual=False), 'effet non relu'),
                (lambda c: c.update(observed_at='2000-01-01T00:00:00+00:00'), 'antérieure')]:
            with self.subTest(fragment=fragment):
                capture = self.observation(contract)
                mutation(capture)
                path = self.root / 'deployment.json'
                path.write_text(json.dumps(capture))
                with self.assertRaisesRegex(ValueError, fragment):
                    evaluate(contract, proof, self.reference(path))

    def test_unsourced_attestation_and_tampered_capture_rejected(self):
        contract, proof = self.contract(), self.build()
        with self.assertRaisesRegex(ValueError, 'non sourcée'):
            evaluate(contract, {'path': proof['path']})
        Path(proof['path']).write_text('{}')
        with self.assertRaisesRegex(ValueError, 'modifiée'):
            evaluate(contract, proof)

    def test_build_must_cover_entire_target_module_and_no_untracked_files(self):
        self.put('sample/untracked.py', '# unexpected local code\n')
        contract, proof = self.contract(), self.build()
        with self.assertRaisesRegex(ValueError, 'tous les fichiers'):
            evaluate(contract, proof)

    def test_schema_summary_cannot_be_edited_to_hide_error(self):
        contract = self.contract()
        contract['sources'].clear()
        with self.assertRaisesRegex(ValueError, 'incohérent'):
            evaluate(contract, self.build())


if __name__ == '__main__':
    unittest.main()
