#!/usr/bin/env python3
"""Plan de release versionné ; le graphe reste l'autorité des étapes d'exécution."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import uuid

import odoo_flow as flow
from odoo_evidence import fingerprint, verify

ROOT = Path(__file__).resolve().parents[1]


def location(release):
    release = Path(release).resolve()
    if release.parent.name != 'changelog' or not (release / 'README.md').is_file():
        raise ValueError('dossier changelog/<release> requis')
    return release, release.parent.parent


def reference(project, name, *, directory=False):
    path = (project / name).resolve()
    if not path.is_relative_to(project) or (not path.is_dir() if directory else not path.is_file()):
        raise ValueError('référence absente ou hors projet : ' + name)
    return path


def validate(plan, project):
    if plan.get('schema') != 1 or not isinstance(plan.get('tasks'), list) or not plan['tasks']:
        raise ValueError('plan schema 1 avec tâches requis')
    ids = [t.get('id') for t in plan['tasks']]
    if any(not isinstance(i, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,40}', i) for i in ids) or len(set(ids)) != len(ids):
        raise ValueError('identifiants uniques et stables requis')
    by_id = {t['id']: t for t in plan['tasks']}
    for task in plan['tasks']:
        for field in ('title', 'request', 'acceptance', 'scopes', 'risk', 'route'):
            if not task.get(field):
                raise ValueError(task['id'] + ' : ' + field + ' manquant')
        if task['route'] not in ('module', 'studio', 'standard') or task['risk'] not in ('normal', 'high'):
            raise ValueError('voie ou risque invalide')
        if not isinstance(task['acceptance'], list) or any(not isinstance(x, str) or not x.strip() for x in task['acceptance']):
            raise ValueError('critères explicites requis')
        reference(project, task['request'])
        for scope in task['scopes']:
            # Un futur module peut ne pas encore exister ; son parent doit rester dans le projet.
            if Path(scope).is_absolute() or not (project / scope).resolve().is_relative_to(project) or scope in ('.', ''):
                raise ValueError('périmètre relatif borné requis')
        for dep in task.get('depends_on', []):
            if dep not in by_id or dep == task['id']:
                raise ValueError('dépendance inconnue ou réflexive')
    def visit(identifier, seen):
        if identifier in seen:
            raise ValueError('cycle dans les dépendances')
        for dep in by_id[identifier].get('depends_on', []):
            visit(dep, seen | {identifier})
    for identifier in ids:
        visit(identifier, set())


def read(release):
    release, project = location(release)
    plan = json.loads((release / 'plan.json').read_text())
    validate(plan, project)
    return plan, project


def contract_hash(task, project):
    contract = {key: task.get(key) for key in ('id', 'title', 'request', 'acceptance', 'scopes', 'risk', 'route', 'depends_on')}
    contract['request_sha256'] = flow.graph_hash(reference(project, task['request']))
    import hashlib
    return hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest()


def task_status(task, project):
    if task.get('deferred'):
        return 'deferred', task['deferred']['reason']
    receipt = task.get('receipt')
    if receipt:
        try:
            if receipt.get('contract_sha256') != contract_hash(task, project):
                raise ValueError('contrat de tâche changé après réception')
            for item in (receipt['acceptance'], receipt['memory']):
                path = reference(project, item['path'])
                if flow.graph_hash(path) != item['sha256']:
                    raise ValueError('passation modifiée après validation')
            proof_path = reference(project, receipt['proof']['path'])
            if flow.graph_hash(proof_path) != receipt['proof']['sha256']:
                raise ValueError('preuve remplacée')
            verify(json.loads(proof_path.read_text()), expected_project=project)
            return 'validated', 'preuve et passation toujours valides'
        except (OSError, ValueError, KeyError) as exc:
            return 'stale', str(exc)
    attempts = task.get('attempts', [])
    if not attempts:
        return 'pending', ''
    try:
        state = json.loads(reference(project, attempts[-1]['flow']).read_text())
    except (OSError, ValueError):
        return 'interrupted', 'état local absent : réception durable non validée ; réconcilier explicitement'
    if state['status'] == 'complete':
        return 'awaiting_receipt', 'graphe terminé ; preuve et consolidation attendues'
    if state['status'] in ('blocked', 'cancelled'):
        return 'blocked', state['status']
    return 'running', attempts[-1]['flow']


def receipt_hash(receipt):
    import hashlib
    return hashlib.sha256(json.dumps(receipt, sort_keys=True).encode()).hexdigest()


def statuses(plan, project):
    states = {task['id']: task_status(task, project) for task in plan['tasks']}
    by_id = {task['id']: task for task in plan['tasks']}
    for task in plan['tasks']:
        if states[task['id']][0] == 'validated':
            expected = task['receipt'].get('dependencies', {})
            current = {d: receipt_hash(by_id[d].get('receipt')) for d in task.get('depends_on', [])}
            if expected != current:
                states[task['id']] = ('stale', 'réception d’une dépendance changée : nouvelle validation requise')
    # Propager les preuves périmées aux tâches qui en dépendaient.
    for _ in plan['tasks']:
        for task in plan['tasks']:
            deps = task.get('depends_on', [])
            bad = [d for d in deps if states[d][0] != 'validated']
            if bad and states[task['id']][0] == 'validated':
                states[task['id']] = ('stale', 'dépendances non validées : ' + ', '.join(bad))
    return states


def overlapping(first, second, project):
    return any((project / a).resolve().is_relative_to((project / b).resolve()) or
               (project / b).resolve().is_relative_to((project / a).resolve())
               for a in first for b in second)


def available(plan, project, identifier):
    states = statuses(plan, project)
    task = next(t for t in plan['tasks'] if t['id'] == identifier)
    if states[identifier][0] != 'pending':
        return False, states[identifier][1] or states[identifier][0]
    deps = [d for d in task.get('depends_on', []) if states[d][0] != 'validated']
    if deps:
        return False, 'dépendances : ' + ', '.join(deps)
    for other in plan['tasks']:
        if other['id'] != identifier and states[other['id']][0] in ('running', 'awaiting_receipt', 'interrupted'):
            if overlapping(task['scopes'], other['scopes'], project):
                return False, 'périmètre réservé par ' + other['id']
    return True, 'revendicable'


def save(release, plan):
    flow.write_state(release / 'plan.json', plan)


def initialise(release, definition):
    release, project = location(release)
    validate(definition, project)
    plan = deepcopy(definition)
    if any(set(t) & {'receipt', 'attempts', 'deferred'} for t in plan['tasks']):
        raise ValueError('une définition ne peut importer un état validé')
    with flow.exclusive_lock(release / 'plan.json'):
        if (release / 'plan.json').exists():
            raise ValueError('plan existant : ne pas écraser son historique')
        plan['history'] = [{'at': flow.now(), 'action': 'prepared'}]
        save(release, plan)


def append_tasks(release, definition):
    release, project = location(release)
    tasks = deepcopy(definition.get('tasks', []))
    if definition.get('schema') != 1 or not tasks:
        raise ValueError('ajout schema 1 avec tâches requis')
    if any(set(t) & {'receipt', 'attempts', 'deferred'} for t in tasks):
        raise ValueError('une définition ne peut importer un état validé')
    with flow.exclusive_lock(release / 'plan.json'):
        plan, project = read(release)
        plan['tasks'].extend(tasks)
        validate(plan, project)
        plan['history'].append({'at': flow.now(), 'action': 'added', 'tasks': [t['id'] for t in tasks]})
        save(release, plan)


def source_snapshot(project, scopes):
    return fingerprint(project, [s for s in scopes if (project / s).exists()], allow_empty=True)


def mutate(release, action, identifier, *, proof=None, acceptance=None, memory=None, reason=None):
    release, project = location(release)
    with flow.exclusive_lock(release / 'plan.json'):
        plan, project = read(release)
        task = next((t for t in plan['tasks'] if t['id'] == identifier), None)
        if task is None:
            raise ValueError('tâche inconnue')
        state, _ = task_status(task, project)
        if action == 'start':
            ready, why = available(plan, project, identifier)
            if not ready:
                raise ValueError(why)
            before = source_snapshot(project, task['scopes'])
            run_id = 'plan-' + identifier.lower() + '-' + uuid.uuid4().hex[:8]
            flow.ensure_local_flow_dirs(project)
            path = project / '.odoo-agents/flows' / (run_id + '.json')
            graph = ROOT / 'workflows/odoo-workflow.json'
            current = flow.new_state(project, 'development', run_id, graph)
            # Le graphe gère les verrous courts ; le plan réserve les périmètres de toute la tâche.
            current['plan_task'] = {'release': str(release), 'id': identifier, 'risk': task['risk']}
            flow.write_state(path, current)
            task.setdefault('attempts', []).append({'flow': str(path.relative_to(project)),
                                                   'at': flow.now(), 'sources_before': before})
            result = str(path)
        elif action == 'finish':
            attempts = task.get('attempts', [])
            if not attempts or json.loads(reference(project, attempts[-1]['flow']).read_text())['status'] != 'complete':
                raise ValueError('le graphe doit être terminé avant la réception')
            current_states = statuses(plan, project)
            if any(current_states[d][0] != 'validated' for d in task.get('depends_on', [])):
                raise ValueError('dépendances à réceptionner avant cette tâche')
            proof_path = reference(project, proof or '')
            evidence = json.loads(proof_path.read_text())
            verify(evidence, expected_project=project)
            # Une preuve sur un fichier sans lien ne valide pas le périmètre de la tâche.
            required = fingerprint(project, task['scopes'])
            if not set(required) <= set(evidence['sources']):
                raise ValueError('preuve ne couvrant pas tout le périmètre')
            receipt = {}
            for key, value in [('proof', proof), ('acceptance', acceptance), ('memory', memory)]:
                path = reference(project, value or '')
                if not path.read_text().strip():
                    raise ValueError('preuve vide : ' + key)
                receipt[key] = {'path': str(path.relative_to(project)), 'sha256': flow.graph_hash(path)}
            receipt['at'] = flow.now(); receipt['contract_sha256'] = contract_hash(task, project)
            by_id = {t['id']: t for t in plan['tasks']}
            receipt['dependencies'] = {d: receipt_hash(by_id[d].get('receipt')) for d in task.get('depends_on', [])}
            if task.get('receipt'):
                plan['history'].append({'at': flow.now(), 'action': 'previous_receipt', 'task_id': identifier, 'receipt': deepcopy(task['receipt'])})
            task['receipt'] = receipt
            result = 'validé ; contenu métier de la réception à relire par l’orchestrateur'
        elif action in ('reopen', 'defer'):
            if not reason:
                raise ValueError('décision motivée requise')
            if state in ('running', 'awaiting_receipt'):
                raise ValueError('libérer/terminer le graphe avant de modifier le plan')
            if action == 'defer':
                task['deferred'] = {'reason': reason, 'at': flow.now()}
            else:
                # L'historique contient la réception invalidée ; aucun faux statut conservé.
                plan['history'].append({'at': flow.now(), 'action': 'previous_attempt', 'task': deepcopy(task)})
                for key in ('receipt', 'attempts', 'deferred'):
                    task.pop(key, None)
            result = action
        else:
            raise ValueError('action inconnue')
        plan['history'].append({'at': flow.now(), 'action': action, 'task_id': identifier, 'reason': reason})
        save(release, plan)
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['init', 'add', 'status', 'changed', 'start', 'finish', 'reopen', 'defer'])
    parser.add_argument('release', type=Path)
    parser.add_argument('--file', type=Path)
    parser.add_argument('--task'); parser.add_argument('--proof'); parser.add_argument('--acceptance'); parser.add_argument('--memory'); parser.add_argument('--reason')
    args = parser.parse_args()
    if args.action in ('init', 'add'):
        if not args.file:
            parser.error('--file requis')
        (initialise if args.action == 'init' else append_tasks)(args.release, json.loads(args.file.read_text()))
    elif args.action == 'changed':
        plan, project = read(args.release)
        task = next(t for t in plan['tasks'] if t['id'] == args.task)
        before = task['attempts'][-1]['sources_before']
        after = source_snapshot(project, task['scopes'])
        for name in sorted(before.keys() | after.keys()):
            if before.get(name) != after.get(name):
                print(name)
    elif args.action == 'status':
        plan, project = read(args.release); states = statuses(plan, project)
        for task in plan['tasks']:
            ready, why = available(plan, project, task['id'])
            print(f"{task['id']} · {states[task['id']][0]} · {'PRÊT' if ready else why} · {task['title']}")
    else:
        print(mutate(args.release, args.action, args.task, proof=args.proof, acceptance=args.acceptance, memory=args.memory, reason=args.reason))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, flow.FlowError) as exc:
        sys.exit(str(exc))
