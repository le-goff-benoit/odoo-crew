import math
import numbers


_PROVIDERS = ("openai", "anthropic")
_WINDOWS = ("5h", "week")


def _is_finite_number(value):
    """Whether *value* is a non-boolean, finite real number."""
    return isinstance(value, numbers.Real) and not isinstance(value, bool) and math.isfinite(value)


def _valid_event(event, now):
    """Return whether an event can describe a quota observation."""
    if not isinstance(event, dict):
        return False
    if event.get("provider") not in _PROVIDERS or event.get("window") not in _WINDOWS:
        return False

    observed_at = event.get("observed_at")
    used_percent = event.get("used_percent")
    reset_at = event.get("reset_at")
    if not _is_finite_number(observed_at) or observed_at < 0 or observed_at > now:
        return False
    if not _is_finite_number(used_percent) or not 0 <= used_percent <= 100:
        return False
    if reset_at is not None:
        if not _is_finite_number(reset_at) or reset_at < 0 or reset_at < observed_at:
            return False
    return True


def snapshot(events, now, ttl=300):
    """Return provider/window observations, never inferred consumption."""
    result = {provider: {window: None for window in _WINDOWS}
              for provider in _PROVIDERS}

    for event in events:
        if not _valid_event(event, now):
            continue
        provider = event["provider"]
        window = event["window"]
        current = result[provider][window]
        # >= deliberately lets the later list entry win when observations tie.
        if current is None or event["observed_at"] >= current["observed_at"]:
            result[provider][window] = {
                "used_percent": event["used_percent"],
                "reset_at": event["reset_at"],
                "observed_at": event["observed_at"],
                "stale": now - event["observed_at"] > ttl,
            }

    return result
