"""Détecter les divergences sur chaque sortie déclarée, sans installer les profils."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('generated', ROOT / 'scripts/odoo_generated.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


class GeneratedTests(unittest.TestCase):
    def test_every_declared_output_is_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            outputs = g.expected_outputs(ROOT, dest)
            self.assertEqual(len(outputs), 26)
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
