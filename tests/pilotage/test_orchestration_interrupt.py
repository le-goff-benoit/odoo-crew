import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import odoo_orchestrate as orchestrate


class InterruptBarrierTests(unittest.TestCase):
    def test_interrupt_then_summary_does_not_restart_until_explicit_resume(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'events.jsonl'
            state = {'id': 'run', 'status': 'active', 'session_id': 'main',
                     'authorized_at': '2026-09-15T10:00:00.000000+00:00'}
            event = {'hook_event_name': 'Stop', 'session_id': 'main'}
            path.write_text(json.dumps({'kind': 'Interrupt', 'rootId': 'main', 'parentId': None,
                                        'at': '2026-09-15T10:00:00.100000+00:00'}) + '\n')
            before = path.read_bytes()
            with patch.object(orchestrate, 'next_actions', return_value=[{'task': 'B', 'action': 'start'}]):
                self.assertEqual(orchestrate.hook(state, event, path), {})
                # A progress update is not a new authorization after interrupt.
                state['updated_at'] = '2026-09-15T10:00:00.200000+00:00'
                self.assertEqual(orchestrate.hook(state, event, path), {})
                state['authorized_at'] = '2026-09-15T10:00:00.300000+00:00'
                self.assertEqual(orchestrate.hook(state, event, path)['decision'], 'block')
            self.assertEqual(path.read_bytes(), before)

    def test_child_failure_and_other_session_do_not_pause_parent(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'events.jsonl'
            state = {'session_id': 'main', 'authorized_at': '2026-09-15T10:00:00Z'}
            for root, parent in [('main', 'main'), ('other', None)]:
                path.write_text(json.dumps({'kind': 'StopFailure', 'rootId': root, 'parentId': parent,
                                            'at': '2026-09-15T10:00:10Z'}) + '\n')
                self.assertFalse(orchestrate.interrupted_since_authorization(state, path))
            path.write_text('{broken')
            self.assertTrue(orchestrate.interrupted_since_authorization(state, path))
