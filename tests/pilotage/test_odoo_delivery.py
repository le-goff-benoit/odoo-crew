"""Régression : les anciens appels email sont inertes, les données préservées."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[2] / 'scripts'


class RemovedDeliveryTests(unittest.TestCase):
    def test_no_importable_send_or_connection_api(self):
        spec = importlib.util.spec_from_file_location('removed_delivery', SCRIPTS / 'odoo_delivery.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for name in ('send', 'prepare', 'configure', 'mime'):
            self.assertFalse(hasattr(module, name))
        self.assertEqual(module.config_for('/not/a/project'), {'enabled': False})
        self.assertEqual(module.status('/not/a/release'), {'enabled': False, 'status': 'not_prepared'})
        for name in ('odoo_gmail.py', 'odoo_smtp.py'):
            self.assertFalse((SCRIPTS / name).exists())

    def test_legacy_commands_refused_without_echoing_arguments(self):
        for command in ('connect', 'connect-smtp', 'configure', 'prepare', 'edit', 'preview', 'status', 'send', 'disconnect', '--help'):
            with self.subTest(command=command):
                result = subprocess.run([sys.executable, str(SCRIPTS / 'odoo_delivery.py'),
                                         command, 'PRIVATE-SYNTHETIC-ARGUMENT'],
                                        capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 1)
                self.assertIn('retirée', result.stderr)
                self.assertNotIn('PRIVATE-SYNTHETIC', result.stdout + result.stderr)
                self.assertEqual(result.stdout, '')

    def test_old_records_not_read_or_modified(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            config = root / 'config.json'
            config.write_text('Not even valid JSON; must not be read')
            draft = root / 'draft.json'
            draft.write_text('Private synthetic draft')
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            result = subprocess.run([sys.executable, str(SCRIPTS / 'odoo_delivery.py'), 'send',
                                     '--human-confirmed', '--approval', str(draft)],
                                    env={**os.environ, 'ODOO_DELIVERY_STATE_DIR': folder},
                                    capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 1)
            self.assertIn('retirée', result.stderr)
            self.assertEqual({p.name: p.read_bytes() for p in root.iterdir()}, before)

    def test_incoming_email_import_is_not_removed(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'request.eml'
            source.write_text('From: synthetic@example.test\nSubject: Demande synthétique\nContent-Type: text/plain; charset=utf-8\n\nTexte client conservé.\n')
            result = subprocess.run([sys.executable, str(SCRIPTS / 'odoo_mail.py'), str(source)],
                                    capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0)
        self.assertIn('Texte client conservé.', result.stdout)


if __name__ == '__main__':
    unittest.main()
