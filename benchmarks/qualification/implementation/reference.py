"""Calibration only: never mounted in candidate sandboxes."""
import math


def ready(tasks, locks):
    records = {t['id']: t for t in tasks}
    if len(records) != len(tasks) or any(t['status'] not in ('pending', 'running', 'received') for t in tasks):
        raise ValueError('invalid tasks')
    if any(mode not in ('read', 'write') for mode in locks.values()):
        raise ValueError('invalid lock')
    visiting, complete = set(), set()
    def visit(key):
        if key not in records or key in visiting:
            raise ValueError('missing dependency or cycle')
        if key in complete:
            return
        visiting.add(key)
        for dep in records[key]['deps']:
            visit(dep)
        visiting.remove(key)
        complete.add(key)
    for key in records:
        visit(key)
    def received(key):
        task = records[key]
        return task['status'] == 'received' and task['proof_current'] and all(received(dep) for dep in task['deps'])
    return sorted(t['id'] for t in tasks if t['status'] == 'pending' and all(received(dep) for dep in t['deps'])
                  and not any(r in locks for r in t['writes']) and not any(locks.get(r) == 'write' for r in t['reads']))


def snapshot(events, now, ttl=300):
    result = {p: {'5h': None, 'week': None} for p in ('openai', 'anthropic')}
    def number(value):
        return type(value) in (float, int) and math.isfinite(value) and value >= 0
    for event in events:
        p, w = event.get('provider'), event.get('window')
        at, used, reset = event.get('observed_at'), event.get('used_percent'), event.get('reset_at')
        if p not in result or w not in result[p] or not number(at) or at > now or not number(used) or used > 100:
            continue
        if reset is not None and (not number(reset) or reset < at):
            continue
        previous = result[p][w]
        if previous is None or previous['observed_at'] <= at:
            result[p][w] = dict(used_percent=used, reset_at=reset, observed_at=at, stale=now-at > ttl)
    return result
