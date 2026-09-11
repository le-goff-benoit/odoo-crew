"""Prévisions conservées, attribution sans doublon et bilan honnête des coûts/absences."""
from copy import deepcopy
import json
import subprocess
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import odoo_effort as effort
import odoo_release_guard as guard


class EffortTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        self.release = self.project / 'changelog' / 'R1'
        self.release.mkdir(parents=True)
        (self.release / 'README.md').write_text('<!-- release ouverte -->\n# Exemple\n')
        effort.init(self.release)
        self.line = {'task': 'A', 'title': 'Contrôle des prix', 'agent': 'odoo-developer',
                     'optimistic_minutes': 2, 'likely_minutes': 5, 'pessimistic_minutes': 8,
                     'basis': 'Jugement initial, cas synthétique', 'assumptions': ['Copie disponible'], 'confidence': 'low'}
        with patch.object(effort, 'now', return_value='2026-09-01T00:00:00+00:00'):
            effort.estimate(self.release, {'lines': [self.line]})

    def usage(self, thread='thread-1', seconds=360, tokens=True):
        return {'provider': 'codex', 'thread_id': thread, 'model': 'model-test',
                'started_at': '2026-09-09T10:00:00+00:00', 'ended_at': '2026-09-09T10:06:00+00:00',
                'elapsed_seconds': 360, 'active_seconds': seconds, 'complete': True,
                'tokens': {'input_tokens': 1000, 'cached_input_tokens': 600, 'cache_write_input_tokens': 100,
                           'output_tokens': 200, 'total_tokens': 1200} if tokens else None,
                'provider_cost': None, 'source_sha256': thread + '-snapshot', 'warnings': [], 'identities': [thread + '-response']}

    def record(self, usage=None, **kwargs):
        with patch.object(effort, 'normalized_usage', return_value=usage or self.usage()):
            return effort.import_usage(self.release, 'A', 'odoo-developer', 'codex', 'fixture', **kwargs)

    def card(self, **updates):
        result = {'provider': 'codex', 'model': 'model-test', 'effective_at': '2026-01-01T00:00:00+00:00',
                  'currency': 'USD', 'basis': 'api_equivalent', 'source': 'synthetic fixture', 'scope': 'synthetic standard',
                  'input_per_million': '10', 'cached_input_per_million': '1', 'cache_write_input_per_million': '12.5', 'output_per_million': '20'}
        result.update(updates)
        return result

    def test_record_past_task_without_inventing_estimate(self):
        effort.add_task(self.release, 'PAST', 'Travail passé')
        effort.add_task(self.release, 'PAST', 'Travail passé')
        with patch.object(effort, 'normalized_usage', return_value=self.usage()):
            effort.import_usage(self.release, 'PAST', 'odoo-tester', 'codex', 'fixture')
        row = next(r for r in effort.report(self.release)['rows'] if r['task'] == 'PAST')
        self.assertIsNone(row['initial'])
        self.assertIsNone(row['delta_minutes'])
        self.assertEqual(row['actual_minutes'], 6)
        with self.assertRaises(ValueError):
            effort.add_task(self.release, 'PAST', 'Autre travail')
        self.assertEqual(len(effort.state(self.release)['estimates']), 1)

    def test_initial_forecast_preserved_and_revision_requires_reason(self):
        original = deepcopy(effort.state(self.release)['estimates'][0])
        revised = dict(self.line, likely_minutes=6)
        with self.assertRaises(ValueError):
            effort.estimate(self.release, {'lines': [revised]})
        effort.estimate(self.release, {'lines': [revised]}, 'Tests supplémentaires')
        data = effort.state(self.release)
        self.assertEqual(data['estimates'][0], original)
        self.assertEqual(original['lines'][0]['expected_minutes'], 5)
        self.assertAlmostEqual(data['estimates'][1]['lines'][0]['expected_minutes'], 34 / 6)

    def test_invalid_forecasts_do_not_mutate_state(self):
        before = (self.release / 'effort.json').read_bytes()
        for replacement in [{'optimistic_minutes': -1}, {'likely_minutes': 12}, {'pessimistic_minutes': float('nan')},
                            {'likely_minutes': True}, {'assumptions': []}, {'confidence': 'sure'}]:
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                effort.estimate(self.release, {'lines': [dict(self.line, **replacement)]}, 'revision')
        self.assertEqual(before, (self.release / 'effort.json').read_bytes())

    def test_duplicate_forecast_line_refused(self):
        with self.assertRaises(ValueError):
            effort.estimate(self.release, {'lines': [self.line, self.line]}, 'revision')

    def test_absence_does_not_become_zero(self):
        report = effort.report(self.release)
        self.assertIsNone(report['totals']['actual_minutes'])
        self.assertIsNone(report['totals']['tokens'])
        self.assertEqual(report['totals']['known_minutes'], 0)
        self.assertIsNone(report['rows'][0]['delta_minutes'])
        self.assertIn('non mesuré', (self.release / 'bilan-effort.md').read_text())

    def test_idempotent_import_and_refresh_preserve_history(self):
        first = self.record(); self.record()
        self.assertEqual(len(effort.state(self.release)['entries']), 1)
        new = self.usage(); new['source_sha256'] = 'new'; new['tokens'] = {k: v * 2 for k, v in new['tokens'].items()}
        self.record(new)
        entry = effort.state(self.release)['entries'][0]
        self.assertEqual(entry['id'], first['id'])
        self.assertEqual(entry['tokens']['total_tokens'], 2400)
        self.assertEqual(len(entry['history']), 1)

    def test_same_session_cannot_be_charged_to_two_agents_or_releases(self):
        self.record()
        with patch.object(effort, 'normalized_usage', return_value=self.usage()), self.assertRaises(ValueError):
            effort.import_usage(self.release, 'A', 'odoo-tester', 'codex', 'fixture')
        other = self.project / 'changelog' / 'R2'; other.mkdir(); (other / 'README.md').write_text('# R2')
        effort.init(other); effort.estimate(other, {'lines': [self.line]})
        with patch.object(effort, 'normalized_usage', return_value=self.usage()), self.assertRaises(ValueError):
            effort.import_usage(other, 'A', 'odoo-developer', 'codex', 'fixture')

    def test_response_identity_duplicate_rejected_even_different_threads(self):
        self.record(); other = self.usage('thread-2'); other['identities'] = self.usage()['identities']
        with self.assertRaises(ValueError):
            self.record(other)

    def test_disjoint_windows_allowed_overlap_rejected(self):
        self.record(since='2026-09-09T10:00:00Z', until='2026-09-09T10:02:00Z')
        self.record(since='2026-09-09T10:02:00Z', until='2026-09-09T10:06:00Z')
        with self.assertRaises(ValueError):
            self.record(since='2026-09-09T10:01:00Z', until='2026-09-09T10:03:00Z')
        with self.assertRaises(ValueError):
            self.record(since='2026-09-09T10:01:00Z')

    def test_timer_baseline_and_unknown_tokens(self):
        with patch.object(effort, 'clock_snapshot', create=True, return_value={'boot': 'test', 'monotonic': 100, 'boottime': 100}), patch.object(effort, 'now', return_value='2026-09-09T10:00:00+00:00'), patch.object(effort, 'normalized_usage', return_value=self.usage()):
            entry = effort.start(self.release, 'A', 'odoo-developer', 'codex', 'fixture')
        latest = self.usage(); latest['tokens'] = {k: v * 2 for k, v in latest['tokens'].items()}
        with patch.object(effort, 'clock_snapshot', create=True, return_value={'boot': 'test', 'monotonic': 220, 'boottime': 28900}), patch.object(effort, 'now', return_value='2026-09-09T18:02:00+00:00'), patch.object(effort, 'normalized_usage', return_value=latest):
            stopped = effort.stop(self.release, entry['id'], 'fixture')
        self.assertEqual(stopped['seconds'], 120)
        self.assertEqual(stopped['suspended_seconds'], 28680)
        self.assertEqual(stopped['tokens']['total_tokens'], 1200)
        with self.assertRaises(ValueError):
            effort.stop(self.release, entry['id'], 'fixture')
        self.assertIsNone(effort.counter_delta(None, latest['tokens']))

    def test_reboot_interrupts_timer_without_inventing_time(self):
        with patch.object(effort, 'clock_snapshot', create=True, return_value={'boot': 'before', 'monotonic': 100, 'boottime': 100}), patch.object(effort, 'normalized_usage', return_value=self.usage()):
            entry = effort.start(self.release, 'A', 'odoo-developer', 'codex', 'fixture')
        with patch.object(effort, 'clock_snapshot', create=True, return_value={'boot': 'after', 'monotonic': 200, 'boottime': 200}), patch.object(effort, 'normalized_usage', return_value=self.usage()):
            stopped = effort.stop(self.release, entry['id'], 'fixture')
        self.assertEqual(stopped['status'], 'interrupted')
        self.assertIsNone(stopped['seconds'])
        self.assertIn('redémarrage', stopped['interruption_reason'])

    def test_partial_token_delta_preserves_known_fields(self):
        baseline = self.usage()['tokens']
        latest = {k: v * 2 for k, v in baseline.items()}
        latest['cache_write_input_tokens'] = None
        delta = effort.counter_delta(baseline, latest)
        self.assertEqual(delta['output_tokens'], baseline['output_tokens'])
        self.assertIsNone(delta['cache_write_input_tokens'])

    def test_live_clock_is_read_only_and_excludes_suspend(self):
        with patch.object(effort, 'clock_snapshot', return_value={'boot': 'test', 'monotonic': 100, 'boottime': 100}), patch.object(effort, 'normalized_usage', return_value=self.usage()):
            effort.start(self.release, 'A', 'odoo-developer', 'codex', 'fixture')
        original = (self.release / 'effort.json').read_bytes()
        data = effort.state(self.release)
        with patch.object(effort, 'clock_snapshot', return_value={'boot': 'test', 'monotonic': 220, 'boottime': 29020}):
            row = effort.report_data(self.release, data, live=True)['rows'][0]
        self.assertEqual(row['known_minutes'], 2)
        self.assertEqual(row['suspended_seconds'], 28800)
        self.assertFalse(row['time_complete'])
        self.assertIsNone(data['entries'][0]['seconds'])
        self.assertEqual((self.release / 'effort.json').read_bytes(), original)

    def test_legacy_timer_without_clock_does_not_guess_sleep(self):
        with patch.object(effort, 'normalized_usage', return_value=self.usage()):
            entry = effort.start(self.release, 'A', 'odoo-developer', 'codex', 'fixture')
            data = effort.state(self.release)
            del data['entries'][0]['clock_start']
            effort.save(self.release, data)
            stopped = effort.stop(self.release, entry['id'], 'fixture')
        self.assertIsNone(stopped['seconds'])
        self.assertEqual(stopped['status'], 'interrupted')

    def test_partial_tokens_report_and_cost_remain_independent(self):
        sample = self.usage()
        sample['tokens']['cache_write_input_tokens'] = None
        self.record(sample)
        effort.rates(self.release, {'cards': [self.card()]})
        report = effort.report(self.release)
        row = report['rows'][0]
        self.assertEqual(row['tokens']['input_tokens'], 1000)
        self.assertEqual(row['tokens']['output_tokens'], 200)
        self.assertFalse(row['token_complete'])
        self.assertIsNone(row['costs'][0]['cost'])

    def test_historical_report_is_validated_without_rewriting(self):
        self.record(self.usage(tokens=False))
        report = effort.report(self.release)
        report.pop('measurement_version')
        for row in report['rows']:
            row.pop('suspended_seconds')
            if not row['token_complete']:
                row['tokens'] = None
        effort.write(self.release / 'bilan-effort.json', report)
        for name, content in effort.render(report).items():
            (self.release / name).write_text(content)
        before = {name: (self.release / name).read_bytes() for name in effort.REPORT_FILES}
        self.assertEqual(effort.check_report(self.release), report)
        self.assertEqual(before, {name: (self.release / name).read_bytes() for name in effort.REPORT_FILES})

    def test_reserved_clock_is_independent_of_wall_time_and_multiple_suspends(self):
        with patch.object(effort, 'now', side_effect=AssertionError('wall time must not be consulted')):
            actual, suspended, error = effort.clock_duration(
                {'boot': 'same', 'monotonic': 400, 'boottime': 500},
                {'boot': 'same', 'monotonic': 700, 'boottime': 22400})
        self.assertEqual(actual, 300)
        self.assertEqual(suspended, 21600)
        self.assertIsNone(error)
        self.assertIsNone(effort.clock_duration(None, None)[0])
        self.assertIsNone(effort.clock_duration({'boot': 'same', 'monotonic': 10, 'boottime': 10},
                                               {'boot': 'same', 'monotonic': 20, 'boottime': 12})[0])

    def test_timer_other_session_or_counter_regression_refused(self):
        with patch.object(effort, 'normalized_usage', return_value=self.usage()):
            entry = effort.start(self.release, 'A', 'odoo-developer', 'codex', 'fixture')
        with patch.object(effort, 'normalized_usage', return_value=self.usage('other')), self.assertRaises(ValueError):
            effort.stop(self.release, entry['id'], 'fixture')
        smaller = self.usage(); smaller['tokens']['total_tokens'] = 2
        with patch.object(effort, 'normalized_usage', return_value=smaller), self.assertRaises(ValueError):
            effort.stop(self.release, entry['id'], 'fixture')
        self.assertEqual(effort.state(self.release)['entries'][0]['status'], 'running')

    def test_new_seal_refuses_running_timer_without_altering_it(self):
        with patch.object(effort, 'normalized_usage', return_value=self.usage()):
            entry = effort.start(self.release, 'A', 'odoo-developer', 'codex', 'fixture')
        effort.report(self.release)
        before = (self.release / 'effort.json').read_bytes()
        # Existing report/closure readers remain compatible with historical data.
        self.assertTrue(effort.check_report(self.release))
        with self.assertRaisesRegex(ValueError, 'chronomètre.*' + entry['id']):
            guard.seal(self.release, [], [])
        self.assertEqual(before, (self.release / 'effort.json').read_bytes())
        self.assertFalse((self.release / 'closure.json').exists())

    def test_interruption_preserves_unknown_time_and_allows_future_work(self):
        with patch.object(effort, 'now', return_value='2026-09-09T10:00:00+00:00'), patch.object(effort, 'normalized_usage', return_value=self.usage()):
            entry = effort.start(self.release, 'A', 'odoo-developer', 'codex', 'fixture')
        with patch.object(effort, 'now', return_value='2026-09-09T10:02:00+00:00'):
            interrupted = effort.interrupt(self.release, entry['id'], 'Attente humaine non isolée, borne de fin inconnue')
        self.assertIsNone(interrupted['seconds'])
        self.assertIsNone(interrupted['tokens'])
        self.assertIsNone(interrupted['ended_at'])
        self.assertEqual(interrupted['baseline'], entry['baseline'])
        self.assertEqual(interrupted['status'], 'interrupted')
        report = effort.report(self.release)
        self.assertIsNone(report['totals']['actual_minutes'])
        self.assertIsNone(report['totals']['envelope_minutes'])
        self.assertTrue(effort.check_closure(self.release))
        with patch.object(effort, 'now', return_value='2026-09-09T10:03:00+00:00'), patch.object(effort, 'normalized_usage', return_value=self.usage()):
            effort.start(self.release, 'A', 'odoo-developer', 'codex', 'fixture')
        self.assertEqual(len(effort.state(self.release)['entries']), 2)

    def test_interruption_requires_reason_and_an_active_timer(self):
        with patch.object(effort, 'normalized_usage', return_value=self.usage()):
            entry = effort.start(self.release, 'A', 'odoo-developer', 'codex', 'fixture')
        before = (self.release / 'effort.json').read_bytes()
        for reason in ('', '   '):
            with self.assertRaises(ValueError):
                effort.interrupt(self.release, entry['id'], reason)
        self.assertEqual(before, (self.release / 'effort.json').read_bytes())
        effort.interrupt(self.release, entry['id'], 'Trace perdue')
        with self.assertRaises(ValueError):
            effort.interrupt(self.release, entry['id'], 'Deuxième fois')

    def test_closure_check_accepts_absent_or_partial_tracking_without_zero(self):
        self.record()
        effort.estimate(self.release, {'lines': [dict(self.line, agent='odoo-tester')]}, 'QA à venir')
        result = effort.check_closure(self.release)
        self.assertEqual(result['known_minutes'], 6)
        self.assertEqual(result['missing_roles'], [{'task': 'A', 'agent': 'odoo-tester'}])
        self.assertFalse(result['complete'])
        (self.release / 'effort.json').unlink()
        self.assertEqual(effort.check_closure(self.release), {'tracking': False})

    def test_interruption_cli_and_readonly_preflight(self):
        with patch.object(effort, 'normalized_usage', return_value=self.usage()):
            entry = effort.start(self.release, 'A', 'odoo-developer', 'codex', 'fixture')
        command = [sys.executable, effort.__file__]
        result = subprocess.run(command + ['check-closure', str(self.release)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn(entry['id'], result.stderr)
        result = subprocess.run(command + ['interrupt', str(self.release), '--entry', entry['id'], '--reason', 'Trace perdue'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsNone(json.loads(result.stdout)['seconds'])
        result = subprocess.run(command + ['check-closure', str(self.release)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)['complete'])

    def test_cumulative_agent_time_is_not_elapsed_time(self):
        self.record(); self.record(self.usage('thread-2'))
        report = effort.report(self.release)
        self.assertEqual(report['totals']['actual_minutes'], 12)
        self.assertEqual(report['totals']['envelope_minutes'], 6)
        self.assertEqual(report['totals']['covered_interval_minutes'], 6)
        self.assertEqual(report['rows'][0]['delta_minutes'], 7)

    def test_incomplete_or_missing_active_duration_remains_unknown(self):
        usage = self.usage(seconds=None); usage['complete'] = False
        self.record(usage)
        report = effort.report(self.release)
        self.assertIsNone(report['rows'][0]['actual_minutes'])
        self.assertIsNone(report['totals']['tokens'])
        self.assertEqual(report['totals']['known_tokens'], 1200)

    def test_cache_cost_and_missing_tariff(self):
        self.record()
        report = effort.report(self.release)
        self.assertEqual(report['totals']['known_costs'], {})
        self.assertEqual(report['totals']['unpriced_entries'], 1)
        effort.rates(self.release, {'cards': [self.card()]})
        report = effort.report(self.release); charge = report['rows'][0]['costs'][0]['cost']
        self.assertAlmostEqual(charge['amount'], .003 + .0006 + .00125 + .004)
        self.assertEqual(charge['kind'], 'calculated')
        self.assertEqual(charge['basis'], 'api_equivalent')

    def test_declared_cost_not_repriced_or_mixed_with_currency(self):
        usage = self.usage(); usage['provider_cost'] = {'amount': 2, 'currency': 'CHF', 'basis': 'native'}
        self.record(usage)
        effort.rates(self.release, {'cards': [self.card()]})
        report = effort.report(self.release)
        self.assertEqual(report['totals']['known_costs'], {'declared:native:CHF': 2})

    def test_tariffs_immutable_and_period_ambiguity_not_priced(self):
        card = self.card(); effort.rates(self.release, {'cards': [card]})
        with self.assertRaises(ValueError):
            effort.rates(self.release, {'cards': [self.card(output_per_million=99)]})
        self.record(); effort.rates(self.release, {'cards': [self.card(effective_at='2026-09-09T10:03:00Z')]})
        self.assertEqual(effort.report(self.release)['totals']['unpriced_entries'], 1)

    def test_retrospective_forecast_not_a_valid_variance(self):
        data = effort.state(self.release); data['estimates'][0]['at'] = '2026-09-10T00:00:00Z'; effort.save(self.release, data)
        self.record(); row = effort.report(self.release)['rows'][0]
        self.assertTrue(row['retrospective'])
        self.assertIsNone(row['delta_minutes'])

    def test_scope_change_even_with_new_revision_blocks_initial_comparison(self):
        data = effort.state(self.release); data['estimates'][0]['lines'][0]['contract_sha256'] = 'old'; effort.save(self.release, data)
        with patch.object(effort, 'contracts', return_value={'A': {'title': 'Changed', 'sha256': 'new'}}):
            effort.estimate(self.release, {'lines': [self.line]}, 'Nouveau périmètre')
            self.record(); report = effort.report(self.release)
        self.assertTrue(report['rows'][0]['scope_changed'])
        self.assertIsNone(report['rows'][0]['delta_minutes'])

    def test_unestimated_task_and_missing_actual_are_visible(self):
        data = effort.state(self.release); data['tasks']['B'] = 'QA'; effort.save(self.release, data)
        self.record(); report = effort.report(self.release)
        self.assertEqual(report['missing_tasks'], ['B'])
        self.assertIsNone(report['totals']['actual_minutes'])

    def test_csv_formula_injection_escaped(self):
        data = effort.state(self.release); data['tasks']['A'] = '=1+1'; effort.save(self.release, data)
        effort.report(self.release)
        self.assertIn("'=1+1", (self.release / 'bilan-effort.csv').read_text())

    def test_report_freshness_and_tampering_checked_for_closure(self):
        effort.report(self.release)
        self.assertIn('effort.json', guard.required_artifacts(self.release))
        (self.release / 'bilan-effort.md').write_text('Everything passed, free!')
        with self.assertRaises(ValueError):
            guard.required_artifacts(self.release)
        effort.report(self.release); self.record()
        with self.assertRaises(ValueError):
            effort.check_report(self.release)
        effort.report(self.release); self.assertTrue(effort.check_report(self.release))

    def test_old_release_without_tracking_still_compatible(self):
        (self.release / 'effort.json').unlink()
        self.assertEqual(guard.required_artifacts(self.release), guard.REQUIRED)

    def test_naive_dates_and_negative_money_refused(self):
        with self.assertRaises(ValueError):
            effort.rates(self.release, {'cards': [self.card(effective_at='2026-01-01T00:00:00')]})
        with self.assertRaises(ValueError):
            effort.rates(self.release, {'cards': [self.card(input_per_million=-1)]})

    def test_equivalent_tariff_timezones_cannot_reprice_history(self):
        effort.rates(self.release, {'cards': [self.card(effective_at='2026-01-01T00:00:00Z')]})
        with self.assertRaises(ValueError):
            effort.rates(self.release, {'cards': [self.card(effective_at='2026-01-01T01:00:00+01:00', input_per_million=99)]})

    def test_request_change_without_plan_invalidates_comparison_and_report(self):
        self.record(); effort.report(self.release)
        (self.release / 'demande.md').write_text('Ajout de périmètre')
        with self.assertRaises(ValueError):
            effort.check_report(self.release)
        row = effort.report(self.release)['rows'][0]
        self.assertTrue(row['scope_changed'])
        self.assertIsNone(row['delta_minutes'])

    def test_partial_revision_preserves_other_agents(self):
        effort.estimate(self.release, {'lines': [dict(self.line, agent='odoo-tester')]}, 'Ajout QA')
        effort.estimate(self.release, {'lines': [dict(self.line, likely_minutes=6)]}, 'Révision dev')
        self.assertEqual(len(effort.state(self.release)['estimates'][-1]['lines']), 2)

    def test_timer_preserves_declared_cost_and_resolves_late_model(self):
        baseline = self.usage(); baseline['model'] = None
        baseline['provider_cost'] = {'amount': 1, 'currency': 'USD', 'basis': 'native'}
        with patch.object(effort, 'normalized_usage', return_value=baseline):
            entry = effort.start(self.release, 'A', 'odoo-developer', 'claude', 'fixture')
        final = self.usage(); final['provider_cost'] = {'amount': 3, 'currency': 'USD', 'basis': 'native'}
        with patch.object(effort, 'normalized_usage', return_value=final):
            result = effort.stop(self.release, entry['id'], 'fixture')
        self.assertEqual(result['model'], 'model-test')
        self.assertEqual(result['provider_cost']['amount'], 2)
        self.assertEqual(result['estimate_revision'], 1)

    def test_stopped_timer_rejects_alias_response_import(self):
        with patch.object(effort, 'normalized_usage', return_value=self.usage()):
            timer = effort.start(self.release, 'A', 'odoo-developer', 'codex', 'fixture')
            effort.stop(self.release, timer['id'], 'fixture')
        alias = self.usage('other'); alias['identities'] = self.usage()['identities']
        with self.assertRaises(ValueError):
            self.record(alias)
