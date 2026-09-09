#!/usr/bin/env python3
"""Read an explicitly selected native session without exporting conversation content.

Token windows use observations at or before their bounds, never interpolation.
Active time is the union of completed native turn intervals, not CPU time.
Missing counters are unknown, including cache counters; they are never zero-filled.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path


TOKEN_KEYS = (
    "input_tokens", "cached_input_tokens", "cache_write_input_tokens",
    "output_tokens", "total_tokens",
)


def _instant(value):
    if not isinstance(value, str):
        raise ValueError("A timestamp must be an ISO string with a timezone")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("Invalid ISO timestamp") from None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Naive timestamps are not accepted")
    return parsed.timestamp()


def _iso(value):
    return datetime.fromtimestamp(value, timezone.utc).isoformat() if value is not None else None


def _number(value, label, integer=False):
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or value < 0
            or (integer and not isinstance(value, int))):
        raise ValueError(f"Invalid nonnegative {label}")
    return value


def _identity(value, label):
    if not isinstance(value, str) or not value:
        raise ValueError(f"Missing or ambiguous {label}")
    return value


def _tokens(raw, provider):
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError("Invalid usage counters")
    if provider == "codex":
        keys = TOKEN_KEYS
    else:
        keys = ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens")
    for key in keys:
        if key in raw and raw[key] is not None:
            _number(raw[key], "token counter", integer=True)
    if any(raw.get(key) is None for key in keys):
        return None
    if provider == "claude":
        inputs = raw["input_tokens"] + raw["cache_read_input_tokens"] + raw["cache_creation_input_tokens"]
        return dict(zip(TOKEN_KEYS, (inputs, raw["cache_read_input_tokens"],
                                   raw["cache_creation_input_tokens"], raw["output_tokens"],
                                   inputs + raw["output_tokens"])))
    result = {key: raw[key] for key in TOKEN_KEYS}
    if (result["cached_input_tokens"] + result["cache_write_input_tokens"] > result["input_tokens"]
            or result["total_tokens"] != result["input_tokens"] + result["output_tokens"]):
        raise ValueError("Inconsistent token counters")
    return result


def _monotonic(previous, current):
    if previous is not None and current is not None:
        if any(current[key] < previous[key] for key in TOKEN_KEYS):
            raise ValueError("Regressive token counters")


def _raw_monotonic(previous, current):
    """Check observed fields even when other fields make normalization unknown."""
    if isinstance(previous, dict) and isinstance(current, dict):
        keys = set(TOKEN_KEYS) | {"cache_read_input_tokens", "cache_creation_input_tokens"}
        if any(current[key] < previous[key] for key in keys
               if current.get(key) is not None and previous.get(key) is not None):
            raise ValueError("Regressive token counters")


def _own_codex(records):
    metadata = [row for row in records if row.get("type") == "session_meta"]
    if not metadata:
        return records, None, None
    meta = metadata[0]
    identity = _identity(meta.get("payload", {}).get("id"), "thread identity")
    if any(row.get("payload", {}).get("id") != identity for row in metadata):
        boundary = next((index for index, row in enumerate(records)
                         if row.get("type") == "event_msg"
                         and row.get("payload", {}).get("type") == "thread_settings_applied"
                         and row["payload"].get("thread_id") == identity), None)
        if boundary is None:
            raise ValueError("Inherited native context without an own-thread boundary")
        records = [meta, *records[boundary:]]
        if any(row.get("payload", {}).get("id") != identity
               for row in records if row.get("type") == "session_meta"):
            raise ValueError("Ambiguous own-thread metadata")
    start = meta.get("payload", {}).get("timestamp", meta.get("timestamp"))
    return records, identity, _instant(start) if start is not None else None


def _interval(payload, timestamp, duration_key):
    def native_time(value):
        # Codex task_complete stores UNIX seconds, rounded to whole seconds.
        return _number(value, "UNIX timestamp") if isinstance(value, (int, float)) else _instant(value)

    raw_end, raw_start = payload.get("completed_at"), payload.get("started_at")
    end = native_time(raw_end) if raw_end is not None else timestamp
    start = native_time(raw_start) if raw_start is not None else None
    duration = payload.get(duration_key)
    if duration is not None:
        duration = _number(duration, "duration") / 1000
        if start is None and end is not None:
            start = end - duration
    if start is None or end is None:
        return None
    if end < start:
        raise ValueError("Regressive turn interval")
    rounded = isinstance(raw_end, int) or isinstance(raw_start, int)
    if duration is not None and abs(end - start - duration) > (2 if rounded else 0.01):
        raise ValueError("Inconsistent turn duration")
    if rounded and duration is not None:
        end = timestamp if timestamp is not None else end
        start = end - duration
    return start, end


def _union(intervals, lower, upper):
    clipped = sorted((max(a, lower) if lower is not None else a,
                      min(b, upper) if upper is not None else b) for a, b in intervals)
    total, finish = 0.0, None
    for start, end in clipped:
        if end < start:
            continue
        total += max(0, end - max(start, finish if finish is not None else start))
        finish = max(end, finish if finish is not None else end)
    return round(total, 6)


def _difference(current, baseline):
    if current is None or baseline is None:
        return None
    _monotonic(baseline, current)
    return {key: current[key] - baseline[key] for key in TOKEN_KEYS}


def _at(samples, bound):
    eligible = samples if bound is None else [sample for sample in samples if sample[0] is not None and sample[0] <= bound]
    return eligible[-1] if eligible else None


def _codex(records, identity, lower, upper, warnings):
    samples, identities, models, intervals = [], [], set(), []
    starts, ends, responses = {}, {}, {}
    previous, previous_raw, last_sample_time = None, None, None
    unknown_usage = False
    for row in records:
        kind, payload = row.get("type"), row.get("payload", {})
        timestamp = _instant(row["timestamp"]) if row.get("timestamp") is not None else None
        if kind == "turn_context" or (kind == "event_msg" and payload.get("type") == "task_started"):
            turn = _identity(payload.get("turn_id"), "turn identity")
            starts.setdefault(turn, timestamp)
            if kind == "turn_context" and payload.get("model"):
                models.add(_identity(payload["model"], "model identity"))
        if kind == "event_msg" and payload.get("type") == "task_complete":
            turn = _identity(payload.get("turn_id"), "completed turn identity")
            interval = _interval(payload, timestamp, "duration_ms")
            if turn in ends and ends[turn] != interval:
                raise ValueError("Ambiguous completed turn identity")
            ends[turn] = interval
            if interval is not None:
                intervals.append(interval)
            else:
                warnings.append("some_completed_turn_durations_missing")
        if kind != "token_usage_record":
            continue
        if identity is None:
            raise ValueError("Usage without native thread identity")
        if payload.get("thread_id", identity) != identity:
            raise ValueError("Usage belongs to another thread")
        response = _identity(payload.get("response_id"), "response identity")
        tokens = _tokens(payload.get("thread_token_usage"), "codex")
        if response in responses:
            if responses[response] != payload.get("thread_token_usage"):
                raise ValueError("Ambiguous response identity with conflicting counters")
            continue
        responses[response] = payload.get("thread_token_usage")
        _raw_monotonic(previous_raw, payload.get("thread_token_usage"))
        if isinstance(payload.get("thread_token_usage"), dict):
            previous_raw = {**(previous_raw or {}), **{
                key: value for key, value in payload["thread_token_usage"].items() if value is not None}}
        if timestamp is not None and last_sample_time is not None and timestamp < last_sample_time:
            raise ValueError("Regressive usage timestamps")
        if timestamp is not None:
            last_sample_time = timestamp
        _monotonic(previous, tokens)
        if tokens is not None:
            previous = tokens
        else:
            unknown_usage = True
        samples.append((timestamp, tokens, response))
    final = _at(samples, upper)
    baseline = _at(samples, lower) if lower is not None else None
    tokens = final[1] if final else None
    if lower is not None:
        tokens = _difference(tokens, baseline[1]) if baseline else None
        if baseline is None:
            warnings.append("missing_window_baseline")
    if any(sample[0] is None for sample in samples) and (lower is not None or upper is not None):
        tokens = None
        warnings.append("usage_timestamps_missing")
    if unknown_usage:
        warnings.append("some_usage_counters_missing")
    for timestamp, _, response in samples:
        if ((lower is None or timestamp is not None and timestamp > lower)
                and (upper is None or timestamp is not None and timestamp <= upper)):
            identities.append(response)
    relevant = {turn for turn, timestamp in starts.items()
                if upper is None or timestamp is None or timestamp <= upper}
    finished = {turn for turn, interval in ends.items()
                if upper is None or interval is not None and interval[1] <= upper}
    complete = bool(finished) and relevant <= finished
    if not complete:
        warnings.append("session_or_window_incomplete")
    return tokens, identities, models, intervals, complete, None


def _claude(records, lower, upper, warnings):
    sessions, messages, models, intervals, costs = set(), {}, set(), [], []
    raw_usage = {}
    recognized, latest_work, latest_end = False, None, None
    missing_message_usage = False
    for row in records:
        for key in ("sessionId", "session_id"):
            if row.get(key) is not None:
                sessions.add(_identity(row[key], "session identity"))
        timestamp = _instant(row["timestamp"]) if row.get("timestamp") is not None else None
        kind = row.get("type")
        if kind in {"assistant", "user"} and (upper is None or timestamp is None or timestamp <= upper):
            if timestamp is not None:
                latest_work = max(timestamp, latest_work if latest_work is not None else timestamp)
        if kind == "system" and row.get("subtype") == "turn_duration":
            recognized = True
            interval = _interval(row, timestamp, "durationMs")
            if interval is not None:
                intervals.append(interval)
                if upper is None or interval[1] <= upper:
                    latest_end = max(interval[1], latest_end if latest_end is not None else interval[1])
            else:
                warnings.append("some_completed_turn_durations_missing")
        if kind == "result" and "total_cost_usd" in row:
            recognized = True
            amount = _number(row["total_cost_usd"], "provider cost")
            if costs and amount < costs[-1][1]:
                raise ValueError("Regressive provider cost")
            if costs and timestamp is not None and costs[-1][0] is not None and timestamp < costs[-1][0]:
                raise ValueError("Regressive provider cost timestamps")
            costs.append((timestamp, amount))
            if timestamp is not None and (upper is None or timestamp <= upper):
                latest_end = max(timestamp, latest_end if latest_end is not None else timestamp)
        if kind != "assistant":
            continue
        message = row.get("message")
        if not isinstance(message, dict) or message.get("type") != "message":
            missing_message_usage = True
            continue
        recognized = True
        identity = _identity(message.get("id"), "message identity")
        model = message.get("model")
        if model is not None:
            models.add(_identity(model, "model identity"))
        tokens = _tokens(message.get("usage"), "claude")
        _raw_monotonic(raw_usage.get(identity), message.get("usage"))
        if isinstance(message.get("usage"), dict):
            raw_usage[identity] = {**raw_usage.get(identity, {}), **{
                key: value for key, value in message["usage"].items() if value is not None}}
        request = row.get("requestId")
        snapshots = messages.setdefault(identity, [])
        if snapshots:
            old_time, old_tokens, old_model, old_request = snapshots[-1]
            if old_model != model or old_request != request:
                raise ValueError("Ambiguous message identity")
            if old_time is not None and timestamp is not None and timestamp < old_time:
                raise ValueError("Regressive message timestamps")
            _monotonic(old_tokens, tokens)
        snapshots.append((timestamp, tokens, model, request))
    if len(sessions) > 1:
        raise ValueError("Ambiguous Claude session identity")
    identity = next(iter(sessions), None)
    if messages and identity is None:
        raise ValueError("Usage without native session identity")

    def cumulative(bound):
        measured = []
        for snapshots in messages.values():
            sample = _at(snapshots, bound)
            if sample is not None:
                if sample[1] is None:
                    return None
                measured.append(sample[1])
        if not measured or missing_message_usage:
            return None
        return {key: sum(sample[key] for sample in measured) for key in TOKEN_KEYS}

    tokens = cumulative(upper)
    if lower is not None:
        baseline = cumulative(lower)
        tokens = _difference(tokens, baseline)
        if baseline is None:
            warnings.append("missing_window_baseline")
    if (lower is not None or upper is not None) and any(
            sample[0] is None for snapshots in messages.values() for sample in snapshots):
        tokens = None
        warnings.append("usage_timestamps_missing")
    identities = [key for key, snapshots in messages.items() if any(
        (lower is None or sample[0] is not None and sample[0] > lower)
        and (upper is None or sample[0] is not None and sample[0] <= upper) for sample in snapshots)]
    cost = None
    final_cost = _at(costs, upper)
    baseline_cost = _at(costs, lower) if lower is not None else None
    if final_cost is not None and (lower is None or baseline_cost is not None):
        if not ((lower is not None or upper is not None) and any(sample[0] is None for sample in costs)):
            cost = {"amount": final_cost[1] - (baseline_cost[1] if baseline_cost else 0),
                    "currency": "USD", "basis": "native_result_total_cost_usd"}
    complete = latest_end is not None and latest_work is not None and latest_end >= latest_work
    if not recognized:
        warnings.append("unrecognized_claude_format")
    if not complete:
        warnings.append("session_or_window_incomplete")
    return identity, tokens, identities, models, intervals, complete, cost


def read_usage(path, provider, since=None, until=None):
    """Return metadata only; the source file is opened read-only and never modified.

    Raises ValueError for invalid timestamps/counters or ambiguous identities.
    Unknown formats and absent measurements return null with explicit warnings.
    Bounds are inclusive for cumulative snapshots; their difference covers
    (since, until]. No pre-first-observation zero baseline is assumed.
    """
    if provider not in {"codex", "claude"}:
        raise ValueError("Unsupported provider")
    lower = _instant(since) if since is not None else None
    upper = _instant(until) if until is not None else None
    if lower is not None and upper is not None and upper < lower:
        raise ValueError("Window ends before it starts")
    raw = Path(path).read_bytes()
    records = []
    for index, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except (ValueError, UnicodeDecodeError):
            raise ValueError(f"Invalid JSON on source line {index}") from None
        if not isinstance(row, dict):
            raise ValueError(f"Expected an object on source line {index}")
        if "payload" in row and not isinstance(row["payload"], dict):
            raise ValueError(f"Invalid metadata on source line {index}")
        records.append(row)
    warnings, start, identity = [], None, None
    if provider == "codex":
        records, identity, start = _own_codex(records)
        tokens, identities, models, intervals, complete, cost = _codex(records, identity, lower, upper, warnings)
    else:
        identity, tokens, identities, models, intervals, complete, cost = _claude(records, lower, upper, warnings)
    timestamps = [_instant(row["timestamp"]) for row in records if row.get("timestamp") is not None]
    if start is None and timestamps:
        start = min(timestamps)
    end = max(timestamps) if timestamps else None
    if intervals:
        start = min(start, min(a for a, _ in intervals)) if start is not None else min(a for a, _ in intervals)
        end = max(end, max(b for _, b in intervals)) if end is not None else max(b for _, b in intervals)
    if start is not None and lower is not None:
        start = max(start, lower)
    if end is not None and upper is not None:
        end = min(end, upper)
    if start is not None and end is not None and end < start:
        start = end = None
        warnings.append("window_outside_observed_session")
    active = _union(intervals, lower, upper) if intervals else None
    if "some_completed_turn_durations_missing" in warnings:
        active = None
    if active is None:
        warnings.append("completed_turn_durations_unavailable")
    if tokens is None:
        warnings.append("tokens_unmeasured")
    if len(models) > 1:
        warnings.append("mixed_models")
    if not models:
        warnings.append("model_unavailable")
    return {
        "provider": provider, "thread_id": identity,
        "model": next(iter(models)) if len(models) == 1 else None,
        "started_at": _iso(start), "ended_at": _iso(end),
        "elapsed_seconds": round(end - start, 6) if start is not None and end is not None else None,
        "active_seconds": active, "complete": complete, "tokens": tokens,
        "provider_cost": cost, "source_sha256": hashlib.sha256(raw).hexdigest(),
        "warnings": sorted(set(warnings)), "identities": sorted(identities),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    read = commands.add_parser("read", help="Read one explicitly selected native JSONL session")
    read.add_argument("--provider", choices=("codex", "claude"), required=True)
    read.add_argument("--source", type=Path, required=True)
    read.add_argument("--since")
    read.add_argument("--until")
    args = parser.parse_args()
    try:
        result = read_usage(args.source, args.provider, args.since, args.until)
    except (OSError, ValueError) as error:
        parser.exit(2, f"Cannot read native usage: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
