import math

_PROVIDERS = ('openai', 'anthropic')
_WINDOWS = ('5h', 'week')


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_finite_number(value):
    return _is_number(value) and math.isfinite(value)


def _is_valid_event(event, now):
    if not isinstance(event, dict):
        return False
    if event.get('provider') not in _PROVIDERS:
        return False
    if event.get('window') not in _WINDOWS:
        return False

    observed_at = event.get('observed_at')
    if not _is_finite_number(observed_at):
        return False
    if observed_at < 0 or observed_at > now:
        return False

    used_percent = event.get('used_percent')
    if not _is_finite_number(used_percent):
        return False
    if used_percent < 0 or used_percent > 100:
        return False

    reset_at = event.get('reset_at')
    if reset_at is not None:
        if not _is_finite_number(reset_at):
            return False
        if reset_at < 0 or reset_at < observed_at:
            return False

    return True


def snapshot(events, now, ttl=300):
    """Return provider/window observations, never inferred consumption."""
    best = {provider: {window: None for window in _WINDOWS} for provider in _PROVIDERS}

    for event in events:
        if not _is_valid_event(event, now):
            continue
        provider = event['provider']
        window = event['window']
        observed_at = event['observed_at']
        current = best[provider][window]
        if current is None or observed_at >= current['observed_at']:
            best[provider][window] = {
                'observed_at': observed_at,
                'used_percent': event['used_percent'],
                'reset_at': event.get('reset_at'),
            }

    result = {provider: {window: None for window in _WINDOWS} for provider in _PROVIDERS}
    for provider in _PROVIDERS:
        for window in _WINDOWS:
            picked = best[provider][window]
            if picked is None:
                continue
            result[provider][window] = {
                'used_percent': picked['used_percent'],
                'reset_at': picked['reset_at'],
                'observed_at': picked['observed_at'],
                'stale': (now - picked['observed_at']) > ttl,
            }

    return result
