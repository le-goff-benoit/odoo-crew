"""Native usage is measured from synthetic sessions, never client projects."""

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "odoo_usage.py"
SPEC = importlib.util.spec_from_file_location("odoo_usage", SCRIPT)
usage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(usage)


def stamp(second):
    return f"2026-09-09T00:00:{second:02d}Z"


def row(kind, second=0, **payload):
    return {"type": kind, "timestamp": stamp(second), "payload": payload}


def counters(inputs=100, cached=50, writes=0, output=20):
    return dict(zip(usage.TOKEN_KEYS, (inputs, cached, writes, output, inputs + output)))


def meta(identity="own"):
    return row("session_meta", id=identity, timestamp=stamp(0))


def count(second=10, response="r1", **values):
    return row("token_usage_record", second, response_id=response,
               thread_id="own", thread_token_usage=counters(**values))


def context(second=1, turn="t1", model="model-a"):
    return row("turn_context", second, turn_id=turn, model=model)


def done(second=10, turn="t1", duration=9000):
    return row("event_msg", second, type="task_complete", turn_id=turn, duration_ms=duration)


def claude(second=10, identity="m1", output=20, **extra):
    return {"type": "assistant", "timestamp": stamp(second), "sessionId": "claude-session",
            "requestId": "request-" + identity,
            "message": {"type": "message", "id": identity, "model": "claude-model",
                        "usage": {"input_tokens": 10, "cache_read_input_tokens": 30,
                                  "cache_creation_input_tokens": 5, "output_tokens": output},
                        "content": [{"type": "text", "text": "PRIVATE CONTENT MUST NEVER ESCAPE"}]},
            **extra}


def claude_done(second=12, duration=11000):
    return {"type": "system", "subtype": "turn_duration", "timestamp": stamp(second),
            "sessionId": "claude-session", "durationMs": duration}


class NativeUsageTests(unittest.TestCase):
    def test_completed_turn_with_missing_duration_is_not_full_active_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'partial.jsonl'
            rows = [meta(), context(), count(), done(), context(11, turn='t2'),
                    row('event_msg', 20, type='task_complete', turn_id='t2')]
            path.write_text(''.join(json.dumps(r) + '\n' for r in rows))
            result = usage.read_usage(path, 'codex')
        self.assertTrue(result['complete'])
        self.assertIsNone(result['active_seconds'])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "session.jsonl"

    def read(self, rows, provider="codex", **bounds):
        self.path.write_text("".join(json.dumps(item) + "\n" for item in rows))
        raw = self.path.read_bytes()
        result = usage.read_usage(self.path, provider, **bounds)
        self.assertEqual(self.path.read_bytes(), raw)
        self.assertEqual(result["source_sha256"], hashlib.sha256(raw).hexdigest())
        return result

    def test_final_cumulative_not_sum_and_cache_is_subset(self):
        result = self.read([meta(), context(), count(), count(20, "r2", inputs=200, output=40), done(20, duration=19000)])
        self.assertEqual(result["tokens"], counters(inputs=200, output=40))
        self.assertEqual(result["active_seconds"], 19)
        self.assertEqual(result["elapsed_seconds"], 20)
        self.assertTrue(result["complete"])
        self.assertEqual(result["identities"], ["r1", "r2"])

    def test_inherited_context_removed_at_native_boundary(self):
        result = self.read([meta(), meta("ancestor"), context(model="ancestor-model"),
                            count(inputs=9000), row("event_msg", 2, type="thread_settings_applied", thread_id="own"),
                            context(3), count(10, "own-response"), done()])
        self.assertEqual(result["tokens"], counters())
        self.assertEqual(result["model"], "model-a")
        self.assertEqual(result["identities"], ["own-response"])

    def test_inherited_context_without_boundary_rejected(self):
        with self.assertRaisesRegex(ValueError, "own-thread boundary"):
            self.read([meta(), meta("ancestor"), count()])

    def test_duplicate_response_is_counted_once(self):
        result = self.read([meta(), count(), count()])
        self.assertEqual(result["identities"], ["r1"])
        self.assertEqual(result["tokens"], counters())

    def test_replayed_old_response_does_not_reset_cumulative(self):
        result = self.read([meta(), count(), count(20, "r2", inputs=200), count()])
        self.assertEqual(result["tokens"], counters(inputs=200))
        self.assertEqual(result["identities"], ["r1", "r2"])

    def test_conflicting_response_and_wrong_thread_rejected(self):
        with self.assertRaisesRegex(ValueError, "Ambiguous response"):
            self.read([meta(), count(), count(inputs=101)])
        wrong = count()
        wrong["payload"]["thread_id"] = "other"
        with self.assertRaisesRegex(ValueError, "another thread"):
            self.read([meta(), wrong])

    def test_window_subtracts_observed_cumulative_without_proration(self):
        result = self.read([meta(), context(), count(), count(20, "r2", inputs=250, output=40),
                            count(30, "r3", inputs=400, output=60), done(30, duration=29000)],
                           since=stamp(15), until=stamp(25))
        self.assertEqual(result["tokens"], counters(inputs=150, cached=0, output=20))
        self.assertEqual(result["identities"], ["r2"])
        self.assertEqual(result["active_seconds"], 10)
        self.assertFalse(result["complete"])

    def test_window_requires_observed_baseline_even_at_session_start(self):
        result = self.read([meta(), count()], since=stamp(0), until=stamp(10))
        self.assertIsNone(result["tokens"])
        self.assertIn("missing_window_baseline", result["warnings"])

    def test_missing_usage_and_missing_cache_are_not_zero(self):
        result = self.read([meta(), context(), done()])
        self.assertIsNone(result["tokens"])
        sample = count()
        del sample["payload"]["thread_token_usage"]["cache_write_input_tokens"]
        self.assertIsNone(self.read([meta(), sample])["tokens"])

    def test_partial_counters_still_reject_regression(self):
        first, second = count(), count(20, "r2", inputs=80)
        del first["payload"]["thread_token_usage"]["cache_write_input_tokens"]
        del second["payload"]["thread_token_usage"]["cache_write_input_tokens"]
        with self.assertRaisesRegex(ValueError, "Regressive"):
            self.read([meta(), first, second])

    def test_naive_timestamps_negative_and_regressive_counters_rejected(self):
        with self.assertRaisesRegex(ValueError, "Naive"):
            self.read([meta()], since="2026-09-09T00:00:00")
        sample = count()
        sample["timestamp"] = "2026-09-09T00:00:10"
        with self.assertRaisesRegex(ValueError, "Naive"):
            self.read([meta(), sample])
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            self.read([meta(), count(cached=-1)])
        with self.assertRaisesRegex(ValueError, "Regressive"):
            self.read([meta(), count(), count(20, "r2", inputs=80)])

    def test_active_session_and_union_of_finished_turns(self):
        result = self.read([meta(), context(), done(), context(5, "t2"),
                            done(15, "t2", 10000), context(20, "t3")])
        self.assertFalse(result["complete"])
        self.assertEqual(result["active_seconds"], 14)
        self.assertEqual(result["elapsed_seconds"], 20)
        self.assertIsNone(self.read([meta(), context()])["active_seconds"])

    def test_native_unix_interval_preserves_millisecond_duration(self):
        completion = done()
        completion["payload"].update(started_at=1788912001, completed_at=1788912010, duration_ms=9002)
        result = self.read([meta(), context(), completion])
        self.assertEqual(result["active_seconds"], 9.002)

    def test_mixed_model_is_unknown(self):
        result = self.read([meta(), context(), done(), context(11, "t2", "model-b"), done(20, "t2")])
        self.assertIsNone(result["model"])
        self.assertIn("mixed_models", result["warnings"])

    def test_claude_streaming_dedup_adds_cache_to_input_once(self):
        result = self.read([claude(output=5), claude(11), claude(11), claude_done()], "claude")
        self.assertEqual(result["tokens"], counters(inputs=45, cached=30, writes=5, output=20))
        self.assertEqual(result["identities"], ["m1"])
        self.assertTrue(result["complete"])
        self.assertEqual(result["active_seconds"], 11)
        self.assertEqual(result["elapsed_seconds"], 11)
        self.assertNotIn("PRIVATE", json.dumps(result))

    def test_claude_unique_messages_are_summed(self):
        result = self.read([claude(), claude(20, "m2", output=30)], "claude")
        self.assertEqual(result["tokens"], counters(inputs=90, cached=60, writes=10, output=50))
        self.assertFalse(result["complete"])

    def test_claude_window_is_difference_in_cumulative_observations(self):
        result = self.read([claude(), claude(20, "m2", output=30)], "claude", since=stamp(10), until=stamp(20))
        self.assertEqual(result["tokens"], counters(inputs=45, cached=30, writes=5, output=30))
        self.assertEqual(result["identities"], ["m2"])

    def test_claude_missing_cache_and_unknown_format_unmeasured(self):
        message = claude()
        del message["message"]["usage"]["cache_creation_input_tokens"]
        self.assertIsNone(self.read([message], "claude")["tokens"])
        result = self.read([{"something": "private"}], "claude")
        self.assertIsNone(result["tokens"])
        self.assertIn("unrecognized_claude_format", result["warnings"])

    def test_claude_ambiguous_sessions_and_message_identity_rejected(self):
        with self.assertRaisesRegex(ValueError, "Ambiguous Claude session"):
            self.read([claude(), claude(20, "m2", sessionId="other")], "claude")
        second = claude(11)
        second["message"]["model"] = "different"
        with self.assertRaisesRegex(ValueError, "Ambiguous message"):
            self.read([claude(), second], "claude")
        with self.assertRaisesRegex(ValueError, "Regressive"):
            self.read([claude(), claude(11, output=5)], "claude")

    def test_native_cost_only_no_model_rate_inferred(self):
        result = self.read([claude()], "claude")
        self.assertIsNone(result["provider_cost"])
        cost = {"type": "result", "timestamp": stamp(12), "session_id": "claude-session", "total_cost_usd": 0.25}
        result = self.read([claude(), cost], "claude")
        self.assertEqual(result["provider_cost"], {"amount": 0.25, "currency": "USD", "basis": "native_result_total_cost_usd"})
        self.assertIsNone(self.read([claude(), cost], "claude", since=stamp(0))["provider_cost"])

    def test_native_cost_window_uses_difference(self):
        first = {"type": "result", "timestamp": stamp(12), "session_id": "claude-session", "total_cost_usd": 0.25}
        second = {**first, "timestamp": stamp(20), "total_cost_usd": 0.75}
        result = self.read([claude(), first, second], "claude", since=stamp(12), until=stamp(20))
        self.assertEqual(result["provider_cost"]["amount"], 0.5)

    def test_missing_usage_timestamp_cannot_be_windowed(self):
        sample = count()
        del sample["timestamp"]
        result = self.read([meta(), sample], since=stamp(0), until=stamp(20))
        self.assertIsNone(result["tokens"])
        self.assertIn("usage_timestamps_missing", result["warnings"])

    def test_cli_metadata_only_and_sanitized_parse_error(self):
        self.read([claude()], "claude")
        process = subprocess.run([sys.executable, str(SCRIPT), "read", "--provider", "claude", "--source", str(self.path)],
                                 capture_output=True, text=True, check=True)
        self.assertNotIn("PRIVATE", process.stdout + process.stderr)
        self.assertEqual(json.loads(process.stdout)["thread_id"], "claude-session")
        self.path.write_text("PRIVATE INVALID JSON")
        process = subprocess.run([sys.executable, str(SCRIPT), "read", "--provider", "claude", "--source", str(self.path)],
                                 capture_output=True, text=True)
        self.assertEqual(process.returncode, 2)
        self.assertNotIn("PRIVATE", process.stdout + process.stderr)


if __name__ == "__main__":
    unittest.main()
