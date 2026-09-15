import math
import unittest

from quotas import snapshot


class SnapshotTest(unittest.TestCase):
    def test_single_valid_observation(self):
        events = [{
            'provider': 'openai', 'window': '5h',
            'observed_at': 100, 'used_percent': 42, 'reset_at': 200,
        }]
        result = snapshot(events, now=150, ttl=300)
        self.assertEqual(result['openai']['5h'], {
            'used_percent': 42, 'reset_at': 200, 'observed_at': 100, 'stale': False,
        })
        self.assertIsNone(result['openai']['week'])
        self.assertIsNone(result['anthropic']['5h'])
        self.assertIsNone(result['anthropic']['week'])

    def test_reset_at_none_is_allowed(self):
        events = [{
            'provider': 'anthropic', 'window': 'week',
            'observed_at': 10, 'used_percent': 0, 'reset_at': None,
        }]
        result = snapshot(events, now=10, ttl=5)
        self.assertEqual(result['anthropic']['week']['reset_at'], None)

    def test_latest_observed_at_wins_even_with_different_reset(self):
        events = [
            {'provider': 'openai', 'window': '5h', 'observed_at': 50,
             'used_percent': 10, 'reset_at': 999},
            {'provider': 'openai', 'window': '5h', 'observed_at': 80,
             'used_percent': 90, 'reset_at': 81},
        ]
        result = snapshot(events, now=100, ttl=300)
        self.assertEqual(result['openai']['5h']['used_percent'], 90)
        self.assertEqual(result['openai']['5h']['reset_at'], 81)

    def test_tie_on_observed_at_last_in_list_wins(self):
        events = [
            {'provider': 'openai', 'window': '5h', 'observed_at': 50,
             'used_percent': 10, 'reset_at': None},
            {'provider': 'openai', 'window': '5h', 'observed_at': 50,
             'used_percent': 55, 'reset_at': None},
        ]
        result = snapshot(events, now=100, ttl=300)
        self.assertEqual(result['openai']['5h']['used_percent'], 55)

    def test_invalid_event_does_not_mask_previous_valid_observation(self):
        events = [
            {'provider': 'openai', 'window': '5h', 'observed_at': 50,
             'used_percent': 10, 'reset_at': None},
            {'provider': 'openai', 'window': '5h', 'observed_at': 90,
             'used_percent': 200, 'reset_at': None},  # invalid: out of range
        ]
        result = snapshot(events, now=100, ttl=300)
        self.assertEqual(result['openai']['5h']['used_percent'], 10)

    def test_unknown_provider_or_window_ignored(self):
        events = [
            {'provider': 'mistral', 'window': '5h', 'observed_at': 1,
             'used_percent': 1, 'reset_at': None},
            {'provider': 'openai', 'window': 'month', 'observed_at': 1,
             'used_percent': 1, 'reset_at': None},
        ]
        result = snapshot(events, now=10, ttl=300)
        self.assertIsNone(result['openai']['5h'])
        self.assertIsNone(result['openai']['week'])

    def test_missing_or_none_observed_at_invalid(self):
        events = [
            {'provider': 'openai', 'window': '5h', 'used_percent': 1, 'reset_at': None},
            {'provider': 'openai', 'window': 'week', 'observed_at': None,
             'used_percent': 1, 'reset_at': None},
        ]
        result = snapshot(events, now=10, ttl=300)
        self.assertIsNone(result['openai']['5h'])
        self.assertIsNone(result['openai']['week'])

    def test_nan_and_infinite_rejected(self):
        events = [
            {'provider': 'openai', 'window': '5h', 'observed_at': math.nan,
             'used_percent': 1, 'reset_at': None},
            {'provider': 'openai', 'window': 'week', 'observed_at': 1,
             'used_percent': math.inf, 'reset_at': None},
        ]
        result = snapshot(events, now=10, ttl=300)
        self.assertIsNone(result['openai']['5h'])
        self.assertIsNone(result['openai']['week'])

    def test_future_observed_at_rejected(self):
        events = [{
            'provider': 'openai', 'window': '5h', 'observed_at': 101,
            'used_percent': 1, 'reset_at': None,
        }]
        result = snapshot(events, now=100, ttl=300)
        self.assertIsNone(result['openai']['5h'])

    def test_used_percent_out_of_range_or_non_numeric_rejected(self):
        events = [
            {'provider': 'openai', 'window': '5h', 'observed_at': 1,
             'used_percent': -1, 'reset_at': None},
            {'provider': 'openai', 'window': 'week', 'observed_at': 1,
             'used_percent': 101, 'reset_at': None},
            {'provider': 'anthropic', 'window': '5h', 'observed_at': 1,
             'used_percent': 'high', 'reset_at': None},
        ]
        result = snapshot(events, now=10, ttl=300)
        self.assertIsNone(result['openai']['5h'])
        self.assertIsNone(result['openai']['week'])
        self.assertIsNone(result['anthropic']['5h'])

    def test_boolean_used_percent_rejected(self):
        events = [{
            'provider': 'openai', 'window': '5h', 'observed_at': 1,
            'used_percent': True, 'reset_at': None,
        }]
        result = snapshot(events, now=10, ttl=300)
        self.assertIsNone(result['openai']['5h'])

    def test_boolean_observed_at_rejected(self):
        events = [{
            'provider': 'openai', 'window': '5h', 'observed_at': True,
            'used_percent': 50, 'reset_at': None,
        }]
        result = snapshot(events, now=10, ttl=300)
        self.assertIsNone(result['openai']['5h'])

    def test_boolean_reset_at_rejected(self):
        events = [{
            'provider': 'openai', 'window': '5h', 'observed_at': 1,
            'used_percent': 50, 'reset_at': False,
        }]
        result = snapshot(events, now=10, ttl=300)
        self.assertIsNone(result['openai']['5h'])

    def test_non_numeric_reset_at_rejected(self):
        events = [{
            'provider': 'openai', 'window': '5h', 'observed_at': 1,
            'used_percent': 50, 'reset_at': 'later',
        }]
        result = snapshot(events, now=10, ttl=300)
        self.assertIsNone(result['openai']['5h'])

    def test_reset_at_before_observed_at_rejected(self):
        events = [{
            'provider': 'openai', 'window': '5h', 'observed_at': 50,
            'used_percent': 50, 'reset_at': 49,
        }]
        result = snapshot(events, now=100, ttl=300)
        self.assertIsNone(result['openai']['5h'])

    def test_reset_at_equal_observed_at_allowed(self):
        events = [{
            'provider': 'openai', 'window': '5h', 'observed_at': 50,
            'used_percent': 50, 'reset_at': 50,
        }]
        result = snapshot(events, now=100, ttl=300)
        self.assertIsNotNone(result['openai']['5h'])

    def test_negative_observed_at_rejected(self):
        events = [{
            'provider': 'openai', 'window': '5h', 'observed_at': -1,
            'used_percent': 50, 'reset_at': None,
        }]
        result = snapshot(events, now=10, ttl=300)
        self.assertIsNone(result['openai']['5h'])

    def test_negative_reset_at_rejected(self):
        events = [{
            'provider': 'openai', 'window': '5h', 'observed_at': 1,
            'used_percent': 50, 'reset_at': -1,
        }]
        result = snapshot(events, now=10, ttl=300)
        self.assertIsNone(result['openai']['5h'])

    def test_stale_flag_true_when_over_ttl(self):
        events = [{
            'provider': 'openai', 'window': '5h', 'observed_at': 0,
            'used_percent': 50, 'reset_at': None,
        }]
        result = snapshot(events, now=301, ttl=300)
        self.assertTrue(result['openai']['5h']['stale'])

    def test_stale_flag_false_when_exactly_at_ttl(self):
        events = [{
            'provider': 'openai', 'window': '5h', 'observed_at': 0,
            'used_percent': 50, 'reset_at': None,
        }]
        result = snapshot(events, now=300, ttl=300)
        self.assertFalse(result['openai']['5h']['stale'])

    def test_events_not_mutated(self):
        event = {
            'provider': 'openai', 'window': '5h', 'observed_at': 1,
            'used_percent': 50, 'reset_at': None,
        }
        events = [dict(event)]
        snapshot(events, now=10, ttl=300)
        self.assertEqual(events[0], event)

    def test_all_four_slots_independent_no_summing(self):
        events = [
            {'provider': 'openai', 'window': '5h', 'observed_at': 1,
             'used_percent': 30, 'reset_at': None},
            {'provider': 'openai', 'window': 'week', 'observed_at': 1,
             'used_percent': 40, 'reset_at': None},
            {'provider': 'anthropic', 'window': '5h', 'observed_at': 1,
             'used_percent': 50, 'reset_at': None},
            {'provider': 'anthropic', 'window': 'week', 'observed_at': 1,
             'used_percent': 60, 'reset_at': None},
        ]
        result = snapshot(events, now=10, ttl=300)
        self.assertEqual(result['openai']['5h']['used_percent'], 30)
        self.assertEqual(result['openai']['week']['used_percent'], 40)
        self.assertEqual(result['anthropic']['5h']['used_percent'], 50)
        self.assertEqual(result['anthropic']['week']['used_percent'], 60)


if __name__ == '__main__':
    unittest.main()
