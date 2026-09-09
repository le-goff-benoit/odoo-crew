"""Résumé hors ligne des événements natifs, sans appel modèle ni verdict métier."""
import json
import sys
from pathlib import Path


def summarize(rows):
    tasks = {}
    final = None
    for row in rows:
        event = row['event']
        at = row['received_seconds']
        if (event.get('type') == 'system' and event.get('subtype') == 'task_started'
                and event.get('task_type') == 'local_agent'):
            tasks[event['task_id']] = {
                'task_id': event['task_id'], 'tool_use_id': event['tool_use_id'],
                'role': event.get('subagent_type'), 'started': at,
                'progress': [], 'tool_returned': False, 'spawn_depth': event.get('spawn_depth'),
            }
        elif event.get('type') == 'system' and event.get('subtype') == 'task_progress':
            task = tasks.get(event.get('task_id'))
            if task:
                task['progress'].append(at)
                task['last_usage'] = event.get('usage')
        elif event.get('type') == 'system' and event.get('subtype') == 'task_notification':
            task = tasks.get(event.get('task_id'))
            if task:
                task['native_status'] = event.get('status')
                task['notified_at'] = at
        elif event.get('type') == 'result':
            final = {key: event.get(key) for key in (
                'subtype', 'is_error', 'duration_ms', 'total_cost_usd', 'subagent_stats', 'modelUsage')}
        for block in event.get('message', {}).get('content', []):
            if block.get('type') != 'tool_result':
                continue
            for task in tasks.values():
                if task['tool_use_id'] == block.get('tool_use_id'):
                    task['tool_returned'] = True
                    task['tool_error'] = bool(block.get('is_error', False))
                    task['returned_at'] = at
    overlaps = []
    values = list(tasks.values())
    for index, left in enumerate(values):
        for right in values[index + 1:]:
            if len(left['progress']) < 2 or len(right['progress']) < 2:
                continue
            overlap = min(max(left['progress']), max(right['progress'])) - max(min(left['progress']), min(right['progress']))
            if overlap > 0:
                overlaps.append({'tasks': [left['task_id'], right['task_id']],
                                 'observed_work_envelope_overlap_seconds': round(overlap, 3)})
    return {'native_tasks_started': len(tasks),
            'tasks_with_observed_work': sum(bool(task['progress']) for task in values),
            'tasks': values, 'overlaps': overlaps, 'provider_result': final,
            'business_verdict': 'À relire séparément dans les preuves et l’oracle Odoo',
            'limit': 'Les enveloppes de progression prouvent le chevauchement des activités observées, pas le calcul simultané du fournisseur ni un gain causal de vitesse.'}


def self_test():
    def event(at, **fields):
        return {'received_seconds': at, 'event': fields}
    request = event(0, type='assistant', message={'content': [{'type': 'tool_use', 'name': 'Agent', 'id': 'call'}]})
    assert summarize([request])['native_tasks_started'] == 0
    rows = [request]
    for task, start in [('a', 1), ('b', 2)]:
        rows.append(event(start, type='system', subtype='task_started', task_type='local_agent', task_id=task, tool_use_id=task, subagent_type='fixture'))
    assert summarize(rows)['tasks_with_observed_work'] == 0
    for task, at in [('a', 3), ('b', 4), ('a', 8), ('b', 9)]:
        rows.append(event(at, type='system', subtype='task_progress', task_id=task))
    result = summarize(rows)
    assert result['tasks_with_observed_work'] == 2
    assert result['overlaps'][0]['observed_work_envelope_overlap_seconds'] == 4
    assert result['provider_result'] is None  # un travail observé n'est pas un parcours terminé
    serial = [row for row in rows if row['event'].get('task_id') != 'b']
    assert not summarize(serial)['overlaps']
    claim = event(1, type='claim', node='module_static_qa', owner='claimed-without-process')
    assert summarize([claim])['native_tasks_started'] == 0
    shell = event(1, type='system', subtype='task_started', task_type='local_bash', task_id='shell', tool_use_id='shell')
    assert summarize([shell])['native_tasks_started'] == 0
    print('Calibration : demande seule, absence de progression, chevauchement, interruption, témoin séquentiel, simple revendication et processus Bash contrôlés.')


if __name__ == '__main__':
    if sys.argv[1:] == ['--self-test']:
        self_test()
    else:
        rows = [json.loads(line) for line in Path(sys.argv[1]).read_text().splitlines()]
        print(json.dumps(summarize(rows), ensure_ascii=False, indent=2))
