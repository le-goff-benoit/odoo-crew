#!/usr/bin/env python3
"""Sélection conservatrice des scénarios métier sourcés et exécution prouvée."""
import argparse
import fnmatch
import json
from pathlib import Path
import sys

from odoo_memory import source
from odoo_evidence import execute


def validate(catalog, project):
    if catalog.get('schema') != 1 or not catalog.get('scenarios'):
        raise ValueError('catalogue schema 1 non vide requis')
    ids = set()
    for row in catalog['scenarios']:
        if row.get('id') in ids:
            raise ValueError('scénario dupliqué')
        ids.add(row.get('id'))
        for field in ('id', 'rule', 'source', 'actor', 'setup', 'expected', 'forbidden', 'triggers', 'scopes', 'command', 'group'):
            if not row.get(field):
                raise ValueError('scénario incomplet : ' + field)
        if row['group'] not in ('server', 'browser', 'data') or not isinstance(row['command'], list) or any(not isinstance(x, str) for x in row['command']):
            raise ValueError('groupe ou commande invalide')
        source(project, row['source'])
        for scope in row['scopes']:
            if not (project / scope).resolve().is_relative_to(project):
                raise ValueError('scope hors projet')


def select(catalog, project, changes, uncertain=False, group=None):
    validate(catalog, project)
    rows = catalog['scenarios']
    # Un fichier sans correspondance peut être une dépendance oubliée : élargir.
    unknown = [f for f in changes if not any(fnmatch.fnmatch(f, pattern) for row in rows for pattern in row['triggers'])]
    full = uncertain or not changes or bool(unknown)
    selected = [row for row in rows if (full or any(fnmatch.fnmatch(f, pattern) for f in changes for pattern in row['triggers'])) and (not group or row['group'] == group)]
    return {'selected': [r['id'] for r in selected], 'full': full, 'unknown_changes': unknown,
            'group': group, 'reason': 'sélection élargie : impact inconnu' if full else 'déclencheurs explicites'}


def run(catalog, project, ids, output):
    validate(catalog, project)
    rows = {r['id']: r for r in catalog['scenarios']}
    if not ids or set(ids) - rows.keys():
        raise ValueError('liste de scénarios non vide et connue requise')
    output.mkdir(parents=True, exist_ok=True)
    proofs = []
    for identifier in ids:
        if '/' in identifier or '..' in identifier:
            raise ValueError('identifiant non sûr')
        row = rows[identifier]
        path = output / (identifier + '.json')
        if path.exists():
            raise ValueError('preuve existante : choisir un nouveau dossier de campagne')
        scopes = list(dict.fromkeys([*row['scopes'], row['source']['path']]))
        result = execute(project, scopes, path, row['command'], module=row.get('module'))
        proofs.append({'id': identifier, 'proof': str(path), 'result': result['result']})
    return proofs


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('action', choices=['select', 'run'])
    p.add_argument('project', type=Path); p.add_argument('--catalog', type=Path)
    p.add_argument('--changed', nargs='*', default=[]); p.add_argument('--uncertain', action='store_true')
    p.add_argument('--group', choices=['server', 'browser', 'data']); p.add_argument('--ids', nargs='+'); p.add_argument('--output', type=Path)
    a = p.parse_args(); project = a.project.resolve()
    try:
        catalog = json.loads((a.catalog or project / '.odoo-agents/SCENARIOS.json').read_text())
        if a.action == 'select':
            result = select(catalog, project, a.changed, a.uncertain, a.group)
        else:
            if not a.output:
                p.error('--output requis')
            result = run(catalog, project, a.ids, a.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError) as e:
        sys.exit(str(e))
