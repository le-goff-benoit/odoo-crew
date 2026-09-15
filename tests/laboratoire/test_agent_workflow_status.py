"""Status reads live trial files without starting work or rewriting archives."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts/odoo_bench_agent_workflows.py'


class AgentWorkflowStatusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)
        self.identifier = 'N06-codex-reference'
        self.campaign = {
            'phases': {'baseline': 'started'},
            'trials': {self.identifier: {'status': 'reserved'}},
        }
        (self.output / 'campaign.json').write_text(json.dumps(self.campaign))

    def read_status(self, trial=None):
        if trial is not None:
            folder = self.output / self.identifier
            folder.mkdir()
            (folder / 'state.json').write_text(json.dumps(trial))
        before = {p.relative_to(self.output): p.read_bytes()
                  for p in self.output.rglob('*') if p.is_file()}
        result = subprocess.run(
            [sys.executable, '-B', str(SCRIPT), 'status', '--output', str(self.output)],
            text=True, capture_output=True, check=True, timeout=10,
        )
        after = {p.relative_to(self.output): p.read_bytes()
                 for p in self.output.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
        data = json.loads(result.stdout)
        self.assertEqual(data['phases'], self.campaign['phases'])
        return data['trials'][self.identifier]

    def test_running_trial_overrides_reserved_campaign_entry(self):
        self.assertEqual(self.read_status({'status': 'running'}), {
            'status': 'running', 'runtime_gate': None, 'agent_seconds': None,
        })

    def test_completed_trial_is_visible_before_ordered_campaign_collection(self):
        self.assertEqual(self.read_status({
            'status': 'executed', 'reception': {'passed': False}, 'agent_seconds': 12.3,
        }), {'status': 'executed', 'runtime_gate': False, 'agent_seconds': 12.3})

    def test_trial_without_state_keeps_reserved_and_creates_nothing(self):
        self.assertEqual(self.read_status(), {
            'status': 'reserved', 'runtime_gate': None, 'agent_seconds': None,
        })


if __name__ == '__main__':
    unittest.main()
