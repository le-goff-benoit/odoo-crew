import json
from pathlib import Path
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch
import xmlrpc.client

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from odoo_bench_native import Lab


class NativeRpcTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.lab = Lab.__new__(Lab)
        self.lab.case = {'kind': 'module', 'module': 'lab_rental', 'model': 'lab.rental'}
        self.lab.project = self.root
        self.lab.url = 'http://127.0.0.1:12345'
        self.request = self.root / 'request.json'
        self.payload = {'model': 'lab.rental', 'method': 'create', 'args': [{'name': 'test', 'days': -1}], 'kwargs': {}}
        self.request.write_text(json.dumps(self.payload))

    def test_rpc_preserves_business_fault_and_stops_http(self):
        rpc = MagicMock()
        rpc.__enter__.return_value = rpc
        rpc.authenticate.return_value = 2
        rpc.execute_kw.side_effect = xmlrpc.client.Fault(2, 'Durée négative refusée')
        with patch.object(self.lab, 'start_http'), patch.object(self.lab, 'stop_http') as stop, patch('xmlrpc.client.ServerProxy', return_value=rpc):
            result = self.lab.rpc(self.request)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)['fault_string'], 'Durée négative refusée')
        self.assertEqual(json.loads(result.stdout)['outcome'], 'fault')
        stop.assert_called_once()
        self.assertEqual(rpc.execute_kw.call_args.args[:5], ('lab_client', 2, 'admin', 'lab.rental', 'create'))

    def test_rpc_success_is_response_not_test_verdict(self):
        rpc = MagicMock()
        rpc.__enter__.return_value = rpc
        rpc.authenticate.return_value = 2
        rpc.execute_kw.return_value = 42
        with patch.object(self.lab, 'start_http'), patch.object(self.lab, 'stop_http'), patch('xmlrpc.client.ServerProxy', return_value=rpc):
            result = self.lab.rpc(self.request)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), {'transport': 'xmlrpc', 'outcome': 'result', 'result': 42})

    def test_rpc_rejects_other_target_and_malformed_request_before_start(self):
        invalid = [dict(self.payload, url='https://example.invalid'), dict(self.payload, model='res.users'),
                   dict(self.payload, method='_private'), dict(self.payload, args={}),
                   dict(self.payload, kwargs=[]), [], dict(self.payload, method=None)]
        with patch.object(self.lab, 'start_http') as start:
            for payload in invalid:
                with self.subTest(payload=payload):
                    self.request.write_text(json.dumps(payload))
                    with self.assertRaises(ValueError):
                        self.lab.rpc(self.request)
            start.assert_not_called()

    def test_rpc_transport_error_still_stops_http(self):
        with patch.object(self.lab, 'start_http', side_effect=RuntimeError('HTTP indisponible')), patch.object(self.lab, 'stop_http') as stop:
            with self.assertRaises(RuntimeError):
                self.lab.rpc(self.request)
        stop.assert_called_once()

    def test_bridge_records_rpc_fault_without_calling_it_success(self):
        lab = self.lab
        lab.lock = threading.Lock()
        lab.folder = self.root
        lab.events = []
        fault = json.dumps({'transport': 'xmlrpc', 'outcome': 'fault', 'fault_string': 'message'})
        with patch.object(lab, 'sync') as sync, patch.object(lab, 'rpc', return_value=SimpleNamespace(returncode=1, stdout=fault)) as rpc:
            result = lab.handle(['rpc', str(self.request)])
            sync.assert_called_once()
            rpc.assert_called_once_with(self.request)
        self.assertEqual(result['exit_code'], 1)
        self.assertEqual(lab.events[0]['exit_code'], 1)
        self.assertEqual((self.root / lab.events[0]['log']).read_text(), fault)
        self.assertNotIn('test_result', lab.events[0])

    def test_bridge_rejects_outside_or_oversized_rpc_before_http(self):
        self.lab.lock = threading.Lock()
        with patch.object(self.lab, 'sync'), patch.object(self.lab, 'rpc') as rpc:
            with self.assertRaises(ValueError): self.lab.handle(['rpc', '/etc/passwd'])
            self.request.write_text('x' * (1024 * 1024 + 1))
            with self.assertRaises(ValueError): self.lab.handle(['rpc', str(self.request)])
            rpc.assert_not_called()

    def test_http_unavailable_is_an_error_with_log(self):
        self.lab.prefix = 'test-rpc'
        self.lab.folder = self.root
        response = SimpleNamespace(stdout='{"network": {"IPAddress": "127.0.0.1"}}', check_returncode=lambda: None)
        with patch.object(self.lab, 'compose', return_value=response), patch('odoo_bench_native.execute', return_value=response), patch('odoo_bench_native.Proxy'), patch('odoo_bench_native.threading.Thread'), patch('xmlrpc.client.ServerProxy', side_effect=ConnectionRefusedError()), patch('odoo_bench_native.time.sleep'):
            with self.assertRaisesRegex(RuntimeError, 'HTTP synthétique indisponible'):
                self.lab.start_http()
        self.assertTrue((self.root / 'web-error.log').is_file())
