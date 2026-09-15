import copy
import unittest

from quotas import snapshot


def event(**changes):
    value = dict(provider='openai', window='5h', observed_at=100,
                 used_percent=40, reset_at=500)
    value.update(changes)
    return value


class SnapshotTest(unittest.TestCase):
    def test_latest_observation_wins_regardless_of_order_or_reset(self):
        events = [event(observed_at=200, used_percent=10, reset_at=300),
                  event(observed_at=100, used_percent=90, reset_at=1000)]
        expected = dict(used_percent=10, reset_at=300, observed_at=200,
                        stale=False)
        for ordered in (events, events[::-1]):
            self.assertEqual(snapshot(ordered, 250)['openai']['5h'], expected)

    def test_last_valid_event_wins_tie(self):
        events = [event(), event(used_percent=0, reset_at=None),
                  event(used_percent=True)]
        self.assertEqual(snapshot(events, 100)['openai']['5h'],
                         dict(used_percent=0, reset_at=None, observed_at=100,
                              stale=False))

    def test_providers_and_windows_are_independent(self):
        events = [event(provider=provider, window=window, used_percent=amount)
                  for provider, window, amount in
                  [('openai', '5h', 0), ('openai', 'week', 100),
                   ('anthropic', '5h', 25), ('anthropic', 'week', 75)]]
        result = snapshot(events, 100)
        for item in events:
            self.assertEqual(result[item['provider']][item['window']],
                             {key: item[key] for key in
                              ('used_percent', 'reset_at', 'observed_at')}
                             | {'stale': False})

    def test_staleness_boundaries(self):
        for now, ttl, stale in [(400, 300, False), (400.1, 300, True),
                                (100, 0, False), (100.1, 0, True),
                                (101, 1, False)]:
            with self.subTest(now=now, ttl=ttl):
                self.assertIs(snapshot([event()], now, ttl)['openai']['5h']['stale'],
                              stale)
        self.assertTrue(snapshot([event()], 401)['openai']['5h']['stale'])

    def test_invalid_events_never_create_or_replace_observations(self):
        invalid = {
            'provider': ['unknown', None, [], True],
            'window': ['day', None, [], True],
            'observed_at': [None, -1, 1001, float('nan'), float('inf'),
                            -float('inf'), True, False, '200', 200j],
            'used_percent': [None, -0.1, 100.1, float('nan'), float('inf'),
                             -float('inf'), True, False, '50', 50j],
            'reset_at': [-1, 199, float('nan'), float('inf'), -float('inf'),
                         True, False, '500', 500j],
        }
        baseline = snapshot([event()], 1000)
        empty = snapshot([], 1000)
        for field, values in invalid.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    bad = event(observed_at=200)
                    bad[field] = value
                    self.assertEqual(snapshot([bad], 1000), empty)
                    self.assertEqual(snapshot([event(), bad], 1000), baseline)

    def test_missing_required_values(self):
        for field in ('provider', 'window', 'observed_at', 'used_percent'):
            with self.subTest(field=field):
                bad = event()
                del bad[field]
                self.assertEqual(snapshot([bad], 100), snapshot([], 100))

    def test_valid_numeric_boundaries(self):
        for observed_at, used_percent, reset_at in [(0, 0, 0), (0, 100, None),
                                                   (0.5, 42.5, 0.5)]:
            with self.subTest(observed_at=observed_at, used_percent=used_percent):
                result = snapshot([event(observed_at=observed_at,
                                         used_percent=used_percent,
                                         reset_at=reset_at)], 1)
                self.assertEqual(result['openai']['5h'],
                                 dict(observed_at=observed_at,
                                      used_percent=used_percent,
                                      reset_at=reset_at, stale=False))
                self.assertIsNone(result['openai']['week'])

    def test_inputs_and_calls_are_independent(self):
        events = [event(), event(provider='anthropic', window='week'),
                  event(used_percent=-1)]
        original = copy.deepcopy(events)
        result = snapshot(events, 100)
        self.assertEqual(events, original)
        result['openai']['5h']['used_percent'] = 99
        self.assertEqual(events, original)
        self.assertEqual(snapshot(events, 100)['openai']['5h']['used_percent'], 40)


if __name__ == '__main__':
    unittest.main()
