#!/usr/bin/env python3
"""Isoler un candidat QA ; le plan et le registre physique conservent l'autorité."""
import argparse
import json
from pathlib import Path
import sys

import odoo_flow as flow
import odoo_plan as plan
from odoo_evidence import fingerprint, repository_identity

REQUIRED = {'database', 'filestore', 'port', 'container', 'logs'}


def resources(value):
    if not isinstance(value, dict) or not REQUIRED <= value.keys():
        raise ValueError('identités physiques database/filestore/port/container/logs requises')
    return {k: flow.canonical_resource(v) for k, v in value.items()}


def valid(candidate):
    try:
        root = Path(candidate['project']).resolve()
        return repository_identity(root) == candidate['repository'] and fingerprint(root, candidate['scopes']) == candidate['sources']
    except (KeyError, OSError, ValueError):
        return False


def active_for_task(task, project):
    try:
        attempt = task['attempts'][-1]
        path = plan.reference(project, attempt['flow'])
        state, graph = flow.load_state(path, flow.DEFAULT_GRAPH)
        candidate = state.get('candidate')
        if state['status'] != 'active' or not candidate or candidate != attempt.get('candidate') or not valid(candidate):
            return False
        nodes = set(flow.ready_nodes(state, graph)) | set(state.get('claims', {}))
        return bool(nodes) and all(graph['nodes'][node].get('role') == 'odoo-tester' for node in nodes)
    except (OSError, ValueError, KeyError, flow.FlowError):
        return False


def isolated(candidate, task):
    if not valid(candidate):
        return False
    try:
        wanted = resources(task.get('resources'))
        current = resources(candidate['resources'])
        return flow.locks_compatible([{'resource': r, 'mode': 'write'} for r in wanted.values()],
                                     [{'resource': r, 'mode': 'write'} for r in current.values()])
    except (ValueError, TypeError):
        return False


def freeze(release, identifier, candidate_root, declared_resources):
    release, project = plan.location(release)
    candidate_root = Path(candidate_root).resolve()
    source_id, candidate_id = repository_identity(project), repository_identity(candidate_root)
    if candidate_root == project or candidate_root.is_relative_to(project) or not source_id or source_id != candidate_id:
        raise ValueError('worktree distinct du même dépôt et de la même révision requis')
    physical = resources(declared_resources)
    with flow.exclusive_lock(release / 'plan.json'):
        definition, _ = plan.read(release)
        task = next(t for t in definition['tasks'] if t['id'] == identifier)
        if plan.task_status(task, project)[0] != 'running':
            raise ValueError('tâche en cours requise')
        path = plan.reference(project, task['attempts'][-1]['flow'])
        with flow.exclusive_lock(path):
            state, graph = flow.load_state(path, flow.DEFAULT_GRAPH)
            ready = flow.ready_nodes(state, graph)
            if state.get('claims') or not ready or any(graph['nodes'][n].get('role') != 'odoo-tester' for n in ready):
                raise ValueError('borne QA sans revendication active requise')
            scopes = list(dict.fromkeys(task.get('check_scopes', task['scopes']) + task.get('reads', [])))
            captured = fingerprint(candidate_root, scopes)
            if captured != fingerprint(project, scopes):
                raise ValueError('le candidat ne contient pas exactement les sources à contrôler')
            candidate = {'project': str(candidate_root), 'repository': candidate_id, 'scopes': scopes,
                         'sources': captured, 'resources': physical, 'frozen_at': flow.now()}
            if not state.get('resource_registry'):
                raise ValueError('déclarer le registre physique partagé avant le gel du candidat')
            registry = flow.registry_path(state)
            # Rebinding does not bypass existing physical leases. claim checks the same registry atomically.
            with flow.exclusive_lock(registry):
                registered = flow.load_registry(registry)
                wanted = [{'resource': r, 'mode': 'write'} for r in physical.values()]
                if any(not flow.locks_compatible(wanted, c.get('locks', [])) for c in registered['claims']):
                    raise ValueError('ressource QA déjà occupée')
                state['resource_registry'] = str(registry)
                state['candidate_original_bindings'] = dict(state.get('resource_bindings', {}))
                state.setdefault('resource_bindings', {}).update({
                    'module_code': {'id': 'path:' + str(candidate_root)},
                    'qa_db_module': {'id': physical['database']},
                })
                state['candidate'] = candidate
                flow.write_state(path, state)
            task['attempts'][-1]['candidate'] = candidate
            definition['history'].append({'at': flow.now(), 'action': 'candidate_frozen', 'task_id': identifier, 'candidate': str(candidate_root)})
            plan.save(release, definition)
            return candidate


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['freeze', 'verify']); p.add_argument('release', type=Path)
    p.add_argument('--task', required=True); p.add_argument('--candidate', type=Path); p.add_argument('--resources', type=Path)
    a = p.parse_args()
    if a.action == 'freeze':
        if not a.candidate or not a.resources: p.error('--candidate et --resources requis')
        result = freeze(a.release, a.task, a.candidate, json.loads(a.resources.read_text()))
    else:
        definition, _ = plan.read(a.release)
        candidate = next(t for t in definition['tasks'] if t['id'] == a.task)['attempts'][-1]['candidate']
        if not valid(candidate): raise ValueError('candidat changé : QA à reprendre')
        result = candidate
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try: main()
    except (OSError, ValueError, KeyError, StopIteration, flow.FlowError) as exc: sys.exit(str(exc))
