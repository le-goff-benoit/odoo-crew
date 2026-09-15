"""Fenêtres de quota : lecture d'observations, jamais d'inférence de consommation."""
import math
import numbers

PROVIDERS = ('openai', 'anthropic')
WINDOWS = ('5h', 'week')


def _number(value):
    """Un nombre réel fini : les booléens ne comptent jamais comme une mesure."""
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        return None
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if math.isnan(value) or math.isinf(value):
        return None
    return value


def _observation(event, now):
    """Retourne (observed_at, used_percent, reset_at) si l'événement est exploitable."""
    if not isinstance(event, dict):
        return None
    if event.get('provider') not in PROVIDERS or event.get('window') not in WINDOWS:
        return None

    observed_at = _number(event.get('observed_at'))
    if observed_at is None or observed_at < 0 or observed_at > now:
        return None

    used_percent = _number(event.get('used_percent'))
    if used_percent is None or not 0 <= used_percent <= 100:
        return None

    reset_at = event.get('reset_at')
    if reset_at is not None:
        reset_value = _number(reset_at)
        if reset_value is None or reset_value < 0 or reset_value < observed_at:
            return None

    return observed_at, event.get('used_percent'), reset_at


def snapshot(events, now, ttl=300):
    """Return provider/window observations, never inferred consumption."""
    best = {provider: {window: None for window in WINDOWS} for provider in PROVIDERS}

    for event in events or ():
        parsed = _observation(event, now)
        if parsed is None:
            continue
        observed_at, used_percent, reset_at = parsed
        slot = best[event['provider']][event['window']]
        # À égalité d'horodatage, le dernier événement de la liste gagne.
        if slot is not None and observed_at < slot['observed_at']:
            continue
        best[event['provider']][event['window']] = {
            'used_percent': used_percent,
            'reset_at': reset_at,
            'observed_at': event.get('observed_at'),
            'stale': (now - observed_at) > ttl,
        }

    return best
