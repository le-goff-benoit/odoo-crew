from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import odoo_bench_runtime as runtime


class RuntimeBoundaryTests(unittest.TestCase):
    def test_implementation_outside_fixture_is_rejected_before_docker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(runtime, 'command', side_effect=AssertionError('Docker must not start')):
                with self.assertRaisesRegex(ValueError, 'hors fixtures'):
                    runtime.campaign(root / 'out', {}, fixtures=root, implementation='../outside.py')
            self.assertFalse((root / 'out').exists())
