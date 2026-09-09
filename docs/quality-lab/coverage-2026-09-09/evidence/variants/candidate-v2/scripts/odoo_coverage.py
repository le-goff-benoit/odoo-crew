"""Couverture déclarative liée aux critères originaux ; pas un juge sémantique."""
import hashlib
import json
from pathlib import Path
import re


FORMAT = 'odoo-qa-coverage/1'
GATES = {'module_task_gate', 'module_high_gate', 'studio_task_gate'}


def digest(value):
    return hashlib.sha256(value).hexdigest()


def project_file(project, value):
    root = Path(project).resolve()
    path = (root / value).resolve()
    if not path.is_relative_to(root) or not path.is_file() or not path.stat().st_size:
        raise ValueError('fichier non vide attendu dans le projet : ' + str(value))
    return path


def contract(project, source):
    path = project_file(project, source)
    lines = path.read_text().splitlines()
    headings = []
    for index, line in enumerate(lines):
        match = re.fullmatch(r'(#{1,6})\s+(?:\d+[.)]?\s+)?Critères d[’\']acceptation\s*', line, re.I)
        if match:
            headings.append((index, len(match[1])))
    if len(headings) != 1:
        raise ValueError("une seule section « Critères d'acceptation » est requise")
    start, level = headings[0]
    blocks = []
    for line in lines[start + 1:]:
        heading = re.match(r'^(#{1,6})\s+', line)
        if heading and len(heading[1]) <= level:
            break
        item = re.fullmatch(r'- \[[ xX]\] (.+)', line)
        if item:
            blocks.append([item[1]])
        elif not line.strip():
            continue
        elif blocks and line.startswith('    ') and not line.lstrip().startswith(('-', '*', '#', '```')):
            blocks[-1].append(line)
        else:
            raise ValueError('critères non interprétables : utiliser des cases - [ ] et des continuations indentées')
    if not blocks:
        raise ValueError('aucun critère : aucune couverture implicite')
    criteria = []
    for index, block in enumerate(blocks, 1):
        text = '\n'.join(block)
        explicit = re.match(r'\*\*([A-Za-z][A-Za-z0-9_-]*)\*\*\s*[—–:-]', text)
        criteria.append({'id': explicit[1] if explicit else f'C{index:02d}', 'text': text})
    if len({row['id'] for row in criteria}) != len(criteria):
        raise ValueError('identifiants de critères dupliqués')
    result = {'source': str(path.relative_to(Path(project).resolve())),
              'source_sha256': digest(path.read_bytes()), 'criteria': criteria}
    result['sha256'] = digest(json.dumps(result, sort_keys=True, ensure_ascii=False).encode())
    return result


def draft(pinned):
    return {'format': FORMAT, 'contract_sha256': pinned['sha256'],
            'criteria': [dict(row, status='missing', evidence=[], note='') for row in pinned['criteria']]}


def verify(proof, pinned, project):
    if contract(project, pinned['source']) != pinned:
        raise ValueError('spécification modifiée depuis la liaison du contrat')
    if proof.get('format') != FORMAT or proof.get('contract_sha256') != pinned['sha256']:
        raise ValueError('couverture absente ou liée à un autre contrat')
    rows = proof.get('criteria')
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError('liste de couverture invalide')
    if [{'id': row.get('id'), 'text': row.get('text')} for row in rows] != pinned['criteria']:
        raise ValueError('critère omis, ajouté, déplacé ou reformulé')
    missing = [row['id'] for row in rows if row.get('status') != 'covered']
    if missing:
        raise ValueError('critères non couverts : ' + ', '.join(missing))
    for row in rows:
        refs = row.get('evidence')
        if not isinstance(refs, list) or not refs:
            raise ValueError(row['id'] + ' : preuve absente')
        for ref in refs:
            if not isinstance(ref, dict) or set(ref) != {'path', 'sha256'}:
                raise ValueError(row['id'] + ' : preuve attendue sous forme path/sha256')
            path = project_file(project, ref['path'])
            if digest(path.read_bytes()) != ref['sha256']:
                raise ValueError(row['id'] + ' : preuve modifiée')
            try:
                data = json.loads(path.read_bytes())
            except ValueError:
                data = None  # Un journal texte brut reste une preuve déclarative.
            if isinstance(data, dict) and data.get('format') == 'odoo-evidence/1':
                from odoo_evidence import verify as verify_execution
                verify_execution(data, project)
