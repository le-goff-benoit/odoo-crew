#!/usr/bin/env python3
"""Contrats de pilotage : résultat métier, moyens de recette et livraison avec réserves."""
import argparse
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from odoo_documents import atomic, locked, reference, verify, within, read_json

API_VERSION = 1
_read_cache = ContextVar('crew_read_cache', default=None)


@contextmanager
def read_session():
    """Cache only within one immutable read; never shared across requests or threads."""
    if _read_cache.get() is not None:
        yield
        return
    token = _read_cache.set({})
    try:
        yield
    finally:
        _read_cache.reset(token)


def cached_statuses(plan, project, reader):
    cache = _read_cache.get()
    if cache is None:
        return reader(plan, project)
    key = (str(Path(project).resolve()), json.dumps(plan, sort_keys=True))
    if key not in cache:
        cache[key] = reader(plan, project)
    return deepcopy(cache[key])


def capabilities():
    return {'schema': API_VERSION, 'features': ['read_session', 'business_results', 'readiness', 'delivery_reservations', 'project_learnings']}


def typed_json(value):
    return json.dumps(value, sort_keys=True, allow_nan=False, separators=(',', ':'))


def business_results(root, contract_ref, observed_ref):
    """Expected values must be pinned independently; observed values come from raw JSON."""
    verify(root, contract_ref); verify(root, observed_ref)
    contract = read_json(within(root, contract_ref['path']))
    observed = read_json(within(root, observed_ref['path']))
    if contract.get('schema') != 1 or not contract.get('cases'):
        raise ValueError('contrat métier vide ou inconnu')
    cases = contract['cases']
    ids = [c['id'] for c in cases]
    if len(ids) != len(set(ids)) or not contract.get('reviewed_by') or not contract.get('basis'):
        raise ValueError('attendus indépendants relus requis')
    values = observed.get('cases', [])
    if len(values) != len(ids) or {c['id'] for c in values} != set(ids):
        raise ValueError('population métier différente du contrat')
    by_id = {c['id']: c for c in values}
    failed = []
    for case in cases:
        actual = by_id[case['id']]
        if not case.get('population') or typed_json(actual.get('population')) != typed_json(case['population']):
            raise ValueError('population non prouvée : ' + case['id'])
        if not isinstance(case.get('expected'), dict) or not case['expected']:
            raise ValueError('attendus chiffrés ou structurés requis')
        if typed_json(actual.get('observed')) != typed_json(case['expected']):
            failed.append(case['id'])
    if failed:
        raise ValueError('résultats métier différents des attendus : ' + ', '.join(failed))
    return {'passed': True, 'cases': len(cases), 'contract': contract_ref, 'observation': observed_ref,
            'limitation': 'La pertinence métier des attendus et la collecte des observations restent à relire.'}


def readiness(root, definition):
    """Evidence based capability check. Does not launch browsers or change access."""
    required = definition.get('required')
    if definition.get('schema') != 1 or not isinstance(required, list) or not required:
        raise ValueError('moyens de recette requis explicitement')
    if len(required) != len(set(required)):
        raise ValueError('moyen de recette dupliqué')
    if not definition.get('environment') or not definition.get('series'):
        raise ValueError('série et environnement requis')
    results = {r['id']: r for r in definition.get('checks', [])}
    pending = []
    for key in required:
        row = results.get(key, {})
        if row.get('status') != 'available':
            pending.append(key); continue
        verify(root, row['evidence'])
        evidence = read_json(within(root, row['evidence']['path']))
        if evidence.get('environment') != definition['environment'] or evidence.get('series') != definition['series'] or evidence.get('capability') != key or evidence.get('available') is not True:
            raise ValueError('observation incompatible : ' + key)
    return {'ready': not pending, 'unavailable': pending, 'environment': definition['environment'], 'series': definition['series']}


def validate_delivery(root, release, definition):
    from odoo_knowledge import release_path, validate
    folder = release_path(root, release)
    if definition.get('status') not in ('published', 'published_with_reservations', 'deployed_verified'):
        raise ValueError('état de livraison inconnu')
    tasks = definition.get('tasks')
    if not definition.get('target') or not isinstance(tasks, list) or not tasks or len(tasks) != len(set(tasks)):
        raise ValueError('cible et tâches uniques requises')
    plan = read_json(folder / 'plan.json')
    selected = [t for t in plan['tasks'] if t['id'] in tasks]
    if len(selected) != len(tasks):
        raise ValueError('tâche livrée absente du plan')
    verify(root, definition['evidence'])
    if definition['status'] == 'deployed_verified':
        row = read_json(within(root, definition['evidence']['path']))
        if row.get('kind') != 'deployment' or row.get('state') != 'accepted':
            raise ValueError('observation de déploiement acceptée requise')
        validate(root, release, row)
        contract = read_json(within(root, row['delivery']['contract']['path']))
        if definition['target'] != contract['target_environment']:
            raise ValueError('environnement cible différent du déploiement observé')
        if set(row.get('tasks', [])) != set(tasks):
            raise ValueError('tâches différentes de la déclaration relue de déploiement')
        scopes = {m['path'] for m in contract['modules'].values()}
        if any(not t.get('scopes') or any(not any(p == m or p.startswith(m + '/') for m in scopes) for p in t['scopes']) for t in selected):
            raise ValueError('périmètre des tâches absent du contrat de livraison')
    if definition['status'] == 'published_with_reservations':
        if not definition.get('reservations'):
            raise ValueError('réserves explicites requises')
        verify(root, definition['decision'])
        for item in definition['reservations']:
            if not all(item.get(k) for k in ('missing_control', 'next_action', 'owner')):
                raise ValueError('contrôle manquant, prochaine action et responsable requis')


def delivery_record(root, release, definition):
    """Store publication and explicit reservations without modifying QA closure."""
    from odoo_knowledge import release_path, validate
    from odoo_flow import now
    root = Path(root).resolve(); folder = release_path(root, release)
    validate_delivery(root, release, definition)
    path = within(root, f'changelog/{release}/delivery-status.json')
    with locked(root):
        data = read_json(path) if path.exists() else {'schema': 1, 'history': []}
        previous = data.get('current', {})
        old_reserves = previous.get('reservations', [])
        removed = [r for r in old_reserves if r not in definition.get('reservations', [])]
        if removed:
            resolutions = definition.get('resolutions', [])
            for reserve in removed:
                resolved = next((r for r in resolutions if r.get('reservation') == reserve), None)
                if not resolved or not resolved.get('result'):
                    raise ValueError('résolution sourcée de chaque réserve requise')
                verify(root, resolved['evidence'])
        if data.get('current') == definition:
            return data
        if data.get('current'):
            data['history'].append({'at': data.get('updated_at'), 'record': data['current']})
        data.update(current=deepcopy(definition), updated_at=now())
        atomic(path, data)
    return data


def delivery_snapshot(root, release):
    path = within(root, f'changelog/{release}/delivery-status.json')
    if not path.exists():
        return {'status': 'unknown', 'verified': False, 'tasks': []}
    data = read_json(path); row = data['current']
    validate_delivery(root, release, row)
    return {**row, 'verified': row['status'] == 'deployed_verified'}


def learning_projection(root, release, row):
    if row['kind'] != 'discovery' or row['state'] != 'accepted':
        return None
    path = within(root, '.odoo-agents/LEARNINGS.json')
    data = read_json(path) if path.exists() else {'schema': 1, 'items': []}
    identifier = release + '--' + row['id']
    item = {k: deepcopy(row[k]) for k in ('statement', 'scope', 'sources', 'review', 'reviewed_by')}
    item.update(id=identifier, release=release, state='accepted', exceptions=row.get('exceptions', []),
                effect=row.get('effect', ''), origin=f'changelog/{release}/knowledge/{row["id"]}.json')
    existing = next((r for r in data['items'] if r['id'] == identifier), None)
    if existing:
        if any(existing.get(k) != v for k, v in item.items()):
            raise ValueError('apprentissage immuable : remplacement explicite requis')
        return data
    predecessor = row.get('supersedes_project') or (release + '--' + row['supersedes'] if row.get('supersedes') else None)
    if predecessor:
        old = next((r for r in data['items'] if r['id'] == predecessor), None)
        if not old:
            previous = read_json(within(root, f'changelog/{release}/knowledge/{row["supersedes"]}.json')) if row.get('supersedes') else {}
            if previous.get('state') != 'proposed':
                raise ValueError('apprentissage remplacé absent')
        elif old.get('state') != 'accepted':
            raise ValueError('remplacement concurrent')
        else:
            old.update(state='superseded', superseded_by=identifier)
    data['items'].append(item)
    return data


def learnings(root, release=None):
    path = within(root, '.odoo-agents/LEARNINGS.json')
    if not path.exists():
        return []
    result = []
    for row in read_json(path)['items']:
        if row.get('state') != 'accepted' or release and row.get('release') != release:
            continue
        valid = True
        try:
            origin = read_json(within(root, row['origin']))
            if origin.get('kind') != 'discovery' or origin.get('state') != 'accepted':
                raise ValueError('origine non acceptée')
            for key in ('statement', 'scope', 'sources', 'review', 'reviewed_by', 'effect', 'exceptions'):
                default = [] if key == 'exceptions' else '' if key == 'effect' else None
                if typed_json(row.get(key, default)) != typed_json(origin.get(key, default)):
                    raise ValueError('projection modifiée')
            for ref in row['sources'] + [row['review']]:
                verify(root, ref)
        except (ValueError, OSError):
            valid = False
        result.append({**row, 'current': valid, 'project_learning': True, 'freshness': 'verified' if valid else 'stale'})
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('capabilities', 'readiness', 'delivery', 'business-results'))
    p.add_argument('project', type=Path); p.add_argument('--release'); p.add_argument('--file', type=Path)
    a = p.parse_args()
    if a.action == 'capabilities':
        result = capabilities()
    else:
        if not a.file: p.error('--file requis')
        data = read_json(a.file)
        if a.action == 'readiness': result = readiness(a.project, data)
        elif a.action == 'delivery': result = delivery_record(a.project, a.release, data)
        else: result = business_results(a.project, data['contract'], data['observation'])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get('ready') is False else 0


if __name__ == '__main__':
    raise SystemExit(main())
