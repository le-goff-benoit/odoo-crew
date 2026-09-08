"""Contrats du laboratoire : pas de faux vert ni de contamination du corrigé."""
import importlib.util
import json
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bench', ROOT / 'scripts/odoo_bench.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


class BenchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def plan(self):
        return b.create_plan(self.root, ['B06'], ['codex'], {'codex': {'model': 'fixture', 'effort': 'high'}})

    def test_packet_excludes_secret_rubric(self):
        case = dict(b.cases()['B06'], rubric=[{'expected': 'SECRET CORRECTOR'}])
        packet = b.make_packet(case, 'ROLE')
        self.assertNotIn('SECRET CORRECTOR', packet)
        self.assertIn(case['prompt'], packet)

    def test_plan_rejects_unimplemented_and_overbudget(self):
        for selected, seconds in [(['B01'], 600), (['B06'], 601), (['B06', 'B06'], 600)]:
            with self.assertRaises(ValueError):
                b.create_plan(self.root, selected, ['codex'], {'codex': {'model': 'fixture', 'effort': 'high'}}, seconds)

    def test_zero_exit_without_completion_is_not_completion(self):
        path = self.root / 'events'
        path.write_text(json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'answer'}}))
        self.assertFalse(b.parse_output(path, 'codex')['completed_event'])

    def test_provider_error_and_usage(self):
        path = self.root / 'events'
        path.write_text(json.dumps({'type': 'result', 'subtype': 'error_max_turns', 'is_error': True, 'result': 'partial'}))
        result = b.parse_output(path, 'claude')
        self.assertFalse(result['completed_event'])
        self.assertEqual(result['provider_error'], 'error_max_turns')

    def test_stop_preserves_pending_without_launch(self):
        run = self.plan()
        (run / 'STOP').touch()
        with patch.object(b, 'isolated_command', side_effect=AssertionError('must not launch')):
            b.run_plan(run)
        self.assertEqual(b.read_json(run / 'state.json')['trials'][0]['status'], 'pending')

    def test_tampered_packet_refuses_launch(self):
        run = self.plan()
        (run / 'B06-codex/packet.txt').write_text('altered')
        with patch.object(b, 'isolated_command', side_effect=AssertionError('must not launch')):
            with self.assertRaisesRegex(ValueError, 'modifié'):
                b.run_plan(run)

    def ready_review(self):
        run = self.plan()
        state = b.read_json(run / 'state.json')
        trial = state['trials'][0]
        answer = 'Synthetic observed answer'
        (run / trial['id'] / 'answer.md').write_text(answer)
        trial.update(status='completed', answer_sha256=b.digest(answer.encode()))
        b.atomic_json(run / 'state.json', state)
        review = {'reviewer': 'human fixture', 'answer_sha256': trial['answer_sha256'], 'criteria': {
            r['id']: {'grade': 'pass', 'evidence': 'observed passage'} for r in b.cases()['B06']['rubric']}}
        return run, trial, review

    def test_critical_failure_never_averaged_away(self):
        run, trial, review = self.ready_review()
        review['criteria']['reject']['grade'] = 'fail'
        b.review_trial(run, trial['id'], review)
        reviewed = b.read_json(run / 'state.json')['trials'][0]['review']
        self.assertEqual(reviewed['verdict'], 'rejected')
        self.assertIsNone(reviewed['dimensions']['development'])

    def test_review_requires_all_criteria_and_correct_answer(self):
        run, trial, review = self.ready_review()
        review['answer_sha256'] = 'wrong'
        with self.assertRaises(ValueError):
            b.review_trial(run, trial['id'], review)
        review['answer_sha256'] = trial['answer_sha256']
        del review['criteria']['reject']
        with self.assertRaises(ValueError):
            b.review_trial(run, trial['id'], review)

    def test_completed_never_retried(self):
        run, trial, _ = self.ready_review()
        with patch.object(b, 'isolated_command', side_effect=AssertionError('must not launch')):
            b.run_plan(run)
        self.assertEqual(b.read_json(run / 'state.json')['trials'][0]['status'], 'completed')

    def test_runner_requires_completion_and_rejects_tool_calls(self):
        for event, expected in [
            ({'type': 'turn.completed', 'usage': {'input_tokens': 3}}, 'completed'),
            ({'type': 'turn.started'}, 'error'),
            ({'type': 'item.completed', 'item': {'type': 'command_execution'}}, 'error'),
        ]:
            with self.subTest(event=event):
                run = self.plan()
                events = [ {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'answer'}}, event]
                code = 'import sys; sys.stdin.read(); print(' + repr('\n'.join(json.dumps(e) for e in events)) + ')'
                with patch.object(b, 'isolated_command', return_value=[sys.executable, '-c', code]), patch.object(b.shutil, 'which', return_value=sys.executable):
                    b.run_plan(run)
                trial = b.read_json(run / 'state.json')['trials'][0]
                self.assertEqual(trial['status'], expected)
                self.assertIsNone(trial['review'])
