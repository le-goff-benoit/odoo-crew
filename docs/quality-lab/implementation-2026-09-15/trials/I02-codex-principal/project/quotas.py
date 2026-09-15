from numbers import Real


def _finite_number(value):
    """Accept finite real numbers, excluding booleans."""
    return (
        isinstance(value, Real)
        and not isinstance(value, bool)
        and -float('inf') < value < float('inf')
    )


def snapshot(events, now, ttl=300):
    """Return provider/window observations, never inferred consumption."""
    result = {
        'openai': {'5h': None, 'week': None},
        'anthropic': {'5h': None, 'week': None},
    }
    for event in events:
        provider = event.get('provider')
        window = event.get('window')
        if provider not in ('openai', 'anthropic') or window not in ('5h', 'week'):
            continue

        observed_at = event.get('observed_at')
        used_percent = event.get('used_percent')
        reset_at = event.get('reset_at')
        if not _finite_number(observed_at) or not 0 <= observed_at <= now:
            continue
        if not _finite_number(used_percent) or not 0 <= used_percent <= 100:
            continue
        if reset_at is not None and (
            not _finite_number(reset_at) or reset_at < observed_at
        ):
            continue

        previous = result[provider][window]
        if previous is None or observed_at >= previous['observed_at']:
            result[provider][window] = {
                'used_percent': used_percent,
                'reset_at': reset_at,
                'observed_at': observed_at,
                'stale': now - observed_at > ttl,
            }
    return result
