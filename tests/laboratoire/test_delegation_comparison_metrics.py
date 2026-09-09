import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[2] / 'benchmarks/delegation_comparison/native_metrics.py'
spec = importlib.util.spec_from_file_location('comparison_metrics', PATH)
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)


class TestComparisonMetrics(unittest.TestCase):
    def test_fork_history_is_not_child_execution(self):
        child = {'type': 'session_meta', 'payload': {'id': 'child'}}
        ancestor = {'type': 'session_meta', 'payload': {'id': 'parent'}}
        context = {'type': 'turn_context', 'payload': {'turn_id': 'ancestor-unfinished'}}
        boundary = {'type': 'event_msg', 'payload': {'type': 'thread_settings_applied', 'thread_id': 'child'}}
        own = {'type': 'turn_context', 'payload': {'turn_id': 'child-turn'}}
        rows = [child, ancestor, context, boundary, own]
        self.assertEqual(metrics.own_records(rows), [child, boundary, own])
        self.assertEqual(metrics.own_records([child, own]), [child, own])
        with self.assertRaises(ValueError):
            metrics.own_records([child, ancestor, context, own])

    def test_export_excludes_private_messages_and_terminal_text(self):
        for payload in [{'type': 'reasoning'}, {'type': 'message', 'role': 'user'},
                        {'type': 'message', 'role': 'developer'},
                        {'type': 'message', 'role': 'assistant', 'channel': 'analysis'}]:
            self.assertIsNone(metrics.allowed({'type': 'response_item', 'payload': payload}))
        row = metrics.allowed({'type': 'event_msg', 'payload': {'type': 'task_complete', 'last_agent_message': 'exclude', 'duration_ms': 10}})
        self.assertNotIn('last_agent_message', row['payload'])
        self.assertIsNotNone(metrics.allowed({'type': 'response_item', 'payload': {'type': 'message', 'role': 'assistant', 'phase': 'final_answer'}}))

    def test_only_final_thread_counter_and_completed_turns(self):
        records = [
            {'type': 'session_meta', 'payload': {'id': 'a', 'timestamp': '2026-09-09T00:00:00Z', 'source': {'subagent': {'thread_spawn': {'agent_path': '/root/a'}}}}},
            {'type': 'turn_context', 'payload': {'turn_id': 't', 'model': 'm', 'effort': 'high'}},
            {'type': 'token_usage_record', 'payload': {'response_id': 'r1', 'thread_token_usage': {'total_tokens': 5}}},
            {'type': 'token_usage_record', 'payload': {'response_id': 'r2', 'thread_token_usage': {'total_tokens': 9}}},
            {'type': 'event_msg', 'timestamp': '2026-09-09T00:00:02Z', 'payload': {'type': 'task_complete', 'turn_id': 't', 'duration_ms': 2000}}]
        row = metrics.summarize(records)
        self.assertEqual(row['tokens']['total_tokens'], 9)
        self.assertTrue(row['complete'])
        self.assertFalse(metrics.summarize(records[:-1])['complete'])

    def row(self, name, total=10, response='r'):
        return {'agent': name, 'tokens': None if total is None else {'total_tokens': total, 'cached_input_tokens': 3},
                'complete': True, 'start': 0, 'end': 3, 'turns': [{'start': 0, 'end': 3}],
                'usage_response_ids': [response], 'model_effort': [('m', 'high')]}

    def test_exact_tree_aggregate_cache_subset_and_overlap(self):
        rows = [self.row('/root/a', response='p'), self.row('/root/a/x', response='x'),
                self.row('/root/a/y', response='y'), self.row('/root/ab', 99, 'z')]
        report = metrics.aggregate(rows, '/root/a')
        self.assertEqual(report['tokens']['total_tokens'], 30)
        self.assertEqual(report['descendants'], 2)
        self.assertEqual(report['child_overlap_seconds'], 3)

    def test_missing_is_not_zero_and_duplicates_not_double_counted(self):
        zero = metrics.aggregate([self.row('/root/a', 0)], '/root/a')
        self.assertTrue(zero['tokens_measured'])
        missing = metrics.aggregate([self.row('/root/a', None)], '/root/a')
        self.assertFalse(missing['tokens_measured'])
        self.assertIsNone(missing['tokens'])
        duplicate = metrics.aggregate([self.row('/root/a'), self.row('/root/a/x')], '/root/a')
        self.assertFalse(duplicate['tokens_measured'])
        active = self.row('/root/a'); active['complete'] = False
        self.assertIsNone(metrics.aggregate([active], '/root/a')['wall_seconds'])
