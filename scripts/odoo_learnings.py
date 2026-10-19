#!/usr/bin/env python3
"""Fiches consultables des apprentissages de release, sans nouvelle autorité mémoire."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re

from odoo_documents import atomic, locked, read_json, reference, within
from odoo_pilotage import learnings

GENERATOR = 'odoo_learnings.py/schema-1'


def export(root):
    """Materialize accepted, stale and superseded records; never promote a proposal.

    LEARNINGS.json and immutable release contributions remain authoritative.
    A failed export can be retried; no existing source or receipt is changed.
    """
    root = Path(root).resolve()
    registry = within(root, '.odoo-agents/LEARNINGS.json')
    if not registry.exists():
        return {'directory': None, 'current': 0, 'historical': 0, 'warnings': []}
    with locked(root):
        source = reference(root, '.odoo-agents/LEARNINGS.json')
        data = read_json(registry)
        if data.get('schema') != 1 or not isinstance(data.get('items'), list):
            raise ValueError('registre des apprentissages invalide')
        checked = {row['id']: row for row in learnings(root)}
        folder = root / '.odoo-agents/learnings'
        if folder.is_symlink():
            raise ValueError('dossier de fiches symbolique : conserver et arbitrer')
        outputs, identifiers, warnings = {}, set(), []
        current = 0
        for item in data['items']:
            identifier = item.get('id', '')
            if not re.fullmatch(r'[A-Za-z0-9_.-]+', identifier) or identifier in identifiers:
                raise ValueError('identifiant de fiche invalide ou dupliqué')
            identifiers.add(identifier)
            # Only the existing reviewed projection is eligible; drafts stay in the release.
            if item.get('state') not in ('accepted', 'superseded'):
                raise ValueError('état inattendu dans le registre accepté')
            row = checked.get(identifier)
            valid = bool(row and row['current'])
            current += int(valid)
            status = 'current' if valid else 'superseded' if item['state'] == 'superseded' else 'stale'
            if status == 'stale':
                warnings.append('Apprentissage périmé à revérifier : ' + identifier)
            card = {'schema': 1, 'generated_by': GENERATOR, 'registry': source,
                    'status': status, 'learning': deepcopy(item),
                    'limitation': 'Vue générée. Lire portée et exceptions ; revalider la série et la règle métier avant réutilisation.'}
            outputs[folder / (identifier + '.json')] = card
        outputs[folder / 'index.json'] = {
            'schema': 1, 'generated_by': GENERATOR, 'registry': source,
            'cards': [p.name for p in outputs], 'current': current,
            'historical': len(identifiers) - current, 'warnings': warnings,
        }
        # Preflight every target before writing any file; preserve personal notes.
        for path in outputs:
            within(root, str(path.relative_to(root)))
            if path.is_symlink():
                raise ValueError('fiche symbolique à conserver : ' + str(path))
            if path.exists() and read_json(path).get('generated_by') != GENERATOR:
                raise ValueError('fiche non générée à conserver : ' + str(path))
        for path, content in outputs.items():
            if not path.exists() or read_json(path) != content:
                atomic(path, content)
    return {'directory': str(folder.relative_to(root)), 'current': current,
            'historical': len(identifiers) - current, 'warnings': warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(export(args.project), ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()
