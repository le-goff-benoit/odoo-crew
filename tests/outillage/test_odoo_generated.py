"""Détecter les divergences sur chaque sortie déclarée, sans installer les profils."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import shutil

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('generated', ROOT / 'scripts/odoo_generated.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


class GeneratedTests(unittest.TestCase):
    def test_common_instruction_change_invalidates_every_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'source'
            root.mkdir()
            shutil.copytree(ROOT / 'roles', root / 'roles')
            for name in ('build.sh', 'routing.md'):
                shutil.copy2(ROOT / name, root / name)
            dest = Path(tmp) / 'distribution'
            for path, content in g.expected_outputs(root, dest).items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            baseline = len(g.check(root, dest))
            common = root / 'roles/communication.md'
            common.write_text(common.read_text() + '\nUpdated shared instruction.\n')
            self.assertEqual(len(g.check(root, dest)) - baseline, 28)
            for path, content in g.expected_outputs(root, dest).items():
                path.write_text(content)
            self.assertEqual(len(g.check(root, dest)), baseline)

    def test_every_declared_output_is_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            outputs = g.expected_outputs(ROOT, dest)
            self.assertEqual(len(outputs), 28)
            for path, content in outputs.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            # Routing intentionally absent; each mutation must add one separate error.
            baseline = g.check(ROOT, dest)
            self.assertEqual(len(baseline), 3)
            for path, content in outputs.items():
                with self.subTest(path=str(path.relative_to(dest))):
                    path.write_text(content + '\nmanual drift\n')
                    self.assertEqual(len(g.check(ROOT, dest)), 4)
                    path.unlink()
                    self.assertEqual(len(g.check(ROOT, dest)), 4)
                    path.write_text(content)

    def test_empty_build_is_not_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'build.sh').write_text('# no declarations')
            with self.assertRaises(ValueError):
                g.expected_outputs(root, root / 'outputs')
