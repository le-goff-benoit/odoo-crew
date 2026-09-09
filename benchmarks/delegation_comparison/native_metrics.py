#!/usr/bin/env python3
"""Native task-tree metrics; allowlisted exports never include reasoning messages."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path


def instant(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp()


def agent_path(record):
    source = record.get('payload', {}).get('source', {})
    return (source.get('subagent', {}).get('thread_spawn', {}).get('agent_path')
            if isinstance(source, dict) else None)


def allowed(record):
    kind, p = record.get('type'), record.get('payload', {})
    keys = None
    if kind == 'session_meta':
        keys = {'id', 'timestamp', 'source', 'agent_nickname', 'agent_role', 'model_provider'}
    elif kind == 'turn_context':
        keys = {'turn_id', 'model', 'effort', 'reasoning_effort'}
    elif kind == 'token_usage_record':
        pass
    elif kind == 'event_msg' and p.get('type') == 'task_complete':
        keys = {'type', 'turn_id', 'started_at', 'completed_at', 'duration_ms', 'time_to_first_token_ms'}
    elif kind == 'response_item':
        tool = p.get('type') in {'function_call', 'function_call_output', 'custom_tool_call', 'custom_tool_call_output'}
        final = (p.get('type') == 'message' and p.get('role') == 'assistant'
                 and (p.get('channel') == 'final' or p.get('phase') == 'final_answer'))
        if not (tool or final):
            return None
    else:
        return None
    result = {key: value for key, value in record.items() if key != 'payload'}
    result['payload'] = ({key: value for key, value in p.items() if key in keys}
                         if keys is not None else p)
    return result


def own_records(records):
    """Remove a native fork's imported prefix, using its own settings boundary.

    The first session_meta belongs to this thread. A fork may then serialize
    ancestor metadata and an unfinished ancestor context before applying its
    own thread settings. Those records are context, not this child's work.
    """
    meta = next(r for r in records if r['type'] == 'session_meta')
    identity = meta['payload']['id']
    if not any(r['type'] == 'session_meta' and r['payload']['id'] != identity
               for r in records):
        return records
    boundary = next((i for i, r in enumerate(records)
                     if r['type'] == 'event_msg'
                     and r['payload'].get('type') == 'thread_settings_applied'
                     and r['payload'].get('thread_id') == identity), None)
    if boundary is None:
        raise ValueError('Inherited native context without an own-thread boundary')
    return [meta, *records[boundary:]]


def overlap(intervals):
    points = sorted([(a, 1) for a, b in intervals] + [(b, -1) for a, b in intervals])
    active, previous, seconds = 0, None, 0.0
    for time, delta in points:
        if previous is not None and active > 1:
            seconds += time - previous
        active += delta
        previous = time
    return round(seconds, 6)


def summarize(records):
    meta = next(r['payload'] for r in records if r['type'] == 'session_meta')
    contexts = [r['payload'] for r in records if r['type'] == 'turn_context']
    usages = [r['payload'] for r in records if r['type'] == 'token_usage_record']
    ends = [r for r in records if r['type'] == 'event_msg' and r['payload'].get('type') == 'task_complete']
    turns = []
    for row in ends:
        end = instant(row['timestamp'])
        duration = row['payload'].get('duration_ms', 0) / 1000
        turns.append({'turn_id': row['payload'].get('turn_id'), 'start': end-duration, 'end': end, 'seconds': duration})
    turn_ids = {r.get('turn_id') for r in contexts if r.get('turn_id')}
    completed_ids = {r['turn_id'] for r in turns}
    calls = [r['payload'] for r in records if r['type'] == 'response_item'
             and r['payload'].get('type') in {'function_call', 'custom_tool_call'}]
    return {'thread_id': meta['id'], 'agent': agent_path({'payload': meta}),
            'start': instant(meta['timestamp']), 'end': max((r['end'] for r in turns), default=None),
            'complete': bool(turns) and turn_ids <= completed_ids,
            'turns': turns, 'model_effort': sorted({(r.get('model'), r.get('effort', r.get('reasoning_effort'))) for r in contexts}),
            'tokens': usages[-1].get('thread_token_usage') if usages else None,
            'usage_response_ids': [r['response_id'] for r in usages if r.get('response_id')],
            'tool_calls': len(calls), 'child_spawns': sum(r.get('name') == 'spawn_agent' for r in calls)}


def aggregate(rows, parent):
    selected = [r for r in rows if r['agent'] == parent or r['agent'].startswith(parent + '/')]
    principal = next(r for r in selected if r['agent'] == parent)
    measured = all(isinstance(r['tokens'], dict) and 'total_tokens' in r['tokens'] for r in selected)
    ids = [i for r in selected for i in r['usage_response_ids']]
    duplicates = len(ids) != len(set(ids))
    complete = all(r['complete'] for r in selected)
    return {'parent': parent, 'threads': selected, 'descendants': len(selected)-1,
            'complete': complete, 'tokens_measured': measured and not duplicates,
            'duplicate_response_ids': duplicates,
            'tokens': {k: sum(r['tokens'].get(k, 0) for r in selected) for k in set().union(*(r['tokens'] for r in selected))} if measured and not duplicates else None,
            'wall_seconds': round(max(r['end'] for r in selected)-principal['start'], 6) if complete else None,
            'child_overlap_seconds': overlap([(t['start'], t['end']) for r in selected if r['agent'] != parent for t in r['turns']]),
            'observed_model_effort': sorted(set(tuple(x) for r in selected for x in r['model_effort'])),
            'scope': 'One final cumulative counter per thread, descendants included. Cached and reasoning are subsets, not added to total. Overlap is native turn availability, not continuous compute activity. Preparation, coordinator and common judge excluded. Tool content is not a generic secret sanitizer.'}


def collect(sessions, parent, output):
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for source in sessions.rglob('*.jsonl'):
        with source.open() as stream:
            try:
                first = json.loads(stream.readline())
            except ValueError:
                continue
        name = agent_path(first)
        if not name or not (name == parent or name.startswith(parent + '/')):
            continue
        raw = source.read_bytes()
        # Parse only to apply an allowlist. Excluded message/reasoning content is
        # neither emitted, summarized nor written to any output artifact.
        owned = own_records([json.loads(line) for line in raw.splitlines()])
        records = [x for row in owned if (x := allowed(row)) is not None]
        target = output / (name.strip('/').replace('/', '--') + '.jsonl')
        target.write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in records))
        row = summarize(records)
        row['export'] = target.name
        row['export_sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
        row['source_snapshot_sha256'] = hashlib.sha256(raw).hexdigest()
        rows.append(row)
    report = aggregate(rows, parent)
    (output/'metrics.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sessions', type=Path, required=True)
    parser.add_argument('--agent', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = collect(args.sessions, args.agent, args.output)
    print(json.dumps({k: v for k, v in result.items() if k != 'threads'}, ensure_ascii=False, indent=2))
