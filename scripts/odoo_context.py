#!/usr/bin/env python3
"""Contexte ciblé avec sources vérifiables ; jamais de troncature silencieuse d'une règle."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata

import odoo_memory
import odoo_documents
import odoo_knowledge


def inventory(project):
    paths = [project / '.odoo-agents' / name for name in ('PROJECT.md', 'JOURNAL.md', 'DECISIONS.json', 'DOCUMENTS.json', 'SOURCE_INDEX.json')]
    paths += list((project / 'decisions').glob('*.md')) + list((project / 'changelog').glob('*/revue_fonctionnelle.md'))
    for pattern in ('*/demande.md', '*/intentions.json', '*/plan.json', '*/consolidation.md', '*/knowledge/*.json'):
        paths += list((project / 'changelog').glob(pattern))
    found = []
    for path in paths:
        if path.exists():
            if not path.resolve().is_relative_to(project) or not path.is_file():
                raise ValueError('source non régulière ou hors projet')
            found.append(str(path.relative_to(project)))
    return sorted(set(found))


def catalog_hashes(project, paths):
    return {name: hashlib.sha256((project / name).read_bytes()).hexdigest() for name in paths}


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def keywords(text):
    normalized = ''.join(c for c in unicodedata.normalize('NFKD', text.casefold()) if not unicodedata.combining(c))
    # Orthographic equivalence only, not semantic matching or rule arbitration.
    return {word[:-1] if len(word) > 3 and word.endswith('s') else word
            for word in re.findall(r'\w{3,}', normalized)}


def markdown_sections(text):
    """Group whole sections; never split paragraphs, lists, fences or subheadings."""
    lines = text.splitlines(keepends=True)
    headings = []
    fence = None
    for index, line in enumerate(lines):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if marker:
            run = marker.group(1)
            if fence is None:
                fence = run
            elif run[0] == fence[0] and len(run) >= len(fence):
                fence = None
            continue
        if fence:
            continue
        match = re.match(r'^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$', line)
        if match:
            headings.append((index, len(match.group(1)), match.group(2)))
    # One document title is context for its sections, not a selection boundary.
    effective = headings[1:] if headings and headings[0][0] == 0 and headings[0][1] == 1 and sum(h[1] == 1 for h in headings) == 1 else headings
    level = min((h[1] for h in effective), default=7)
    cuts = [(0, headings[0][2] if headings and headings[0][0] == 0 else 'Préambule')]
    for index, depth, title in effective:
        if depth != level:
            continue
        # An exception is inseparable from the preceding rule, even if written
        # with a sibling heading rather than a subordinate heading.
        normalized_title = re.sub(
            r'^(?:\d+(?:\.\d+)*|[IVXLCDM]+|[A-Za-z])(?:[.)\-:–—]|\s)+', '', title.strip('*_ '))
        normalized_title = normalized_title.lstrip('*_ ')
        if re.match(r'(?i)^(exceptions?|limites?|conditions?|attention|sauf|cas particuliers?)\b', normalized_title):
            continue
        if index == 0:
            cuts[0] = (0, title)
        else:
            cuts.append((index, title))
    result = []
    for position, (start, title) in enumerate(cuts):
        end = cuts[position + 1][0] if position + 1 < len(cuts) else len(lines)
        content = ''.join(lines[start:end])
        if content.strip():
            result.append({'title': title, 'start_line': start + 1, 'end_line': end,
                           'content': content, 'section_sha256': digest(content)})
    return result


LIMITATION = ('Sélection lexicale, rappel non exhaustif : synonymes et contradictions ne sont pas résolus. '
              'Une date, même plus récente, ne vaut pas arbitrage. Vérifier les décisions courantes ; '
              'les autres sources peuvent être historiques.')


def context(project, query='', budget=12000, release=None, task=None, role='orchestrator'):
    project = Path(project).resolve()
    if budget < 1000:
        raise ValueError('budget minimum 1000 caractères')
    catalog_paths = inventory(project)
    hashes = catalog_hashes(project, catalog_paths)
    words = keywords(query)
    sections = []
    shared = odoo_knowledge.brief(project, release, task, role) if release else None
    for name in catalog_paths:
        path = project / name
        mandatory = name == '.odoo-agents/DECISIONS.json'
        if mandatory:
            rendered = odoo_memory.render(json.loads(path.read_text()), project)
            parts = [{'title': 'Décisions courantes et questions ouvertes', 'content': rendered,
                      'start_line': None, 'end_line': None, 'section_sha256': digest(rendered)}]
        elif name == '.odoo-agents/DOCUMENTS.json':
            parts = markdown_sections(odoo_documents.render(project))
        elif name == '.odoo-agents/SOURCE_INDEX.json':
            import odoo_source_index
            index = json.loads(path.read_text())
            try:
                odoo_source_index.verify(index)
                content = '# Sources Odoo indexées\n' + json.dumps(index, ensure_ascii=False, indent=2)
            except (ValueError, OSError, KeyError) as exc:
                content = '# Index à régénérer\n' + str(exc)
            parts = markdown_sections(content)
        else:
            parts = markdown_sections(path.read_text())
        for part in parts:
            title_words = keywords(name + ' ' + part['title'])
            text_words = keywords(part['content'])
            relevance = 3 * len(words & title_words) + len(words & text_words)
            business = name == '.odoo-agents/PROJECT.md' and bool(re.search(
                r'(?i)métier|metier|compréhension|decisions?|décisions?|règles?|contraintes?|actées?', part['title']))
            eligible = mandatory or business or relevance > 0 or not words
            priority = 1000 if mandatory else 900 if business else 500 + min(relevance, 399) if relevance else 100
            sections.append(dict(part, path=name, sha256=hashes[name], mandatory=mandatory,
                                 priority=priority, eligible=eligible, included=mandatory,
                                 reason=None if mandatory else 'sans correspondance lexicale' if not eligible else 'budget atteint'))
    # Stable order is a display tie-break only; neither filename nor date asserts
    # that one conflicting statement supersedes another.
    ranked = sorted(range(len(sections)), key=lambda i: (-sections[i]['priority'], sections[i]['path'], sections[i]['start_line'] or 0))

    def render(insufficient=False):
        out = ['# Contexte ciblé', LIMITATION]
        if shared:
            out.append(shared['text'])
        if insufficient:
            out.append('BUDGET INSUFFISANT : décisions obligatoires et index conservés intégralement ; augmenter le budget avant de poursuivre.')
        for i in ranked:
            item = sections[i]
            if item['included']:
                location = 'rendu validé' if item['mandatory'] else f"L{item['start_line']}-L{item['end_line']}"
                out.append(f"\n## {item['path']} · {location}\n" + item['content'].strip())
        omitted = [item for item in sections if not item['included']]
        if omitted:
            out.append('\nIndex des sections non incluses — ouvrir les lignes indiquées ; détails et empreintes dans le JSON :')
            for name in catalog_paths:
                entries = [i for i in omitted if i['path'] == name]
                if entries:
                    ranges = ', '.join(f"L{i['start_line']}-L{i['end_line']}" for i in entries)
                    out.append(f'- {name} : {ranges}')
        return '\n'.join(out) + '\n'

    # Reserve the complete omission index too. It is deliberately never silently
    # truncated; even an unusually large index produces an explicit insufficiency.
    baseline = render()
    insufficient = len(baseline) > budget
    if not insufficient:
        for i in ranked:
            item = sections[i]
            if item['mandatory'] or not item['eligible']:
                continue
            item['included'] = True
            if len(render()) > budget:
                item['included'] = False
            else:
                item['reason'] = None
    text = render(insufficient)
    refs = []
    for name in catalog_paths:
        relevant = [i for i in sections if i['path'] == name and i['eligible']]
        if relevant:
            refs.append({'path': name, 'sha256': hashes[name], 'included': any(i['included'] for i in relevant),
                         'priority': max(i['priority'] for i in relevant),
                         'reason': None if all(i['included'] for i in relevant) else 'sections non incluses consultables dans l’index'})
    result = {'schema': 2, 'project': str(project), 'query': query, 'budget_characters': budget,
              'text': text, 'sources': refs, 'catalog_paths': catalog_paths, 'catalog_sha256': hashes,
              'sections': [{k: v for k, v in i.items() if k != 'content'} for i in sections],
              'budget_status': 'insufficient' if insufficient else 'within_budget',
              'emitted_characters': len(text), 'actual_characters': len(text),
              'minimum_characters': len(render(True)) if insufficient else len(baseline),
              'limitation': LIMITATION}
    result['context_sha256'] = digest(text)
    if release:
        result.update(schema=3, release=release, task=task, role=role, shared_memory=shared)
    return result


def verify_context(record, project):
    project = Path(project).resolve()
    if record.get('project') != str(project):
        raise ValueError('contexte d’un autre projet : régénérer dans ce checkout')
    if record.get('catalog_paths') != inventory(project):
        raise ValueError('catalogue de connaissances changé : nouvelle source ou suppression')
    if record.get('catalog_sha256') != catalog_hashes(project, record['catalog_paths']):
        raise ValueError('catalogue de connaissances changé : contenu potentiellement pertinent')
    if hashlib.sha256(record['text'].encode()).hexdigest() != record['context_sha256']:
        raise ValueError('texte du contexte changé')
    for item in record['sources']:
        path = (project / item['path']).resolve()
        if not path.is_relative_to(project) or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('contexte périmé : ' + item['path'])
    if record.get('schema') in (2, 3):
        if record.get('schema') == 3:
            odoo_knowledge.verify_brief(project, record['shared_memory'])
        current = context(project, record['query'], record['budget_characters'],
                          record.get('release'), record.get('task'), record.get('role', 'orchestrator'))
        for key in ('sections', 'sources', 'text', 'budget_status', 'emitted_characters', 'actual_characters', 'minimum_characters'):
            if record.get(key) != current[key]:
                raise ValueError('sélection ou provenance des sections changée : ' + key)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('project', type=Path)
    p.add_argument('--query', default=''); p.add_argument('--budget', type=int, default=12000)
    p.add_argument('--output', type=Path); p.add_argument('--verify', type=Path)
    p.add_argument('--release'); p.add_argument('--task'); p.add_argument('--role', default='orchestrator')
    a = p.parse_args()
    try:
        if a.verify:
            verify_context(json.loads(a.verify.read_text()), a.project); print('Contexte sourcé inchangé.')
        else:
            result = context(a.project, a.query, a.budget, a.release, a.task, a.role)
            if a.output:
                a.output.parent.mkdir(parents=True, exist_ok=True)
                a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
            print(result['text'], end='')
    except (ValueError, OSError) as e:
        sys.exit(str(e))
