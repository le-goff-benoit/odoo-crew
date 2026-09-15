"""Measurement must not turn missing counters or a red gate into success."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    'workflow_summary', ROOT / 'docs/quality-lab/agent-workflows-2026-09-15/summarize.py')
summary = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(summary)


class WorkflowSummaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.trial = self.root / 'campaign/N06-codex-reference'
        self.review = self.root / 'reviews/N06-codex-reference'
        self.trial.mkdir(parents=True)
        self.review.mkdir(parents=True)
        self.state = {
            'status': 'executed', 'started_at': '2026-09-16T00:00:00+00:00',
            'elapsed_to_oracle_seconds': 60, 'oracle': {'passed': True},
            'reception': {'passed': True}, 'turns': [{'tool_calls': 2}],
        }
        self.verdict = {
            'verdict': 'accepted', 'review_seconds': 20,
            'finished_at_utc': '2026-09-16T00:02:00+00:00',
        }

    def measure(self):
        (self.trial / 'state.json').write_text(json.dumps(self.state))
        if self.verdict is not None:
            (self.review / 'semantic-review.json').write_text(json.dumps(self.verdict))
        return summary.summarize(self.root / 'campaign', self.root / 'reviews')['rows'][0]

    def test_work_and_queue_are_distinct_and_reserve_is_not_full_receipt(self):
        row = self.measure()
        self.assertEqual(row['measured_work_to_verdict_seconds'], 80)
        self.assertEqual(row['wall_to_verdict_seconds'], 120)
        self.assertEqual(row['review_queue_seconds'], 40)
        self.assertEqual(row['time_to_unreserved_receipt_seconds'], 120)
        self.verdict['verdict'] = 'accepted_with_reservations'
        self.assertIsNone(self.measure()['time_to_unreserved_receipt_seconds'])

    def test_semantic_acceptance_cannot_override_failed_or_missing_execution(self):
        for field, value in [('reception', {'passed': False}),
                             ('oracle', {'passed': False}), ('status', 'incident')]:
            old = self.state[field]
            self.state[field] = value
            self.assertIsNone(self.measure()['time_to_unreserved_receipt_seconds'])
            self.state[field] = old

    def test_missing_counter_or_pending_review_stays_unknown(self):
        for turns in [[], [{}], [{'tool_calls': None}], [{'tool_calls': 2}, {}]]:
            self.state['turns'] = turns
            self.assertIsNone(self.measure()['tool_calls'])
        self.verdict = None
        (self.review / 'semantic-review.json').unlink()
        row = self.measure()
        self.assertIsNone(row['post_reception_rework_performed'])
        self.assertIsNone(row['review_seconds'])
        self.assertIsNone(row['measured_work_to_verdict_seconds'])


if __name__ == '__main__':
    unittest.main()
