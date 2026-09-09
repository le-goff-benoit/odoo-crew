#!/usr/bin/env python3
"""Contexte ciblé avec sources vérifiables ; jamais de troncature silencieuse d'une règle."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

import odoo_memory


def inventory(project):
    paths = [project / '.odoo-agents' / name for name in ('PROJECT.md', 'JOURNAL.md', 'DECISIONS.json')]
    paths += list((project / 'decisions').glob('*.md')) + list((project / 'changelog').glob('*/revue_fonctionnelle.md'))
    found = []
    for path in paths:
        if path.exists():
            if not path.resolve().is_relative_to(project) or not path.is_file():
                raise ValueError('source non régulière ou hors projet')
            found.append(str(path.relative_to(project)))
    return sorted(set(found))


def context(project, query='', budget=12000):
    project = Path(project).resolve()
    if budget < 1000:
        raise ValueError('budget minimum 1000 caractères')
    catalog_paths = inventory(project)
    candidates = []
    memory = project / '.odoo-agents/DECISIONS.json'
    if memory.exists():
        data = json.loads(memory.read_text()); rendered = odoo_memory.render(data, project)
        candidates.append((1000, memory, rendered))
    project_md = project / '.odoo-agents/PROJECT.md'
    if project_md.exists():
        candidates.append((900, project_md, project_md.read_text()))
    words = set(re.findall(r'\w{3,}', query.lower()))
    paths = list((project / 'changelog').glob('*/revue_fonctionnelle.md')) + list((project / 'decisions').glob('*.md'))
    journal = project / '.odoo-agents/JOURNAL.md'
    if journal.exists():
        paths.append(journal)
    for path in paths:
        text = path.read_text()
        score = len(words & set(re.findall(r'\w{3,}', text.lower())))
        if score or not words:
            candidates.append((score, path, text))
    candidates.sort(key=lambda x: (-x[0], str(x[1])))
    out = ['# Contexte ciblé', 'Les archives restent historiques ; vérifier les décisions courantes avant de les appliquer.']
    refs = []; used = len('\n'.join(out))
    for priority, path, text in candidates:
        if not path.resolve().is_relative_to(project):
            raise ValueError('source hors projet')
        name = str(path.relative_to(project))
        block = '\n## ' + name + '\n' + text.strip() + '\n'
        included = used + len(block) <= budget
        if included:
            out.append(block); used += len(block)
        refs.append({'path': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'included': included,
                     'priority': priority, 'reason': None if included else 'bloc entier à lire sur demande ; budget atteint'})
    omitted = [r['path'] for r in refs if not r['included']]
    if omitted:
        out += ['\nBlocs non inclus (aucune exception tronquée ; les lire si nécessaires) :', *['- ' + name for name in omitted]]
    result = {'schema': 1, 'project': str(project), 'query': query, 'budget_characters': budget,
              'text': '\n'.join(out) + '\n', 'sources': refs, 'catalog_paths': catalog_paths,
              'limitation': 'Sélection lexicale, sans garantie de rappel exhaustif. Sources non sélectionnées toujours consultables.'}
    result['context_sha256'] = hashlib.sha256(result['text'].encode()).hexdigest()
    return result


def verify_context(record, project):
    project = Path(project).resolve()
    if record.get('catalog_paths') != inventory(project):
        raise ValueError('catalogue de connaissances changé : nouvelle source ou suppression')
    if hashlib.sha256(record['text'].encode()).hexdigest() != record['context_sha256']:
        raise ValueError('texte du contexte changé')
    for item in record['sources']:
        path = (project / item['path']).resolve()
        if not path.is_relative_to(project) or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('contexte périmé : ' + item['path'])


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('project', type=Path)
    p.add_argument('--query', default=''); p.add_argument('--budget', type=int, default=12000)
    p.add_argument('--output', type=Path); p.add_argument('--verify', type=Path); a = p.parse_args()
    try:
        if a.verify:
            verify_context(json.loads(a.verify.read_text()), a.project); print('Contexte sourcé inchangé.')
        else:
            result = context(a.project, a.query, a.budget)
            if a.output:
                a.output.parent.mkdir(parents=True, exist_ok=True)
                a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
            print(result['text'])
    except (ValueError, OSError) as e:
        sys.exit(str(e))
