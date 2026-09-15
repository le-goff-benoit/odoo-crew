#!/usr/bin/env python3
"""Mémoire vivante de release : contributions immuables, réception et passation vérifiables."""
import argparse
import hashlib
import json
from pathlib import Path
import re

from odoo_documents import atomic, catalogue, locked, read_json, reference, verify, within


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def release_path(root, release):
    if not isinstance(release, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+', release):
        raise ValueError('identifiant de release invalide')
    path = within(root, 'changelog/' + release)
    if not (path / 'README.md').is_file():
        raise ValueError('release absente')
    return path


def validate(root, release, row):
    release_path(root, release)
    if row.get('schema') != 1 or not re.fullmatch(r'[A-Za-z0-9_-]+', row.get('id', '')):
        raise ValueError('contribution schema 1 avec identifiant stable requise')
    if row.get('kind') not in ('discovery', 'decision', 'question', 'implementation', 'deployment', 'deferred'):
        raise ValueError('nature de contribution inconnue')
    if row.get('state') not in ('proposed', 'accepted') or not row.get('statement') or not row.get('author'):
        raise ValueError('auteur, contenu et état explicites requis')
    if not row.get('sources') or not isinstance(row.get('scope'), list):
        raise ValueError('sources et périmètre explicites requis (vide = partagé)')
    for ref in row['sources']:
        verify(root, ref)
    if row['state'] == 'accepted':
        if not row.get('reviewed_by') or not row.get('review'):
            raise ValueError('acceptation sans relecture sourcée')
        verify(root, row['review'])
        if row['kind'] == 'decision' and (release_path(root, release) / 'plan.json').exists():
            import odoo_plan
            plan, _ = odoo_plan.read(release_path(root, release))
            affected = row.get('affects_tasks')
            if (not isinstance(affected, list) or not row.get('impact_reason')
                    or not set(affected) <= {t['id'] for t in plan['tasks']}):
                raise ValueError('décision : affects_tasks et impact_reason requis pour les tâches du plan')
    if row.get('supersedes'):
        if not re.fullmatch(r'[A-Za-z0-9_-]+', row['supersedes']) or row['state'] != 'accepted' or row['supersedes'] == row['id']:
            raise ValueError('remplacement non accepté ou cyclique')
        previous = within(root, f'changelog/{release}/knowledge/{row["supersedes"]}.json')
        if not previous.is_file():
            raise ValueError('contribution remplacée absente')
    if row['kind'] == 'implementation' and row['state'] == 'accepted':
        import odoo_plan
        plan, project = odoo_plan.read(release_path(root, release))
        task = next((t for t in plan['tasks'] if t['id'] == row.get('task')), None)
        if not task or odoo_plan.statuses(plan, project)[task['id']][0] != 'validated':
            raise ValueError('tâche non réceptionnée, différée ou preuve périmée')
        if odoo_plan.result_hash(task['receipt']) != row.get('receipt_sha256'):
            raise ValueError('réception de tâche remplacée')
    if row['kind'] == 'deployment' and row['state'] == 'accepted':
        import odoo_delivery_guard
        delivery = row.get('delivery', {})
        for key in ('contract', 'build', 'observation'):
            verify(root, delivery[key])
        contract = read_json(within(root, delivery['contract']['path']))
        if Path(contract['repository']).resolve() != Path(root).resolve():
            raise ValueError('contrat de livraison d’un autre projet')
        def check_nested(value):
            if isinstance(value, dict):
                if 'path' in value and 'sha256' in value:
                    path = within(root, value['path'])
                    verify(root, {**value, 'path': str(path.relative_to(Path(root).resolve()))})
                    if path.suffix == '.json':
                        if str(path) in visited:
                            return
                        visited.add(str(path))
                        check_nested(read_json(path))
                for item in value.values():
                    check_nested(item)
            elif isinstance(value, list):
                for item in value:
                    check_nested(item)
        visited = set()
        check_nested(delivery)
        refs = [{**delivery[key], 'path': str(within(root, delivery[key]['path']))}
                for key in ('build', 'observation')]
        result = odoo_delivery_guard.evaluate(contract, *refs)
        if result['status'] != 'deployed_verified':
            raise ValueError('déploiement non vérifié')


def publish(root, release, row):
    root = Path(root).resolve()
    with locked(root):
        validate(root, release, row)
        target = within(root, f'changelog/{release}/knowledge/{row["id"]}.json')
        if target.exists():
            if read_json(target) != row:
                raise ValueError('contribution immuable : publier un nouvel identifiant et un remplacement explicite')
            return target
        # One accepted successor per entry: competing reviews must be reconciled.
        for path in target.parent.glob('*.json'):
            other = read_json(path)
            if row.get('supersedes') and other.get('supersedes') == row['supersedes']:
                raise ValueError('remplacement concurrent : réconcilier les contributions')
        atomic(target, row)
        return target


def contributions(root, release=None):
    root = Path(root).resolve()
    folders = [release_path(root, release)] if release else sorted((root / 'changelog').glob('*'))
    rows = []
    for folder in folders:
        for path in sorted(folder.glob('knowledge/*.json')):
            raw = {}
            try:
                within(root, str(path.relative_to(root)))
                row = read_json(path)
                raw = row
                if row.get('id') != path.stem:
                    raise ValueError('identifiant différent du nom de contribution')
                validate(root, folder.name, row)
                row = dict(row, freshness='verified', warning=None)
            except (ValueError, OSError, KeyError, TypeError) as exc:
                row = {'id': path.stem, 'statement': 'Contribution à relire', 'freshness': 'stale',
                       'warning': str(exc), 'kind': 'unknown', 'state': 'unknown', 'sources': [], 'scope': []}
                if isinstance(raw, dict) and raw.get('supersedes'):
                    row['supersedes'] = raw['supersedes']
            rows.append(dict(row, release=folder.name, path=str(path.relative_to(root))))
    # A stale successor does not silently resurrect an obsolete rule.
    replaced = {(r['release'], r['supersedes']) for r in rows if r.get('supersedes')}
    for row in rows:
        row['current'] = (row['release'], row['id']) not in replaced
    return rows


def snapshot(root, release=None):
    """Read-only live view: source validity is recalculated, not a cached green flag."""
    root = Path(root).resolve()
    warnings, decisions, questions = [], [], []
    path = within(root, '.odoo-agents/DECISIONS.json')
    if path.exists():
        try:
            import odoo_memory
            data = read_json(path)
            odoo_memory.validate(data, root)
            decisions = data['decisions']
            questions = data.get('questions', [])
        except (ValueError, OSError, KeyError, TypeError) as exc:
            warnings.append('Décisions non vérifiées : ' + str(exc))
    try:
        documents = catalogue(root)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        documents = []; warnings.append('Catalogue non vérifié : ' + str(exc))
    rows = contributions(root, release)
    # Existing receipts already contain reviewed memory. Expose them immediately,
    # including during releases not yet migrated to structured contributions.
    receipts = []
    folders = [release_path(root, release)] if release else sorted((root / 'changelog').glob('*'))
    for folder in folders:
        if not folder.resolve().is_relative_to(root):
            warnings.append('Release hors projet ignorée : ' + folder.name)
            continue
        if not (folder / 'plan.json').is_file():
            continue
        try:
            import odoo_plan
            plan, project = odoo_plan.read(folder)
            states = odoo_plan.statuses(plan, project)
            for task in plan['tasks']:
                if not task.get('receipt'):
                    continue
                if not task['receipt'].get('memory'):
                    warnings.append(f"{folder.name} · {task['id']} : fragment mémoire absent de la réception")
                    continue
                ref = task['receipt']['memory']
                valid = states[task['id']][0] == 'validated'
                receipts.append({'task': task['id'], 'release': folder.name, 'source': ref,
                                 'state': states[task['id']][0], 'warning': states[task['id']][1],
                                 'text': within(root, ref['path']).read_text() if valid else '',
                                 'result_sha256': odoo_plan.result_hash(task['receipt'])})
        except (ValueError, OSError, KeyError, TypeError) as exc:
            warnings.append(folder.name + ' : réception non vérifiée : ' + str(exc))
    source_index = None
    index_path = within(root, '.odoo-agents/SOURCE_INDEX.json')
    if index_path.exists():
        try:
            import odoo_series
            import odoo_source_index
            index = read_json(index_path)
            if index['series'] != odoo_series.resolve(root)['series']:
                raise ValueError('série de l’index différente du projet')
            for layer in index['layers']:
                target = Path(layer['root']).resolve()
                expected = root if layer['layer'] == 'custom' else odoo_series.SOURCES_ROOT / (index['series'] + ('-enterprise' if layer['layer'] == 'enterprise' else ''))
                if target != expected.resolve():
                    raise ValueError('racine de sources à vérifier dans la bibliothèque déclarée')
            odoo_source_index.verify(index)
            source_index = {'series': index['series'], 'freshness': 'verified',
                            'layers': [{k: layer[k] for k in ('layer', 'revision', 'modules', 'missing', 'warnings')} | {'symbols': len(layer['symbols'])} for layer in index['layers']],
                            'limitation': index['layers'][0]['limitation']}
        except (ValueError, OSError, KeyError, TypeError) as exc:
            warnings.append('Index de sources non vérifié : ' + str(exc))
    return {'schema': 1, 'release': release, 'decisions': decisions, 'questions': questions, 'documents': documents, 'source_index': source_index,
            'contributions': rows, 'receipts': receipts, 'warnings': warnings,
            'limitation': 'Sources et preuves vérifiées ; fidélité métier à relire. Une réception locale ne prouve pas un déploiement.'}


def brief(root, release, task=None, role='orchestrator'):
    data = snapshot(root, release)
    out = [f'# Mémoire partagée · {release}', f'Tâche : {task or "release"} · rôle : {role}', data['limitation']]
    out += data['warnings']
    for row in data['decisions']:
        if row['status'] != 'superseded':
            out.append(f"- Décision {row['id']} [{row['status']}] : {row['statement']} — " + ', '.join(s['path'] for s in row['sources']))
            if row.get('scope'):
                out.append('  Périmètre : ' + ', '.join(row['scope']))
            if row.get('exceptions'):
                out.append('  Exceptions : ' + '; '.join(row['exceptions']))
            out.append('  Réalisation déclarée : ' + row['implementation']['status'])
    for row in data['questions']:
        if row['status'] == 'open':
            out.append(f"- Question {row['id']} [ouverte] : {row['question']} — {row['source']['path']}")
    for row in data['contributions']:
        if row['current']:
            out.append(f"- {row['id']} [{row['kind']}/{row['state']}/{row['freshness']}] {row['statement']} — {row['path']}")
            out += [f"  Source : {s['path']}" for s in row['sources']]
            if row.get('warning'):
                out.append('  À relire : ' + row['warning'])
    for row in data['receipts']:
        out.append(f"## Acquis {row['task']} [{row['state']}] · {row['source']['path']}\n{row['text'] or row['warning']}")
    out.append('## Pièces à consulter (originaux et repères dans DOCUMENTS.json)')
    for row in data['documents']:
        out.append(f"- {row['id']} {row['version']} [{row['status']}/{row['freshness']}] : {row['original']['path']}")
    text = '\n'.join(out) + '\n'
    return {'schema': 1, 'project': str(Path(root).resolve()), 'release': release,
            'task': task, 'role': role, 'knowledge_sha256': digest(data), 'text': text}


def verify_brief(root, record):
    current = brief(root, record['release'], record.get('task'), record.get('role'))
    if record != current:
        raise ValueError('mémoire partagée enrichie ou sources changées : relire avant de poursuivre')
    data = snapshot(root, record['release'])
    if (data['warnings'] or any(r['freshness'] != 'verified' for r in data['contributions'] if r['current'])
            or any(r['freshness'] != 'verified' for r in data['documents'])):
        raise ValueError('mémoire ou pièces non vérifiées : réconcilier les sources avant réception')


def impact_sources(root, release, task):
    """Explicit decision links only; unknown semantic dependencies stay a review task."""
    result = {}
    for path in sorted(release_path(root, release).glob('knowledge/*.json')):
        path = within(root, str(path.relative_to(Path(root))))
        row = read_json(path)
        if row.get('kind') == 'decision' and row.get('state') == 'accepted' and task in row.get('affects_tasks', []):
            for ref in row['sources'] + [row['review']]:
                verify(root, ref)
            result[row['id']] = reference(root, str(path.relative_to(Path(root))))['sha256']
    return result


def consolidate(root, release):
    folder = release_path(root, release)
    with locked(root):
        if (folder / 'closure.json').exists():
            raise ValueError('release scellée : conserver sa consolidation ; ajouter les observations séparément')
        data = snapshot(root, release)
        if (data['warnings'] or any(r['freshness'] != 'verified' for r in data['contributions'] if r['current'])
                or any(r['freshness'] != 'verified' for r in data['documents'])):
            raise ValueError('mémoire à réconcilier avant consolidation')
        result = {'schema': 1, 'release': release, 'knowledge_sha256': digest(data), 'snapshot': data}
        atomic(folder / 'knowledge-consolidation.json', result)
        return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['show', 'publish', 'brief', 'verify', 'consolidate'])
    parser.add_argument('project', type=Path); parser.add_argument('--release')
    parser.add_argument('--task'); parser.add_argument('--role', default='orchestrator')
    parser.add_argument('--file', type=Path); parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.action in ('publish', 'verify') and not args.file:
        parser.error('--file requis pour ' + args.action)
    if args.action in ('publish', 'brief', 'consolidate') and not args.release:
        parser.error('--release attend l’identifiant court de la release')
    try:
        if args.action == 'publish':
            print(publish(args.project, args.release, read_json(args.file)))
        elif args.action == 'verify':
            verify_brief(args.project, read_json(args.file)); print('Mémoire partagée inchangée.')
        elif args.action == 'brief':
            result = brief(args.project, args.release, args.task, args.role)
            if args.output:
                atomic(args.output, result)
            print(result['text'])
        elif args.action == 'consolidate':
            print(json.dumps(consolidate(args.project, args.release), ensure_ascii=False, indent=2))
        else:
            print(json.dumps(snapshot(args.project, args.release), ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, str(exc) + '\n')
