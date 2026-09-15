"""Do not rank a fast native answer as a received Odoo correction."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from odoo_bench_native import runtime_reception
from odoo_bench_agent_workflows import jobs_for


class ReceptionMetricsTests(unittest.TestCase):
    def setUp(self):
        self.sources = {'models/request.py': 'code-v2', 'tests/test_request.py': 'test-v2'}
        self.state = {'status': 'executed', 'oracle': {'passed': True}}
        self.events = [dict(args=[action], exit_code=0,
                            module_sources_before=dict(self.sources),
                            module_sources_after=dict(self.sources),
                            test_result={'valid': True}) for action in ('lint', 'qa', 'update')]

    def receive(self):
        return runtime_reception(self.state, self.events, self.sources)

    def test_staged_campaign_preserves_holdout_and_call_budget(self):
        baseline = jobs_for('baseline')
        candidate = jobs_for('candidate')
        self.assertEqual({case for case, _, _ in baseline}, {'N06'})
        self.assertEqual(len(baseline + candidate), 8)
        self.assertEqual(len(set(baseline + candidate)), 8)
        for provider in ('codex', 'claude'):
            for case in ('N06', 'N07'):
                self.assertEqual({label for c, p, label in baseline + candidate
                                  if c == case and p == provider}, {'reference', 'candidate'})

    def test_full_runtime_is_still_pending_semantic_reception(self):
        result = self.receive()
        self.assertTrue(result['passed'])
        self.assertEqual(result['semantic_review'], 'pending')
        self.assertIsNone(result['time_to_accepted_receipt_seconds'])

    def test_fast_return_without_qa_is_not_received(self):
        self.events = []
        self.assertFalse(self.receive()['passed'])

    def test_oracle_cannot_replace_agent_qa(self):
        self.events[1]['test_result']['valid'] = False
        self.assertFalse(self.receive()['passed'])

    def test_final_code_or_tests_changed_invalidates_receipts(self):
        for path in self.sources:
            with self.subTest(path=path):
                previous = self.sources[path]
                self.sources[path] = 'changed'
                self.assertFalse(self.receive()['passed'])
                self.sources[path] = previous

    def test_mutation_during_qa_is_not_a_fresh_receipt(self):
        self.events[1]['module_sources_before']['models/request.py'] = 'old'
        self.assertFalse(self.receive()['passed'])

    def test_latest_failed_qa_is_not_hidden_by_previous_green(self):
        event = copy.deepcopy(self.events[1])
        event['exit_code'] = 1
        self.events.append(event)
        self.assertFalse(self.receive()['passed'])

    def test_provider_completion_with_error_is_not_success(self):
        self.state['turns'] = [{'status': 'completed', 'provider_completed': True, 'error': 'quota exhausted'}]
        self.assertFalse(self.receive()['passed'])

    def test_timeout_with_remaining_good_code_is_not_a_completed_trial(self):
        self.state['status'] = 'incident'
        self.assertFalse(self.receive()['passed'])

    def test_historical_events_without_hashes_are_unknown(self):
        for event in self.events:
            event.pop('module_sources_before')
            event.pop('module_sources_after')
        self.assertFalse(self.receive()['passed'])

    def test_no_module_does_not_claim_studio_runtime_coverage(self):
        self.sources = {}
        self.assertFalse(self.receive()['passed'])


if __name__ == '__main__':
    unittest.main()
