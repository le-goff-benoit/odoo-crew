#!/usr/bin/env python3
"""Registre versionné des intentions ; l'orchestrateur conserve la source et arbitre."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sys

import odoo_flow as flow

STATUSES = {'clarify', 'ready', 'planned', 'satisfied', 'deferred'}


def read(path):
    data = json.loads(Path(path).read_text())
    if data.get('schema') != 1 or not isinstance(data.get('items'), list):
        raise ValueError('registre intentions schema 1 requis')
    ids = [i.get('id') for i in data['items']]
    if len(ids) != len(set(ids)):
        raise ValueError('identifiants dupliqués')
    for item in data['items']:
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,40}', item.get('id', '')) or item.get('status') not in STATUSES:
            raise ValueError('identifiant ou état d’intention invalide')
        if not item.get('text') or not item.get('purpose') or not item.get('source', {}).get('sha256'):
            raise ValueError('texte, résultat attendu et source conservée requis')
        for key in ('questions', 'constraints', 'decisions', 'tasks'):
            if not isinstance(item.get(key), list):
                raise ValueError(key + ' doit être une liste')
        if item['questions'] and item['status'] not in ('clarify', 'deferred'):
            raise ValueError('question bloquante non résolue')
    return data


def update(release, definition):
    from odoo_plan import location, reference
    release, project = location(release)
    path = release / 'intentions.json'
    with flow.exclusive_lock(path):
        data = read(path) if path.exists() else {'schema': 1, 'revision': 0, 'items': [], 'history': []}
        for raw in definition.get('items', []):
            item = deepcopy(raw)
            old = next((i for i in data['items'] if i['id'] == item['id']), None)
            source = reference(project, item['source']['path'])
            content = source.read_text()
            # Preserve the original bytes in the register; later requests never erase them.
            item['source'] = {'path': str(source.relative_to(project)), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'original': content}
            if old and old['source']['path'] == item['source']['path'] and not raw['source'].get('refresh'):
                item['source'] = deepcopy(old['source'])
            for key in ('questions', 'constraints', 'decisions', 'tasks'):
                item.setdefault(key, [])
            item.setdefault('criteria', [item.get('purpose', '')])
            item.setdefault('coverage', [])
            item.setdefault('status', 'clarify' if item['questions'] else 'ready')
            if item['status'] == 'satisfied':
                raise ValueError('utiliser satisfy avec réception vérifiée')
            old = next((i for i in data['items'] if i['id'] == item['id']), None)
            if old:
                data['history'].append({'at': flow.now(), 'action': 'revised', 'item': deepcopy(old)})
                data['items'][data['items'].index(old)] = item
            else:
                data['items'].append(item)
                data['history'].append({'at': flow.now(), 'action': 'created', 'id': item['id']})
        # Validate before the atomic replace, without writing an invalid intermediary.
        validate_data(data)
        data['revision'] += 1
        flow.write_state(path, data)
        return data


def validate_data(data):
    # Same validation as read, without temporary files.
    if len({i['id'] for i in data['items']}) != len(data['items']):
        raise ValueError('identifiants dupliqués')
    for i in data['items']:
        if not isinstance(i.get('criteria', [i.get('purpose')]), list) or not all(isinstance(c, str) and c.strip() for c in i.get('criteria', [i.get('purpose')])):
            raise ValueError('critères explicites d’intention requis')
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,40}', i.get('id', '')) or not i.get('text') or not i.get('purpose'):
            raise ValueError('identifiant, texte et résultat attendu requis')
        if i.get('status') not in STATUSES or any(not isinstance(i.get(k), list) for k in ('questions', 'constraints', 'decisions', 'tasks')):
            raise ValueError('état ou listes invalides')
        if i['questions'] and i['status'] not in ('clarify', 'deferred'):
            raise ValueError('question bloquante non résolue')


def reconcile(release, identifier=None, standard_proof=None):
    from odoo_plan import location, read as read_plan, statuses, reference
    from odoo_evidence import verify
    release, project = location(release)
    path = release / 'intentions.json'
    with flow.exclusive_lock(path):
        data = read(path)
        plan, _ = read_plan(release) if (release / 'plan.json').exists() else ({'tasks': []}, project)
        states = statuses(plan, project)
        for item in data['items']:
            if identifier and item['id'] != identifier:
                continue
            old = deepcopy(item)
            item['tasks'] = [t['id'] for t in plan['tasks'] if item['id'] in t.get('intentions', [])]
            if item['status'] != 'deferred':
                if item['questions']:
                    item['status'] = 'clarify'
                elif item['tasks']:
                    by_task = {t['id']: t for t in plan['tasks']}
                    criteria = set(item.get('criteria', [item['purpose']]))
                    covered = set()
                    for link in item.get('coverage', []):
                        task = by_task.get(link.get('task'))
                        if task and task['id'] in item['tasks'] and link.get('task_criterion') in task['acceptance'] and states[task['id']][0] == 'validated':
                            covered.add(link.get('criterion'))
                    item['status'] = 'satisfied' if criteria and criteria <= covered and all(states[t][0] == 'validated' for t in item['tasks']) else 'planned'
                else:
                    item['status'] = 'ready'
            if identifier == item['id'] and standard_proof:
                proof_path = reference(project, standard_proof)
                verify(json.loads(proof_path.read_text()), project)
                if item['questions'] or item['tasks']:
                    raise ValueError('solution standard réservée à une intention sans tâche ni question')
                item['standard_proof'] = {'path': standard_proof, 'sha256': flow.graph_hash(proof_path)}
                item['status'] = 'satisfied'
            elif item.get('standard_proof') and not item['tasks'] and not item['questions']:
                try:
                    proof_path = reference(project, item['standard_proof']['path'])
                    if flow.graph_hash(proof_path) != item['standard_proof']['sha256']:
                        raise ValueError('preuve remplacée')
                    verify(json.loads(proof_path.read_text()), project)
                    item['status'] = 'satisfied'
                except (ValueError, OSError, KeyError):
                    item['status'] = 'ready'
            if old != item:
                data['history'].append({'at': flow.now(), 'action': 'reconciled', 'item': old})
        data['revision'] += 1
        flow.write_state(path, data)
        return data


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['update', 'status', 'reconcile', 'satisfy'])
    p.add_argument('release', type=Path); p.add_argument('--file', type=Path)
    p.add_argument('--intention'); p.add_argument('--proof')
    a = p.parse_args()
    if a.action == 'update':
        if not a.file: p.error('--file requis')
        result = update(a.release, json.loads(a.file.read_text()))
    elif a.action in ('reconcile', 'satisfy'):
        if a.action == 'satisfy' and not (a.intention and a.proof): p.error('--intention et --proof requis')
        result = reconcile(a.release, a.intention, a.proof)
    else:
        result = read(a.release / 'intentions.json')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try: main()
    except (ValueError, OSError, KeyError) as exc: sys.exit(str(exc))
