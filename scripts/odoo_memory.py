#!/usr/bin/env python3
"""Valider et restituer une mémoire de décisions sourcées, sans inférer d'arbitrage."""
import argparse
import hashlib
import json
from pathlib import Path


class MemoryError(ValueError):
    pass


def source(root, value):
    path = (root / value['path']).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file() or not path.stat().st_size:
        raise MemoryError('source absente, vide ou hors projet : ' + value['path'])
    if hashlib.sha256(path.read_bytes()).hexdigest() != value['sha256']:
        raise MemoryError('source modifiée : ' + value['path'])


def validate(data, root):
    if data.get('schema') != 1:
        raise MemoryError('schéma de mémoire inconnu')
    rows = data.get('decisions', [])
    ids = [row['id'] for row in rows]
    if len(ids) != len(set(ids)):
        raise MemoryError('identifiant de décision dupliqué')
    by_id = {row['id']: row for row in rows}
    for row in rows:
        if row['status'] not in ('proposed', 'confirmed', 'superseded') or not row.get('statement'):
            raise MemoryError('statut ou règle invalide : ' + row['id'])
        if not row.get('sources'):
            raise MemoryError('décision sans source : ' + row['id'])
        for item in row['sources']:
            source(root, item)
        if row['status'] != 'proposed' and not row.get('confirmed_by'):
            raise MemoryError('auteur de confirmation absent : ' + row['id'])
        realization = row.get('implementation', {})
        if realization.get('status') not in ('unknown', 'not_started', 'local_validated', 'deployed'):
            raise MemoryError('état de réalisation absent ou inconnu : ' + row['id'])
        if row['status'] == 'proposed' and realization['status'] not in ('unknown', 'not_started'):
            raise MemoryError('proposition présentée comme réalisée : ' + row['id'])
        if realization['status'] in ('local_validated', 'deployed'):
            if not realization.get('evidence'):
                raise MemoryError('réalisation sans preuve : ' + row['id'])
            source(root, realization['evidence'])
        if realization['status'] == 'deployed' and not realization.get('instance'):
            raise MemoryError('déploiement sans instance identifiée : ' + row['id'])
        seen, current = set(), row
        while current['status'] == 'superseded':
            identifier = current['id']
            if identifier in seen:
                raise MemoryError('cycle de remplacement')
            seen.add(identifier)
            successor = current.get('superseded_by')
            if successor not in by_id or by_id[successor]['status'] == 'proposed':
                raise MemoryError('remplacement sans décision confirmée : ' + identifier)
            current = by_id[successor]
    questions = data.get('questions', [])
    if len({q['id'] for q in questions}) != len(questions):
        raise MemoryError('identifiant de question dupliqué')
    for question in questions:
        if question.get('status') not in ('open', 'resolved') or not question.get('question'):
            raise MemoryError('question invalide')
        source(root, question['source'])
        if question['status'] == 'resolved' and question.get('decision_id') not in by_id:
            raise MemoryError('question résolue sans décision')
        if question['status'] == 'resolved' and by_id[question['decision_id']]['status'] == 'proposed':
            raise MemoryError('question résolue par une proposition')


def render(data, root, topic=None):
    validate(data, root)
    out = ['## Décisions courantes et questions ouvertes (DECISIONS.json)',
           'Validation structurelle et empreintes vérifiées ; fidélité métier à relire dans les sources.']
    visible = [r for r in data['decisions'] if r['status'] != 'superseded' and
               (not topic or topic in r.get('scope', []))]
    for row in visible:
        refs = ', '.join(s['path'] for s in row['sources'])
        out.append(f"- {row['id']} [{row['status']} ; réalisation={row['implementation']['status']}] {row['statement']} — sources : {refs}")
    for q in data.get('questions', []):
        if q['status'] == 'open':
            out.append(f"- {q['id']} [QUESTION OUVERTE] {q['question']} — source : {q['source']['path']}")
    replaced = [r['id'] + ' → ' + r['superseded_by'] for r in data['decisions'] if r['status'] == 'superseded']
    if replaced:
        out.append('Historique remplacé, non applicable : ' + ', '.join(replaced))
    return '\n'.join(out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('--topic')
    args = parser.parse_args()
    data = json.loads((args.project / '.odoo-agents/DECISIONS.json').read_text())
    try:
        print(render(data, args.project, args.topic))
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(2, f'Mémoire non validée : {exc}\n')
