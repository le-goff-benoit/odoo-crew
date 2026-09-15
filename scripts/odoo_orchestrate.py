#!/usr/bin/env python3
"""État d'orchestration écrit par le principal ; garde Stop purement en lecture."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import uuid

import odoo_flow as flow
import odoo_plan as plan

STATUSES = {'active', 'waiting_human', 'waiting_resource', 'paused', 'interrupted', 'complete'}


def state_path(project):
    return Path(project).resolve() / '.odoo-agents/orchestration.json'


def update(project, action, *, owner=None, provider=None, model=None, session_id=None,
           release=None, tasks=None, phase=None, reason=None):
    project = Path(project).resolve()
    path = state_path(project)
    with flow.exclusive_lock(path):
        state = json.loads(path.read_text()) if path.exists() else None
        if action == 'activate':
            if not all((owner, provider in ('codex', 'claude'), model, session_id)):
                raise ValueError('propriétaire, fournisseur, modèle principal et session requis')
            if state and state['status'] not in ('complete', 'interrupted'):
                raise ValueError('orchestration existante : reprendre ou terminer explicitement')
            if state:
                archive = project / '.odoo-agents/orchestrations' / (state['id'] + '.json')
                if not archive.exists():
                    flow.write_state(archive, state)
            state = {'schema': 1, 'id': 'orchestration-' + uuid.uuid4().hex[:12], 'project': str(project),
                     'owner': owner, 'provider': provider, 'model': model, 'session_id': session_id,
                     'status': 'active', 'phase': phase or 'preparation', 'started_at': flow.now(),
                     'phase_started_at': flow.now(), 'revision': 0, 'authorized_tasks': [], 'history': []}
        else:
            if not state or owner != state['owner']:
                raise ValueError('seul le propriétaire de l’orchestration peut la modifier')
            if state['status'] == 'complete':
                raise ValueError('orchestration terminée')
            if action == 'resume':
                if not session_id:
                    raise ValueError('session de reprise requise')
                state['session_id'] = session_id
                state['status'] = 'active'
            elif action in ('pause', 'interrupt', 'complete', 'waiting-human', 'waiting-resource'):
                state['status'] = {'pause': 'paused', 'interrupt': 'interrupted', 'complete': 'complete',
                                   'waiting-human': 'waiting_human', 'waiting-resource': 'waiting_resource'}[action]
                if action in ('pause', 'interrupt', 'waiting-human', 'waiting-resource') and not reason:
                    raise ValueError('motif d’attente/arrêt requis')
                if action == 'complete':
                    if state.get('release'):
                        definition, root = plan.read(state['release'])
                        states = plan.statuses(definition, root)
                        if any(states[t][0] not in ('validated', 'deferred') for t in state['authorized_tasks']):
                            raise ValueError('tâches autorisées encore à traiter')
                    state['ended_at'] = flow.now()
            elif action not in ('progress', 'attach'):
                raise ValueError('action inconnue')
        if release:
            resolved, root = plan.location(release)
            if root != project:
                raise ValueError('release d’un autre projet')
            if state.get('release') and state['release'] != str(resolved):
                raise ValueError('orchestration déjà rattachée à une autre release')
            state['release'] = str(resolved)
        if tasks is not None:
            if not state.get('release'):
                raise ValueError('release requise pour autoriser des tâches')
            definition, _ = plan.read(state['release'])
            known = {t['id'] for t in definition['tasks']}
            if not set(tasks) <= known:
                raise ValueError('tâche autorisée inconnue')
            state['authorized_tasks'] = list(dict.fromkeys(tasks))
        if phase and phase != state['phase']:
            state['phase'] = phase
            state['phase_started_at'] = flow.now()
        state['reason'] = reason
        if action in ('activate', 'resume'):
            state['authorized_at'] = datetime.now(timezone.utc).isoformat()
        state['revision'] += 1
        state['history'].append({'at': flow.now(), 'action': action, 'phase': state['phase'],
                                 'status': state['status'], 'reason': reason, 'revision': state['revision']})
        flow.write_state(path, state)
        if state.get('release'):
            flow.write_state(Path(state['release']) / 'orchestration.json', dict(state))
        return state


def next_actions(state):
    if not state.get('release') or not state.get('authorized_tasks'):
        return []
    definition, project = plan.read(state['release'])
    states = plan.statuses(definition, project)
    result = []
    for task in definition['tasks']:
        if task['id'] not in state['authorized_tasks']:
            continue
        status = states[task['id']][0]
        if status == 'pending' and plan.available(definition, project, task['id'])[0]:
            result.append({'task': task['id'], 'action': 'start'})
        elif status == 'awaiting_receipt':
            result.append({'task': task['id'], 'action': 'receive'})
        elif status == 'running':
            path = plan.reference(project, task['attempts'][-1]['flow'])
            snapshot, graph = flow.load_state(path, flow.DEFAULT_GRAPH)
            for node, claim in snapshot.get('claims', {}).items():
                if claim.get('owner') == state.get('owner'):
                    result.append({'task': task['id'], 'action': 'resume_claim', 'node': node})
            for node in flow.ready_nodes(snapshot, graph):
                if graph['nodes'][node]['executor'] != 'human' and flow.claimability(snapshot, graph, node)['claimable']:
                    result.append({'task': task['id'], 'action': 'claim', 'node': node})
    return result


def interrupted_since_authorization(state, events):
    """Observe an interrupt even when the interrupted principal could not persist it."""
    path = Path(events)
    if not path.exists():
        return False
    if path.is_symlink() or path.stat().st_size > 64 * 1024 * 1024:
        return True  # Unknown collection must not grant a continuation.
    authorization = state.get('authorized_at') or next(
        (e['at'] for e in reversed(state.get('history', [])) if e.get('action') in ('activate', 'resume')),
        state.get('started_at'))
    try:
        started = datetime.fromisoformat(authorization.replace('Z', '+00:00')).timestamp()
        with path.open() as stream:
            for line in stream:
                event = json.loads(line)
                if (event.get('rootId') == state.get('session_id') and not event.get('parentId')
                        and event.get('kind') in ('Interrupt', 'StopFailure')):
                    at = datetime.fromisoformat(event['at'].replace('Z', '+00:00')).timestamp()
                    if at >= started:
                        return True
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return True
    return False


def hook(state, event, events=None):
    """Never writes, launches children, accepts evidence, releases locks or expands scope."""
    event_name = event.get('hook_event_name', event.get('event', ''))
    if event_name not in ('Stop', 'stop') or event.get('stop_hook_active'):
        return {}
    if state.get('status') != 'active' or state.get('session_id') != event.get('session_id', event.get('thread_id')):
        return {}
    if event.get('parent_thread_id') or event.get('parent_agent_id') or event.get('agent_type') not in (None, '', 'main', 'orchestrator'):
        return {}
    if events and interrupted_since_authorization(state, events):
        return {}
    actions = next_actions(state)
    if not actions:
        return {}
    upcoming = ', '.join(a['task'] + ':' + a['action'] + (':' + a['node'] if a.get('node') else '') for a in actions[:8])
    return {'decision': 'block', 'reason': 'Le run ' + state['id'] + ' est autorisé et encore actif. Actions prêtes : ' + upcoming +
            '. Reprends effectivement les outils de l’orchestrateur, réceptionne les preuves avant les dépendants, puis poursuis les tâches autorisées. '
            'Si une attente humaine, une interruption, une limite fournisseur ou un blocage réel empêche ce travail, enregistre cet état et termine. '
            'Ce rappel ne vaut ni réception ni autorisation supplémentaire.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['activate', 'attach', 'progress', 'pause', 'interrupt', 'resume', 'complete', 'waiting-human', 'waiting-resource', 'status', 'hook'])
    p.add_argument('--project', type=Path); p.add_argument('--state', type=Path)
    for option in ('owner', 'provider', 'model', 'session-id', 'release', 'phase', 'reason'):
        p.add_argument('--' + option)
    p.add_argument('--task', action='append')
    p.add_argument('--events', type=Path, help='Journal de métadonnées natif, lecture seule du garde')
    a = p.parse_args()
    if not a.project and not a.state:
        p.error('--project ou --state requis')
    path = a.state or state_path(a.project)
    if a.action in ('status', 'hook'):
        data = json.loads(path.read_text())
        if a.action == 'hook':
            raw = sys.stdin.read(1048577)
            if len(raw) > 1048576: return
            result = hook(data, json.loads(raw), a.events)
        else:
            result = data
    else:
        if not a.project: p.error('--project requis pour une mutation')
        result = update(a.project, a.action, owner=a.owner, provider=a.provider, model=a.model,
                        session_id=a.session_id, release=a.release, tasks=a.task, phase=a.phase, reason=a.reason)
    if result:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    try: main()
    except (OSError, ValueError, KeyError, TypeError, flow.FlowError) as exc:
        # Missing/malformed state never blocks a provider session.
        if 'hook' not in sys.argv[1:2]: sys.exit(str(exc))
