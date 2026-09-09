import os
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from odoo_instance import Instance
from odoo_pack import Target


class GuardTests(unittest.TestCase):
    def test_local_target_refuses_remote_before_authentication(self):
        for url in ('https://example.invalid', 'http://localhost.example.invalid', 'http://user@localhost:8079', 'file:///etc/passwd'):
            with self.assertRaises(ValueError):
                Target.local('synthetic', url, 'dummy', 'dummy')
        for url in ('http://localhost:8079', 'http://127.0.0.1:8079', 'http://[::1]:8079'):
            self.assertIsNone(Target.local('synthetic', url, 'dummy', 'dummy').guard)

    def test_read_like_method_name_cannot_bypass_production_guard(self):
        inst = Instance('fixture', 'synthetic-prod', 'production', 'https://example.invalid', 'dummy')
        inst._proxy = Mock()
        inst.uid = Mock(return_value=1)
        for method in ('search_and_delete', 'get_reset', 'read_and_write', 'check_and_apply', 'create'):
            with self.assertRaises(SystemExit):
                inst.execute('x.synthetic', method)
        inst._proxy.assert_not_called()
        inst.execute('x.synthetic', 'search_read', [])
        inst._proxy.assert_called_once()

    def test_confirmation_requires_both_flags(self):
        inst = Instance('fixture', 'synthetic-prod', 'production', 'https://example.invalid', 'dummy')
        inst._proxy = Mock()
        inst.uid = Mock(return_value=1)
        with patch.dict(os.environ, {'ODOO_PRODUCTION_CONFIRMED': 'synthetic-prod'}):
            with self.assertRaises(SystemExit):
                inst.execute('x.synthetic', 'write', [1], {})
            inst.execute('x.synthetic', 'write', [1], {}, allow_write=True)
        inst._proxy.assert_called_once()
