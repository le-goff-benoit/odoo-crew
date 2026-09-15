import math
import unittest

from quotas import snapshot


class SnapshotTest(unittest.TestCase):
    def test_newest_event_wins_and_equal_timestamp_uses_last_event(self):
        events = [
            {"provider": "openai", "window": "5h", "observed_at": 10,
             "used_percent": 10, "reset_at": 20},
            {"provider": "openai", "window": "5h", "observed_at": 11,
             "used_percent": 20, "reset_at": 12},
            {"provider": "openai", "window": "5h", "observed_at": 11,
             "used_percent": 30, "reset_at": None},
        ]

        result = snapshot(events, now=20)

        self.assertEqual(result["openai"]["5h"], {
            "used_percent": 30, "reset_at": None, "observed_at": 11,
            "stale": False,
        })
        self.assertIsNone(result["anthropic"]["week"])

    def test_invalid_events_do_not_replace_a_valid_observation(self):
        valid = {"provider": "anthropic", "window": "week", "observed_at": 20,
                 "used_percent": 40, "reset_at": 25}
        invalid_events = [
            {"provider": "unknown", "window": "week", "observed_at": 30, "used_percent": 1, "reset_at": None},
            {"provider": "anthropic", "window": "month", "observed_at": 30, "used_percent": 1, "reset_at": None},
            {"provider": "anthropic", "window": "week", "observed_at": None, "used_percent": 1, "reset_at": None},
            {"provider": "anthropic", "window": "week", "observed_at": math.nan, "used_percent": 1, "reset_at": None},
            {"provider": "anthropic", "window": "week", "observed_at": math.inf, "used_percent": 1, "reset_at": None},
            {"provider": "anthropic", "window": "week", "observed_at": 101, "used_percent": 1, "reset_at": None},
            {"provider": "anthropic", "window": "week", "observed_at": -1, "used_percent": 1, "reset_at": None},
            {"provider": "anthropic", "window": "week", "observed_at": 30, "used_percent": True, "reset_at": None},
            {"provider": "anthropic", "window": "week", "observed_at": 30, "used_percent": 101, "reset_at": None},
            {"provider": "anthropic", "window": "week", "observed_at": 30, "used_percent": 1, "reset_at": False},
            {"provider": "anthropic", "window": "week", "observed_at": 30, "used_percent": 1, "reset_at": 29},
        ]

        result = snapshot([valid] + invalid_events, now=100)

        self.assertEqual(result["anthropic"]["week"]["used_percent"], 40)
        self.assertEqual(result["anthropic"]["week"]["observed_at"], 20)

    def test_staleness_boundary_and_inputs_are_not_mutated(self):
        event = {"provider": "openai", "window": "week", "observed_at": 100,
                 "used_percent": 0, "reset_at": 100}
        events = [event]

        fresh = snapshot(events, now=400, ttl=300)
        stale = snapshot(events, now=401, ttl=300)

        self.assertFalse(fresh["openai"]["week"]["stale"])
        self.assertTrue(stale["openai"]["week"]["stale"])
        self.assertEqual(event, {
            "provider": "openai", "window": "week", "observed_at": 100,
            "used_percent": 0, "reset_at": 100,
        })
        self.assertIsNot(fresh["openai"]["week"], event)


if __name__ == "__main__":
    unittest.main()
