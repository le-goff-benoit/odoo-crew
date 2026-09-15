import copy
import math
import unittest

from quotas import snapshot

EMPTY = {'openai': {'5h': None, 'week': None},
         'anthropic': {'5h': None, 'week': None}}


def event(provider='openai', window='5h', observed_at=900, used_percent=40, reset_at=None):
    return {'provider': provider, 'window': window, 'observed_at': observed_at,
            'used_percent': used_percent, 'reset_at': reset_at}


class ShapeTest(unittest.TestCase):
    def test_all_slots_always_present(self):
        result = snapshot([event()], 1000)
        self.assertEqual(sorted(result), ['anthropic', 'openai'])
        for provider in ('openai', 'anthropic'):
            self.assertEqual(sorted(result[provider]), ['5h', 'week'])

    def test_observation_fields(self):
        result = snapshot([event(used_percent=61.5, reset_at=1500)], 1000)
        self.assertEqual(result['openai']['5h'],
                         {'used_percent': 61.5, 'reset_at': 1500,
                          'observed_at': 900, 'stale': False})

    def test_inputs_are_not_modified(self):
        events = [event(), event(provider='anthropic', window='week', observed_at=100),
                  event(provider='ghost'), event(used_percent=None)]
        reference = copy.deepcopy(events)
        snapshot(events, 1000)
        self.assertEqual(events, reference)

    def test_result_does_not_alias_input_events(self):
        events = [event()]
        result = snapshot(events, 1000)
        result['openai']['5h']['used_percent'] = 99
        self.assertEqual(events[0]['used_percent'], 40)


class IsolationTest(unittest.TestCase):
    def test_providers_and_windows_stay_separate(self):
        events = [event('openai', '5h', 900, 10), event('openai', 'week', 900, 20),
                  event('anthropic', '5h', 900, 30), event('anthropic', 'week', 900, 40)]
        result = snapshot(events, 1000)
        self.assertEqual(result['openai']['5h']['used_percent'], 10)
        self.assertEqual(result['openai']['week']['used_percent'], 20)
        self.assertEqual(result['anthropic']['5h']['used_percent'], 30)
        self.assertEqual(result['anthropic']['week']['used_percent'], 40)

    def test_never_sums_repeated_observations(self):
        events = [event(observed_at=800, used_percent=30), event(observed_at=900, used_percent=30)]
        self.assertEqual(snapshot(events, 1000)['openai']['5h']['used_percent'], 30)

    def test_absent_window_is_none_not_zero(self):
        result = snapshot([event('openai', '5h')], 1000)
        self.assertIsNone(result['openai']['week'])
        self.assertIsNone(result['anthropic']['5h'])
        self.assertIsNone(result['anthropic']['week'])


class RecencyTest(unittest.TestCase):
    def test_most_recent_wins_regardless_of_order(self):
        events = [event(observed_at=950, used_percent=70), event(observed_at=800, used_percent=10)]
        self.assertEqual(snapshot(events, 1000)['openai']['5h']['used_percent'], 70)

    def test_most_recent_wins_even_with_different_reset(self):
        events = [event(observed_at=800, used_percent=10, reset_at=5000),
                  event(observed_at=950, used_percent=70, reset_at=None)]
        self.assertEqual(snapshot(events, 1000)['openai']['5h'],
                         {'used_percent': 70, 'reset_at': None, 'observed_at': 950, 'stale': False})

    def test_tie_goes_to_last_event_in_list(self):
        events = [event(observed_at=900, used_percent=10, reset_at=1200),
                  event(observed_at=900, used_percent=90, reset_at=None)]
        self.assertEqual(snapshot(events, 1000)['openai']['5h'],
                         {'used_percent': 90, 'reset_at': None, 'observed_at': 900, 'stale': False})

    def test_older_event_after_newer_does_not_win(self):
        events = [event(observed_at=900, used_percent=90), event(observed_at=899, used_percent=1)]
        self.assertEqual(snapshot(events, 1000)['openai']['5h']['observed_at'], 900)


class StaleTest(unittest.TestCase):
    def test_equality_is_fresh(self):
        self.assertFalse(snapshot([event(observed_at=700)], 1000, ttl=300)['openai']['5h']['stale'])

    def test_just_beyond_ttl_is_stale(self):
        self.assertTrue(snapshot([event(observed_at=699)], 1000, ttl=300)['openai']['5h']['stale'])

    def test_zero_ttl_same_instant_is_fresh(self):
        self.assertFalse(snapshot([event(observed_at=1000)], 1000, ttl=0)['openai']['5h']['stale'])

    def test_default_ttl_is_300(self):
        self.assertTrue(snapshot([event(observed_at=500)], 1000)['openai']['5h']['stale'])

    def test_stale_winner_still_beats_fresh_older_event(self):
        events = [event(observed_at=100, used_percent=5), event(observed_at=200, used_percent=50)]
        result = snapshot(events, 10000, ttl=300)['openai']['5h']
        self.assertEqual(result['used_percent'], 50)
        self.assertTrue(result['stale'])


class RejectionTest(unittest.TestCase):
    def assertRejected(self, bad):
        self.assertEqual(snapshot([bad], 1000), EMPTY)

    def test_unknown_provider(self):
        self.assertRejected(event(provider='mistral'))

    def test_unknown_window(self):
        self.assertRejected(event(window='day'))

    def test_missing_provider_or_window_key(self):
        for key in ('provider', 'window'):
            bad = event()
            del bad[key]
            self.assertRejected(bad)

    def test_case_sensitive_names(self):
        self.assertRejected(event(provider='OpenAI'))
        self.assertRejected(event(window='WEEK'))

    def test_missing_or_none_observed_at(self):
        self.assertRejected(event(observed_at=None))
        bad = event()
        del bad['observed_at']
        self.assertRejected(bad)

    def test_non_numeric_observed_at(self):
        for value in ('900', [900], {}, object()):
            self.assertRejected(event(observed_at=value))

    def test_nan_and_infinite_observed_at(self):
        for value in (float('nan'), float('inf'), float('-inf')):
            self.assertRejected(event(observed_at=value))

    def test_future_observed_at(self):
        self.assertRejected(event(observed_at=1001))

    def test_negative_observed_at(self):
        self.assertRejected(event(observed_at=-1))

    def test_boolean_observed_at(self):
        for value in (True, False):
            self.assertRejected(event(observed_at=value))

    def test_percent_out_of_range(self):
        for value in (-0.1, 100.1, 101, -5):
            self.assertRejected(event(used_percent=value))

    def test_percent_non_numeric_or_missing(self):
        for value in ('40', None, [40], {}):
            self.assertRejected(event(used_percent=value))
        bad = event()
        del bad['used_percent']
        self.assertRejected(bad)

    def test_percent_nan_or_infinite(self):
        for value in (float('nan'), float('inf'), float('-inf')):
            self.assertRejected(event(used_percent=value))

    def test_boolean_percent(self):
        for value in (True, False):
            self.assertRejected(event(used_percent=value))

    def test_reset_at_non_numeric(self):
        for value in ('1200', [1200], {}, object()):
            self.assertRejected(event(reset_at=value))

    def test_boolean_reset_at(self):
        for value in (True, False):
            self.assertRejected(event(reset_at=value))

    def test_reset_at_nan_or_infinite(self):
        for value in (float('nan'), float('inf'), float('-inf')):
            self.assertRejected(event(reset_at=value))

    def test_reset_at_before_observed_at(self):
        self.assertRejected(event(observed_at=900, reset_at=899))

    def test_negative_reset_at(self):
        self.assertRejected(event(observed_at=900, reset_at=-1))

    def test_non_dict_event(self):
        for bad in (None, 42, 'openai', ['openai', '5h'], object()):
            self.assertRejected(bad)


class AcceptanceTest(unittest.TestCase):
    def test_percent_bounds_are_inclusive(self):
        for value in (0, 0.0, 100, 100.0):
            result = snapshot([event(used_percent=value)], 1000)['openai']['5h']
            self.assertEqual(result['used_percent'], value)

    def test_reset_at_equal_to_observed_at_is_valid(self):
        result = snapshot([event(observed_at=900, reset_at=900)], 1000)['openai']['5h']
        self.assertEqual(result['reset_at'], 900)

    def test_reset_at_none_is_valid(self):
        self.assertIsNone(snapshot([event(reset_at=None)], 1000)['openai']['5h']['reset_at'])

    def test_observed_at_equal_now_is_valid(self):
        self.assertEqual(snapshot([event(observed_at=1000)], 1000)['openai']['5h']['observed_at'], 1000)

    def test_zero_timestamps_are_valid(self):
        result = snapshot([event(observed_at=0, reset_at=0)], 0)['openai']['5h']
        self.assertEqual(result, {'used_percent': 40, 'reset_at': 0,
                                  'observed_at': 0, 'stale': False})


class MaskingTest(unittest.TestCase):
    def test_invalid_later_event_does_not_hide_valid_one(self):
        events = [event(observed_at=900, used_percent=40),
                  event(observed_at=950, used_percent=None)]
        self.assertEqual(snapshot(events, 1000)['openai']['5h']['used_percent'], 40)

    def test_future_event_does_not_hide_valid_one(self):
        events = [event(observed_at=900, used_percent=40), event(observed_at=9999, used_percent=99)]
        self.assertEqual(snapshot(events, 1000)['openai']['5h']['observed_at'], 900)

    def test_bad_reset_does_not_hide_valid_one(self):
        events = [event(observed_at=900, used_percent=40, reset_at=1500),
                  event(observed_at=950, used_percent=99, reset_at=10)]
        self.assertEqual(snapshot(events, 1000)['openai']['5h'],
                         {'used_percent': 40, 'reset_at': 1500,
                          'observed_at': 900, 'stale': False})

    def test_invalid_events_alone_leave_everything_unknown(self):
        events = [event(provider='ghost'), event(window='month'),
                  event(observed_at=math.nan), event(used_percent=200), None]
        self.assertEqual(snapshot(events, 1000), EMPTY)

    def test_invalid_event_does_not_leak_into_other_slot(self):
        events = [event('openai', '5h', 900, 40), event('anthropic', 'week', 950, 'bad')]
        result = snapshot(events, 1000)
        self.assertEqual(result['openai']['5h']['used_percent'], 40)
        self.assertIsNone(result['anthropic']['week'])


class MixedStreamTest(unittest.TestCase):
    def test_realistic_stream(self):
        events = [
            event('openai', '5h', 100, 12, 4000),
            {'provider': 'openai', 'window': '5h'},
            event('openai', '5h', 940, 55, 4000),
            event('openai', 'week', 940, 80, None),
            event('anthropic', '5h', 300, 5, 3000),
            event('anthropic', '5h', 300, 6, 3000),
            event('anthropic', 'week', 2000, 99, 9000),
        ]
        self.assertEqual(snapshot(events, 1000, ttl=100), {
            'openai': {
                '5h': {'used_percent': 55, 'reset_at': 4000, 'observed_at': 940, 'stale': False},
                'week': {'used_percent': 80, 'reset_at': None, 'observed_at': 940, 'stale': False},
            },
            'anthropic': {
                '5h': {'used_percent': 6, 'reset_at': 3000, 'observed_at': 300, 'stale': True},
                'week': None,
            },
        })


if __name__ == '__main__':
    unittest.main()
