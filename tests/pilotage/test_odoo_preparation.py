"""Cadrage avant release : une mesure, une attribution, aucune prévision inventée."""
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import odoo_effort as effort
import odoo_release_guard as guard


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        self.usage = {'thread_id': 'session-1', 'model': 'fixture', 'provider': 'codex',
                      'tokens': dict.fromkeys(effort.TOKEN_KEYS, 0),
                      'source_sha256': 'fixture', 'warnings': [], 'identities': []}
        self.mock_usage = patch.object(effort, 'normalized_usage', return_value=self.usage)
        self.mock_usage.start()
        self.addCleanup(self.mock_usage.stop)
        self.clock = {'boot': 'boot', 'monotonic': 100, 'boottime': 100}
        clock = patch.object(effort, 'clock_snapshot', side_effect=lambda: dict(self.clock))
        clock.start()
        self.addCleanup(clock.stop)

    def release(self, name='R1', open=True):
        folder = self.project / 'changelog' / name
        folder.mkdir(parents=True)
        (folder / 'README.md').write_text('<!-- release ouverte -->' if open else '# Close')
        effort.init(folder)
        return folder

    def start(self):
        return effort.prepare_start(self.project, 'odoo-analyst', 'codex', 'fixture')

    def test_project_preparation_survives_attachment_without_copy_or_forecast(self):
        entry = self.start()
        self.assertFalse((self.project / 'changelog').exists())
        self.clock.update(monotonic=160, boottime=460)
        pending = effort.preparation_report(self.project, live=True)
        self.assertEqual(pending['rows'][0]['known_minutes'], 1)
        release = self.release()
        before = (release / 'effort.json').read_bytes()
        effort.prepare_attach(self.project, entry['id'], release)
        effort.prepare_attach(self.project, entry['id'], release)
        self.assertIsNone(effort.preparation_report(self.project))
        self.assertEqual(before, (release / 'effort.json').read_bytes())
        effort.stop(effort.preparation_folder(self.project), entry['id'], 'fixture')
        report = effort.report(release)
        self.assertEqual(report['rows'][0]['entries'], [entry['id']])
        self.assertEqual(report['rows'][0]['actual_minutes'], 1)
        self.assertEqual(report['rows'][0]['suspended_seconds'], 300)
        self.assertIsNone(report['rows'][0]['initial'])
        self.assertEqual(report['rows'][0]['phase'], 'preparation')
        self.assertEqual(effort.state(release)['entries'], [])
        effort.check_report(release)

    def test_overlap_refused_in_both_directions(self):
        entry = self.start()
        release = self.release()
        effort.add_task(release, 'T01', 'Tâche')
        with self.assertRaisesRegex(ValueError, 'déjà attribuée'):
            effort.start(release, 'T01', 'odoo-analyst', 'codex', 'fixture')
        effort.stop(effort.preparation_folder(self.project), entry['id'], 'fixture')
        effort.start(release, 'T01', 'odoo-analyst', 'codex', 'fixture')
        with self.assertRaisesRegex(ValueError, 'déjà attribuée'):
            self.start()

    def test_closure_catches_attached_running_timer(self):
        entry = self.start()
        release = self.release()
        effort.prepare_attach(self.project, entry['id'], release)
        with self.assertRaisesRegex(ValueError, 'chronomètre'):
            effort.check_closure(release)
        effort.interrupt(effort.preparation_folder(self.project), entry['id'], 'borne perdue')
        self.assertFalse(effort.check_closure(release)['complete'])

    def test_closed_foreign_or_second_release_rejected_without_mutation(self):
        entry = self.start()
        release = self.release()
        closed = self.release('closed', open=False)
        before = deepcopy(effort.state(effort.preparation_folder(self.project)))
        with self.assertRaises(ValueError):
            effort.prepare_attach(self.project, entry['id'], closed)
        with self.assertRaises(ValueError):
            effort.prepare_attach(self.project.parent, entry['id'], release)
        self.assertEqual(before, effort.state(effort.preparation_folder(self.project)))
        effort.prepare_attach(self.project, entry['id'], release)
        with self.assertRaises(ValueError):
            effort.prepare_attach(self.project, entry['id'], self.release('R2'))

    def test_countercase_other_preparation_is_not_automatically_attached(self):
        first = self.start()
        self.usage['thread_id'] = 'session-2'
        second = self.start()
        release = self.release()
        effort.prepare_attach(self.project, first['id'], release)
        pending = effort.preparation_report(self.project, live=True)
        attached = effort.report_data(release, effort.state(release), live=True)
        self.assertEqual(pending['rows'][0]['entries'], [second['id']])
        self.assertEqual(attached['rows'][0]['entries'], [first['id']])

    def test_read_only_preview_and_reboot_never_count_night(self):
        entry = self.start()
        file = effort.preparation_folder(self.project) / 'effort.json'
        before = file.read_bytes()
        self.clock.update(boot='new-boot', monotonic=86400, boottime=86400)
        row = effort.preparation_report(self.project, live=True)['rows'][0]
        self.assertIsNone(row['actual_minutes'])
        self.assertEqual(row['known_minutes'], 0)
        self.assertEqual(before, file.read_bytes())
        stopped = effort.stop(effort.preparation_folder(self.project), entry['id'], 'fixture')
        self.assertEqual(stopped['status'], 'interrupted')
        self.assertIsNone(stopped['seconds'])

    def test_concurrent_start_has_one_winner(self):
        def attempt(_):
            try:
                return self.start()['id']
            except ValueError:
                return None
        with ThreadPoolExecutor(max_workers=4) as workers:
            results = list(workers.map(attempt, range(4)))
        self.assertEqual(sum(bool(value) for value in results), 1)
        self.assertEqual(len(effort.state(effort.preparation_folder(self.project))['entries']), 1)

    def test_forecasts_and_unrelated_sealed_report_preserved(self):
        release = self.release()
        entry = self.start()
        effort.prepare_attach(self.project, entry['id'], release)
        effort.stop(effort.preparation_folder(self.project), entry['id'], 'fixture')
        effort.report(release)
        saved = (release / 'bilan-effort.json').read_bytes()
        self.usage['thread_id'] = 'another'
        self.start()
        effort.check_report(release)
        self.assertEqual(saved, (release / 'bilan-effort.json').read_bytes())
        # No retroactive initial estimate created by either passage.
        self.assertEqual(effort.state(release)['estimates'], [])

    def test_preparation_only_release_requires_report_before_seal(self):
        entry = self.start()
        release = self.release()
        (release / 'effort.json').unlink()  # Synthetic no-plan release.
        effort.prepare_attach(self.project, entry['id'], release)
        with self.assertRaises(ValueError):
            effort.check_closure(release)
        effort.stop(effort.preparation_folder(self.project), entry['id'], 'fixture')
        with self.assertRaises(OSError):
            guard.required_artifacts(release)
        effort.report(release)
        self.assertIn('bilan-effort.json', guard.required_artifacts(release))
        self.assertNotIn('effort.json', guard.required_artifacts(release))

    def test_mutated_attached_ledger_invalidates_report(self):
        entry = self.start()
        release = self.release()
        effort.prepare_attach(self.project, entry['id'], release)
        effort.stop(effort.preparation_folder(self.project), entry['id'], 'fixture')
        effort.report(release)
        folder = effort.preparation_folder(self.project)
        data = effort.state(folder)
        data['entries'][0]['seconds'] = 900
        effort.save(folder, data)
        with self.assertRaises(ValueError):
            effort.check_report(release)

    def test_known_task_transition_counts_only_future_passage(self):
        entry = self.start()
        release = self.release()
        effort.prepare_attach(self.project, entry['id'], release)
        self.clock.update(monotonic=160, boottime=160)
        effort.stop(effort.preparation_folder(self.project), entry['id'], 'fixture')
        effort.add_task(release, 'T01', 'Tâche définie')
        task = effort.start(release, 'T01', 'odoo-developer', 'codex', 'fixture')
        self.clock.update(monotonic=280, boottime=280)
        effort.stop(release, task['id'], 'fixture')
        report = effort.report(release)
        self.assertEqual({r['phase']: r['actual_minutes'] for r in report['rows']}, {'preparation': 1, 'task': 2})
        self.assertEqual(report['totals']['actual_minutes'], 3)

    def test_cli_native_codex_and_claude_counters(self):
        # Subprocesses use the actual native readers, not normalized_usage mocks.
        for provider in ('codex', 'claude'):
            with self.subTest(provider=provider):
                source = self.project / (provider + '.jsonl')
                def raw(amount):
                    if provider == 'codex':
                        return {'type': 'token_usage_record', 'timestamp': '2026-09-11T10:00:00Z',
                                'payload': {'thread_id': provider, 'response_id': str(amount),
                                            'thread_token_usage': {'input_tokens': amount, 'output_tokens': amount,
                                                                  'cached_input_tokens': 0, 'cache_write_input_tokens': 0,
                                                                  'total_tokens': 2 * amount}}}
                    return {'type': 'assistant', 'timestamp': '2026-09-11T10:00:00Z', 'sessionId': provider,
                            'requestId': str(amount), 'message': {'type': 'message', 'id': str(amount), 'model': 'fixture',
                            'usage': {'input_tokens': amount, 'output_tokens': amount,
                                      'cache_read_input_tokens': 0, 'cache_creation_input_tokens': 0}}}
                def cli(*args):
                    run = subprocess.run([sys.executable, effort.__file__, *args], capture_output=True, text=True)
                    self.assertEqual(run.returncode, 0, run.stderr)
                    return json.loads(run.stdout)
                metadata = json.dumps({'type': 'session_meta', 'payload': {'id': provider}}) + '\n' if provider == 'codex' else ''
                source.write_text(metadata + json.dumps(raw(10)) + '\n')
                entry = cli('prepare-start', str(self.project), '--agent', 'odoo-analyst', '--provider', provider, '--source', str(source))
                source.write_text(source.read_text() + json.dumps(raw(30)) + '\n')
                result = cli('prepare-stop', str(self.project), '--entry', entry['id'], '--source', str(source))
                self.assertEqual(result['tokens']['input_tokens'], 20 if provider == 'codex' else 30)
                self.assertEqual(result['tokens']['output_tokens'], 20 if provider == 'codex' else 30)
                self.assertEqual(result['status'], 'complete')


if __name__ == '__main__':
    unittest.main()
