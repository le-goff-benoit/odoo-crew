"""Prévisions conservées, attribution sans doublon et bilan honnête des coûts/absences."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
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
        with patch.object(effort, 'now', return_value='2026-09-09T10:00:00+00:00'), patch.object(effort, 'normalized_usage', return_value=self.usage()):
            entry = effort.start(self.release, 'A', 'odoo-developer', 'codex', 'fixture')
        latest = self.usage(); latest['tokens'] = {k: v * 2 for k, v in latest['tokens'].items()}
        with patch.object(effort, 'now', return_value='2026-09-09T10:02:00+00:00'), patch.object(effort, 'normalized_usage', return_value=latest):
            stopped = effort.stop(self.release, entry['id'], 'fixture')
        self.assertEqual(stopped['seconds'], 120)
        self.assertEqual(stopped['tokens']['total_tokens'], 1200)
        with self.assertRaises(ValueError):
            effort.stop(self.release, entry['id'], 'fixture')
        self.assertIsNone(effort.counter_delta(None, latest['tokens']))

    def test_timer_other_session_or_counter_regression_refused(self):
        with patch.object(effort, 'normalized_usage', return_value=self.usage()):
            entry = effort.start(self.release, 'A', 'odoo-developer', 'codex', 'fixture')
        with patch.object(effort, 'normalized_usage', return_value=self.usage('other')), self.assertRaises(ValueError):
            effort.stop(self.release, entry['id'], 'fixture')
        smaller = self.usage(); smaller['tokens']['total_tokens'] = 2
        with patch.object(effort, 'normalized_usage', return_value=smaller), self.assertRaises(ValueError):
            effort.stop(self.release, entry['id'], 'fixture')
        self.assertEqual(effort.state(self.release)['entries'][0]['status'], 'running')

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
