#!/usr/bin/env python3
"""Réception documentaire coopérative : intégrité et citations, pas jugement métier."""
import argparse
import json
import tempfile
from pathlib import Path

from odoo_coverage import digest, project_file
from odoo_evidence import fingerprint

FORMAT = 'odoo-task-reception/1'
BUNDLE_FORMAT = 'odoo-task-reception-bundle/1'
TARGETS = {'.odoo-agents/PROJECT.md', '.odoo-agents/JOURNAL.md'}
AXES = {'request_contract': ('source', 'spec'),
        'contract_evidence': ('spec', 'evidence'),
        'source_memory': ('source', 'draft')}


def ref(root, value):
    path = project_file(root, value)
    return {'path': str(path.relative_to(root)), 'sha256': digest(path.read_bytes())}


def memory_path(root, value):
    # Les cibles canoniques ne doivent pas rediriger vers un autre document.
    path = root / value
    if value not in TARGETS or path.resolve() != path.absolute():
        raise ValueError('cible mémoire canonique requise : ' + str(value))
    if path.exists() and not path.is_file():
        raise ValueError('cible mémoire non régulière : ' + value)
    return path


def prepare(project, sources, spec, evidence, memories, scopes, owner):
    root = Path(project).resolve()
    if not owner.strip() or not sources or not evidence:
        raise ValueError('propriétaire, demande et preuves requis')
    groups = {'source': [ref(root, value) for value in sources],
              'spec': [ref(root, spec)],
              'evidence': [ref(root, value) for value in evidence]}
    rows = []
    for value in memories:
        target, separator, proposed = value.partition('=')
        if not separator:
            raise ValueError('mémoire attendue sous forme TARGET=DRAFT')
        path = memory_path(root, target)
        rows.append({'target': target, 'before_sha256': digest(path.read_bytes()) if path.exists() else None,
                     'draft': ref(root, proposed)})
    if len(rows) != 2 or {row['target'] for row in rows} != TARGETS:
        raise ValueError('PROJECT.md et JOURNAL.md requis une fois chacun')
    inputs = {item['path'] for group in groups.values() for item in group}
    drafts = [row['draft']['path'] for row in rows]
    if len(set(drafts)) != 2 or (set(drafts) & (inputs | TARGETS)) or inputs & TARGETS:
        raise ValueError('sources, drafts et cibles mémoire doivent être distincts')
    result = {'format': BUNDLE_FORMAT, 'project': str(root), 'owner': owner,
              'groups': groups, 'memory': rows, 'scopes': [str(value) for value in scopes]}
    result['code'] = fingerprint(root, result['scopes']) if scopes else {}
    if set(result['code']) & (inputs | set(drafts) | TARGETS):
        raise ValueError('périmètre de code distinct des documents et de la mémoire requis')
    return result


def verify_contract(bundle, contract):
    if contract and bundle['groups']['spec'] != [{'path': contract['source'], 'sha256': contract['source_sha256']}]:
        raise ValueError('spécification de réception différente du contrat QA lié')


def draft(bundle_sha256, reviewer, mode='independent'):
    return {'format': FORMAT, 'bundle_sha256': bundle_sha256,
            'reviewer': reviewer, 'mode': mode, 'verdict': 'blocked',
            'checks': {axis: {'status': 'fail', 'citations': [], 'explanation': ''} for axis in AXES}}


def check_ref(root, item, allow_empty=False):
    if allow_empty:
        path = (root / item['path']).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError('fichier attendu dans le projet : ' + item['path'])
    else:
        path = project_file(root, item['path'])
    if digest(path.read_bytes()) != item['sha256']:
        raise ValueError('fichier modifié depuis préparation : ' + item['path'])
    return path


def check_execution(root, path, seen=None):
    """Conserve la fraîcheur des preuves structurées imbriquées, même renommées."""
    seen = set() if seen is None else seen
    if path in seen:
        return
    seen.add(path)
    try:
        value = json.loads(path.read_bytes())
    except (ValueError, UnicodeError):
        return
    if not isinstance(value, dict):
        return
    if value.get('format') == 'odoo-evidence/1':
        from odoo_evidence import verify
        verify(value, root, require_success=False)
    elif value.get('format') == 'odoo-qa-coverage/1':
        for row in value['criteria']:
            for item in row['evidence']:
                check_execution(root, check_ref(root, item), seen)


def verify_bundle(project, pinned, published=False, memory_policy=None):
    root = Path(project).resolve()
    path = check_ref(root, pinned)
    bundle = json.loads(path.read_bytes())
    if bundle['format'] != BUNDLE_FORMAT or bundle['project'] != str(root):
        raise ValueError('dossier de réception incompatible')
    for group, items in bundle['groups'].items():
        for item in items:
            source = check_ref(root, item)
            if group == 'evidence':
                check_execution(root, source)
    for row in bundle['memory']:
        if row.get('base'):
            check_ref(root, row['base'], allow_empty=True)
    policy = memory_policy or ('published' if published else 'before')
    if policy not in {'before', 'published', 'publishable', 'ignore'}:
        raise ValueError('politique mémoire inconnue')
    for row in ([] if policy == 'ignore' else bundle['memory']):
        proposed = check_ref(root, row['draft'])
        target = memory_path(root, row['target'])
        current = digest(target.read_bytes()) if target.exists() else None
        expected = row['draft']['sha256'] if policy == 'published' else row['before_sha256']
        valid = current in {row['before_sha256'], row['draft']['sha256']} if policy == 'publishable' else current == expected
        if not valid:
            message = 'publication différente du draft approuvé' if published else 'mémoire modifiée depuis préparation'
            raise ValueError(message + ' : ' + row['target'])
    if (fingerprint(root, bundle['scopes']) if bundle['scopes'] else {}) != bundle['code']:
        raise ValueError('code changé depuis préparation')
    return bundle


def verify(review, pinned, project, require_pass=True, published=False, memory_policy=None):
    bundle = verify_bundle(project, pinned, published, memory_policy)
    if review.get('format') != FORMAT or review.get('bundle_sha256') != pinned['sha256']:
        raise ValueError('réception absente ou liée à un autre dossier')
    reviewer = review.get('reviewer')
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise ValueError('identité déclarée du relecteur requise')
    if review.get('mode') not in {'independent', 'self'} or review.get('verdict') not in {'pass', 'revise', 'blocked'}:
        raise ValueError('mode ou verdict de réception invalide')
    if require_pass and (review['mode'] != 'independent' or reviewer.strip() == bundle['owner'].strip()):
        raise ValueError('réception indépendante requise : auto-relecture refusée')
    checks = review.get('checks')
    if not isinstance(checks, dict) or set(checks) != set(AXES):
        raise ValueError('les trois axes de réception sont requis exactement')
    groups = {key: {item['path'] for item in refs} for key, refs in bundle['groups'].items()}
    groups['draft'] = {row['draft']['path'] for row in bundle['memory']}
    groups['base'] = {row['base']['path'] for row in bundle['memory'] if row.get('base')
                      and check_ref(Path(project).resolve(), row['base'], allow_empty=True).read_text().strip()}
    frozen = set().union(*groups.values())
    for axis, needed in AXES.items():
        check = checks[axis]
        if not isinstance(check, dict) or check.get('status') not in {'pass', 'fail'}:
            raise ValueError(axis + ' : statut requis')
        if not isinstance(check.get('explanation'), str) or not check['explanation'].strip():
            raise ValueError(axis + ' : explication requise')
        citations = check.get('citations')
        if not isinstance(citations, list):
            raise ValueError(axis + ' : citations requises')
        cited = set()
        for citation in citations:
            if not isinstance(citation, dict) or set(citation) != {'path', 'quote'}:
                raise ValueError(axis + ' : citation path/quote requise')
            source, quote = citation['path'], citation['quote']
            if source not in frozen or not isinstance(quote, str) or not quote.strip():
                raise ValueError(axis + ' : citation hors dossier ou vide')
            if quote not in project_file(project, source).read_text():
                raise ValueError(axis + ' : citation introuvable dans ' + source)
            cited.add(source)
        if axis == 'source_memory' and not groups['base'] <= cited:
            raise ValueError('source_memory : citer toutes les bases mémoire conservées')
        if any(not (cited & groups[group]) for group in needed):
            raise ValueError(axis + ' : citer les deux groupes confrontés')
        if require_pass and check['status'] != 'pass':
            raise ValueError(axis + ' : axe non conforme')
    if require_pass and review['verdict'] != 'pass':
        raise ValueError('réception non conforme')
    return bundle


def atomic_publish(path, content):
    """Remplacement atomique d'un fichier ; aucune transaction entre les deux cibles."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile('wb', dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        if path.exists():
            temporary.chmod(path.stat().st_mode & 0o777)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def publish(project, pinned, review):
    root = Path(project).resolve()
    bundle = verify(review, pinned, root, memory_policy='publishable')
    result = []
    for row in bundle['memory']:
        # Prévalidation globale répétée avant chaque remplacement : un tiers peut
        # néanmoins ignorer le protocole entre cette lecture et replace().
        verify(review, pinned, root, memory_policy='publishable')
        target = memory_path(root, row['target'])
        current = digest(target.read_bytes()) if target.exists() else None
        if current == row['draft']['sha256']:
            result.append({'target': row['target'], 'action': 'already_published'})
        else:
            atomic_publish(target, check_ref(root, row['draft']).read_bytes())
            result.append({'target': row['target'], 'action': 'published'})
    verify(review, pinned, root, published=True)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    command = sub.add_parser('draft', help='imprimer le JSON à remplir par le relecteur')
    command.add_argument('bundle', type=Path)
    command.add_argument('--reviewer', required=True)
    command.add_argument('--mode', choices=['independent', 'self'], default='independent')
    check = sub.add_parser('check-bases', help='vérifier les bases mémoire et la fraîcheur avant copie sous verrou mémoire')
    check.add_argument('bundle', type=Path)
    args = parser.parse_args(argv)
    try:
        raw = args.bundle.read_bytes()
        if args.command == 'draft':
            print(json.dumps(draft(digest(raw), args.reviewer, args.mode), ensure_ascii=False, indent=2))
        else:
            bundle = json.loads(raw)
            verify_bundle(bundle['project'], {'path': str(args.bundle.resolve()), 'sha256': digest(raw)})
            print('Bases mémoire inchangées et dossier frais ; conserver le verrou mémoire pendant la copie des drafts.')
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(2, str(exc) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
