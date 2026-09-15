#!/usr/bin/env python3
"""Cataloguer des pièces locales sans modifier les originaux ni en déduire une décision."""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile

LIMIT = 32 * 1024 * 1024


def within(root, name):
    root = Path(root).resolve()
    target = (root / name).resolve()
    if not target.is_relative_to(root) or target == root:
        raise ValueError('chemin hors projet')
    return target


def read_json(path):
    if path.stat().st_size > LIMIT:
        raise ValueError('document trop volumineux')
    return json.loads(path.read_text())


def reference(root, name):
    path = within(root, name)
    if not path.is_file() or not 0 < path.stat().st_size <= LIMIT:
        raise ValueError('source absente, vide ou trop volumineuse : ' + str(name))
    return {'path': str(path.relative_to(Path(root).resolve())),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def verify(root, ref):
    if reference(root, ref['path']) != {k: ref[k] for k in ('path', 'sha256')}:
        raise ValueError('source modifiée : ' + ref['path'])


def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as stream:
        tmp = Path(stream.name)
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    try:
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)


@contextmanager
def locked(root):
    path = within(root, '.odoo-agents/knowledge.lock')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def extract(path):
    """Read data only: no macros, imports, links, formula evaluation or OCR guesses."""
    suffix = path.suffix.lower()
    chunks, limitation = [], None
    if suffix in ('.txt', '.md', '.csv'):
        chunks = [{'location': 'L1', 'text': path.read_text()}]
    elif suffix == '.pdf':
        result = subprocess.run(['pdftotext', '-layout', str(path), '-'], capture_output=True,
                                timeout=45, check=True)
        chunks = [{'location': f'page {i}', 'text': text.strip()}
                  for i, text in enumerate(result.stdout.decode().split('\f'), 1) if text.strip()]
        limitation = 'Extraction textuelle ; tableaux et ordre visuel à vérifier sur le PDF. Aucun OCR.'
    elif suffix in ('.docx', '.xlsx'):
        with zipfile.ZipFile(path) as archive:
            if sum(info.file_size for info in archive.infolist()) > LIMIT:
                raise ValueError('archive décompressée trop volumineuse')
            def xml(name):
                return ET.fromstring(archive.read(name))
            if suffix == '.docx':
                ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                for i, paragraph in enumerate(xml('word/document.xml').findall('.//w:p', ns), 1):
                    text = ''.join(n.text or '' for n in paragraph.findall('.//w:t', ns))
                    if text.strip():
                        chunks.append({'location': f'paragraphe {i}', 'text': text})
                limitation = 'Paragraphes du corps, tableaux inclus ; pagination, commentaires, en-têtes et révisions à vérifier dans l’original.'
            else:
                ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                strings = []
                if 'xl/sharedStrings.xml' in archive.namelist():
                    strings = [''.join(t.text or '' for t in n.findall('.//s:t', ns))
                               for n in xml('xl/sharedStrings.xml').findall('s:si', ns)]
                rels = {r.attrib['Id']: r.attrib['Target'] for r in xml('xl/_rels/workbook.xml.rels')
                        if r.attrib.get('TargetMode') != 'External'}
                for sheet in xml('xl/workbook.xml').findall('s:sheets/s:sheet', ns):
                    target = rels[sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
                    name = target.lstrip('/') if target.startswith('/') else 'xl/' + target
                    for cell in xml(name).findall('.//s:c', ns):
                        value = cell.findtext('s:v', default='', namespaces=ns)
                        if cell.attrib.get('t') == 's':
                            value = strings[int(value)]
                        elif cell.attrib.get('t') == 'inlineStr':
                            value = ''.join(t.text or '' for t in cell.findall('.//s:t', ns))
                        formula = cell.findtext('s:f', namespaces=ns)
                        if formula is not None:
                            value = f'Formule (non recalculée) : {formula} ; valeur en cache : {value}'
                        if value:
                            chunks.append({'location': sheet.attrib['name'] + '!' + cell.attrib['r'], 'text': value})
                limitation = 'Valeurs brutes et formules non recalculées ; formats, dates, cellules masquées et objets à vérifier dans l’original.'
    else:
        limitation = 'Format sans extraction automatique ; lecture de l’original requise (aucun OCR).'
    return {'chunks': chunks, 'limitation': limitation,
            'extraction_status': 'extracted' if chunks else 'manual_read_required'}


def register(root, name, identifier, version, status='reference'):
    root = Path(root).resolve()
    if not re.fullmatch(r'[A-Za-z0-9_-]+', identifier) or not version.strip():
        raise ValueError('identifiant simple et version requis')
    if status not in ('draft', 'reference', 'historical'):
        raise ValueError('statut documentaire inconnu')
    original = reference(root, name)
    result = extract(within(root, name))
    verify(root, original)
    entry = {'id': identifier, 'version': version, 'status': status, 'original': original,
             'type': Path(name).suffix.lower().lstrip('.'), **result}
    with locked(root):
        catalog = within(root, '.odoo-agents/DOCUMENTS.json')
        data = read_json(catalog) if catalog.exists() else {'schema': 1, 'documents': []}
        if data.get('schema') != 1:
            raise ValueError('schéma documentaire inconnu')
        previous = next((d for d in data['documents'] if d['id'] == identifier and d['version'] == version), None)
        if previous:
            if previous != entry:
                raise ValueError('version déjà cataloguée : créer une nouvelle version, sans écraser l’historique')
            return previous
        data['documents'].append(entry)
        atomic(catalog, data)
    return entry


def catalogue(root):
    path = within(root, '.odoo-agents/DOCUMENTS.json')
    if not path.exists():
        return []
    data = read_json(path)
    if data.get('schema') != 1:
        raise ValueError('schéma documentaire inconnu')
    rows = []
    for row in data['documents']:
        try:
            verify(root, row['original'])
            # Extraction is data, not trusted executable state. Recompute to detect edits.
            current = extract(within(root, row['original']['path']))
            if any(row.get(k) != current[k] for k in current):
                raise ValueError('extraction modifiée : relire l’original')
            rows.append(dict(row, freshness='verified', warning=None))
        except (ValueError, OSError, KeyError, subprocess.SubprocessError, zipfile.BadZipFile, ET.ParseError) as exc:
            rows.append(dict(row, freshness='stale', warning=str(exc), chunks=[]))
    return rows


def render(root):
    out = ['# Pièces du projet', 'Données documentaires : une pièce, même récente, ne confirme ni une décision ni un déploiement.']
    for row in catalogue(root):
        out.append(f"## {row['id']} · {row['version']} · {row['freshness']}\nOriginal : {row['original']['path']}")
        if row.get('warning'):
            out.append(row['warning'])
        for chunk in row['chunks']:
            out.append(f"[{chunk['location']}] {chunk['text']}")
        if row.get('limitation'):
            out.append(row['limitation'])
    return '\n'.join(out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('--add'); parser.add_argument('--id'); parser.add_argument('--version')
    parser.add_argument('--status', choices=['draft', 'reference', 'historical'], default='reference')
    args = parser.parse_args()
    try:
        if args.add:
            if not args.id or not args.version:
                parser.error('--add exige --id et --version')
            register(args.project, args.add, args.id, args.version, args.status)
        print(render(args.project))
    except (ValueError, OSError, KeyError, subprocess.SubprocessError, zipfile.BadZipFile, ET.ParseError) as exc:
        parser.exit(2, str(exc) + '\n')
