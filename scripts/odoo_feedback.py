#!/usr/bin/env python3
"""Collecter les retours sourcés sans appel modèle ni adoption automatique de règles."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

from odoo_documents import atomic, locked, read_json, reference, within

CATEGORIES = ('human_correction', 'business_defect', 'contract_change', 'environment',
              'stale_evidence', 'documentation', 'provider_incident', 'escaped_defect')


def record(root, source, text, kind, release=None):
    """Capture an explicit sourced fact; classification is supplied, not guessed."""
    root = Path(root).resolve()
    if kind not in CATEGORIES or not text.strip():
        raise ValueError('catégorie et texte requis')
    if release:
        from odoo_knowledge import release_path
        release_path(root, release)
    ref = reference(root, source)
    excerpt = within(root, source).read_text()
    if reference(root, source) != ref:
        raise ValueError('source changée pendant la collecte')
    if text not in excerpt:
        raise ValueError('le retour doit citer exactement sa source')
    row = {'kind': kind, 'release': release, 'source': ref['path'], 'text': text,
           'excerpt': excerpt, 'source_sha256': ref['sha256']}
    identifier = digest(row)
    event = {'schema': 1, 'id': identifier, **row}
    with locked(root):
        path = within(root, '.odoo-agents/feedback/events/' + identifier + '.json')
        if path.exists() and read_json(path) != event:
            raise ValueError('observation immuable modifiée')
        atomic(path, event)
    return event


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def observations(root, release=None):
    from odoo_briefing import journal_entries, learned_lines
    journal = within(root, '.odoo-agents/JOURNAL.md')
    if journal.is_file():
        for entry in journal_entries(journal):
            for lesson in learned_lines([entry]):
                yield {'kind': 'lesson', 'release': None, 'source': '.odoo-agents/JOURNAL.md',
                       'text': lesson, 'excerpt': entry}
    for path in sorted(within(root, '.odoo-agents/flows').glob('*.json')):
        flow = read_json(within(root, str(path.relative_to(root))))
        flow_release = Path(flow.get('plan_task', {}).get('release', '')).name or None
        if release and flow_release not in (None, release):
            continue
        for event in flow.get('events', []):
            if event.get('outcome') in ('retry', 'blocked', 'exhausted'):
                yield {'kind': 'qa_retry', 'release': flow_release, 'source': str(path.relative_to(root)),
                       'text': event.get('note') or ('Reprise : ' + event.get('node', '?')),
                       'excerpt': event}
    folders = [within(root, 'changelog/' + release)] if release else sorted((root / 'changelog').glob('*'))
    for folder in folders:
        if not folder.is_dir():
            continue
        within(root, str(folder.relative_to(root)))
        plan_path = within(root, str(folder.relative_to(root) / 'plan.json'))
        if plan_path.is_file():
            plan = read_json(plan_path)
            for row in plan.get('history', []):
                if row.get('action') in ('reopen', 'defer', 'finish'):
                    yield {'kind': row['action'], 'release': folder.name, 'source': str(plan_path.relative_to(root)),
                           'text': row.get('reason') or ('Tâche réceptionnée : ' + row.get('task_id', '?')),
                           'excerpt': row}
        for name in ('closure.json', 'qa.md'):
            path = within(root, str(folder.relative_to(root) / name))
            if path.is_file() and path.stat().st_size:
                yield {'kind': 'closure' if name == 'closure.json' else 'qa', 'release': folder.name,
                       'source': str(path.relative_to(root)), 'text': 'Résultat à examiner : ' + name,
                       'excerpt': path.read_text()}
        for path in sorted(folder.glob('knowledge/*.json')):
            row = read_json(within(root, str(path.relative_to(root))))
            if row.get('kind') == 'deployment':
                yield {'kind': 'deployment', 'release': folder.name, 'source': str(path.relative_to(root)),
                       'text': row.get('statement', 'Observation de déploiement'), 'excerpt': row}


def collect(root, release=None):
    root = Path(root).resolve()
    if release:
        from odoo_knowledge import release_path
        release_path(root, release)
    # Materialize before writing: malformed inputs never create a partial report.
    rows = list(observations(root, release))
    with locked(root):
        for row in rows:
            identifier = digest(row)
            target = within(root, '.odoo-agents/feedback/events/' + identifier + '.json')
            event = {'schema': 1, 'id': identifier, **row}
            if target.exists():
                if read_json(target) != event:
                    raise ValueError('observation immuable modifiée : ' + identifier)
            else:
                atomic(target, event)
        pending = within(root, '.odoo-agents/feedback/pending/' + (release or 'project') + '.json')
        pending.unlink(missing_ok=True)
        result = snapshot(root, release)
        atomic(within(root, '.odoo-agents/feedback/reports/' + (release or 'project') + '.json'), result)
    return result


def snapshot(root, release=None):
    root = Path(root).resolve()
    rows, warnings = [], []
    folder = within(root, '.odoo-agents/feedback/events')
    triage = within(root, '.odoo-agents/feedback/triage.json')
    states = read_json(triage) if triage.exists() else {}
    for path in sorted(folder.glob('*.json')):
        try:
            event = read_json(within(root, str(path.relative_to(root))))
            payload = {k: v for k, v in event.items() if k not in ('id', 'schema')}
            if event.get('schema') != 1 or event.get('id') != path.stem or digest(payload) != path.stem:
                raise ValueError('empreinte d’observation invalide')
            if release and event['release'] not in (None, release):
                continue
            rows.append({**event, 'triage': states.get(event['id'], {'status': 'candidate'})})
        except (ValueError, OSError, KeyError, TypeError) as exc:
            warnings.append(path.name + ' : ' + str(exc))
    pending = within(root, '.odoo-agents/feedback/pending')
    for path in sorted(pending.glob('*.json')):
        warnings.append('Collecte à reprendre : ' + path.stem)
    # Content grouping is explicit; no semantic equivalence or global rule is inferred.
    groups = {}
    for row in rows:
        key = digest({'kind': row['kind'], 'text': row['text']})
        group = groups.setdefault(key, {'kind': row['kind'], 'text': row['text'], 'occurrences': [], 'pending': 0})
        group['occurrences'].append(row['id'])
        group['pending'] += row['triage']['status'] == 'candidate'
    return {'schema': 1, 'release': release, 'events': rows, 'groups': list(groups.values()),
            'pending': sum(r['triage']['status'] == 'candidate' for r in rows), 'warnings': warnings,
            'limitation': 'Observations historiques figées, à qualifier ; aucune règle adoptée automatiquement.'}


def triage(root, identifier, status, reviewer, reason):
    if status not in ('candidate', 'reviewed', 'dismissed') or not reviewer.strip() or not reason.strip():
        raise ValueError('statut, relecteur et motif explicites requis')
    root = Path(root).resolve()
    with locked(root):
        if identifier not in {e['id'] for e in snapshot(root)['events']}:
            raise ValueError('observation inconnue ou corrompue')
        path = within(root, '.odoo-agents/feedback/triage.json')
        data = read_json(path) if path.exists() else {}
        data[identifier] = {'status': status, 'reviewer': reviewer, 'reason': reason,
                            'at': datetime.now(timezone.utc).isoformat()}
        atomic(path, data)


def automatic(root, release=None):
    """Failure is visible and retryable; never redo successful product QA for it."""
    try:
        return collect(root, release)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        message = 'Feedback à reprendre via odoo_feedback.py collect : ' + str(exc)
        print(message, file=sys.stderr)
        try:
            atomic(within(root, '.odoo-agents/feedback/pending/' + (release or 'project') + '.json'),
                   {'error': str(exc), 'release': release})
        except (ValueError, OSError):
            pass
        return {'pending_collection': True, 'warning': message}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('collect', 'show', 'triage', 'record'))
    parser.add_argument('project', type=Path)
    parser.add_argument('--release')
    parser.add_argument('--id'); parser.add_argument('--status'); parser.add_argument('--reviewer'); parser.add_argument('--reason')
    parser.add_argument('--source'); parser.add_argument('--text'); parser.add_argument('--kind', choices=CATEGORIES)
    args = parser.parse_args()
    try:
        if args.action == 'record':
            if not args.source or not args.text:
                raise ValueError('--source et --text requis')
            record(args.project, args.source, args.text, args.kind, args.release)
        if args.action == 'triage':
            triage(args.project, args.id, args.status, args.reviewer or '', args.reason or '')
        result = collect(args.project, args.release) if args.action == 'collect' else snapshot(args.project, args.release)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()
