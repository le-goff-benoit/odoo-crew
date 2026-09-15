#!/usr/bin/env python3
"""Index statique Odoo par série/révision : aucune importation de code ni accès à une base."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from odoo_documents import atomic
import odoo_series


def revision(root):
    proc = subprocess.run(['git', '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null',
                           '-C', str(root), 'rev-parse', 'HEAD'], capture_output=True, text=True, timeout=10)
    return proc.stdout.strip() if proc.returncode == 0 else None


def module_path(root, module):
    if not module.isidentifier():
        raise ValueError('nom de module invalide')
    paths = [root / module, root / 'addons' / module, root / 'odoo/addons' / module]
    if root.name == module:
        paths.insert(0, root)
    for path in paths:
        if path.resolve().is_relative_to(root) and (path / '__manifest__.py').is_file():
            return path
    return None


def index(root, modules, series, layer):
    root = Path(root).resolve()
    files, symbols, missing, warnings = {}, [], [], []
    for module in sorted(set(modules)):
        folder = module_path(root, module)
        if folder is None:
            missing.append(module); continue
        for path in sorted(folder.rglob('*')):
            if not path.is_file() or path.suffix not in ('.py', '.xml'):
                continue
            if path.is_symlink() or not path.resolve().is_relative_to(root):
                raise ValueError('lien de source hors périmètre')
            name = str(path.relative_to(root))
            content = path.read_bytes()
            files[name] = hashlib.sha256(content).hexdigest()
            def add(kind, symbol, line=None, model=None):
                symbols.append({'module': module, 'kind': kind, 'name': symbol, 'model': model,
                                'path': name, 'line': line, 'sha256': files[name]})
            try:
                if path.suffix == '.py':
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if not isinstance(node, ast.ClassDef):
                            continue
                        models = []
                        for item in node.body:
                            if isinstance(item, ast.Assign) and any(isinstance(t, ast.Name) and t.id in ('_name', '_inherit') for t in item.targets):
                                try:
                                    value = ast.literal_eval(item.value)
                                    models += [value] if isinstance(value, str) else value if isinstance(value, list) else []
                                except (ValueError, TypeError):
                                    warnings.append(name + ': modèle dynamique non résolu')
                        model = ', '.join(str(m) for m in models) or None
                        if model:
                            add('model', model, node.lineno, model)
                        for item in node.body:
                            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                add('test' if item.name.startswith('test_') else 'method', item.name, item.lineno, model)
                            elif isinstance(item, ast.Assign) and isinstance(item.value, ast.Call):
                                call = item.value.func
                                if isinstance(call, ast.Attribute) and isinstance(call.value, ast.Name) and call.value.id == 'fields':
                                    for target in item.targets:
                                        if isinstance(target, ast.Name):
                                            add('field', target.id, item.lineno, model)
                else:
                    tree = ET.fromstring(content)
                    for node in tree.iter():
                        if node.tag in ('record', 'template') and node.get('id'):
                            add('view' if node.get('model') == 'ir.ui.view' or node.tag == 'template' else 'record',
                                module + '.' + node.get('id'), model=node.get('model'))
            except (SyntaxError, ET.ParseError, UnicodeError) as exc:
                warnings.append(name + ': ' + str(exc))
    identity = {'series': series, 'layer': layer, 'root': str(root), 'revision': revision(root), 'files': files}
    return {'schema': 1, **identity, 'modules': sorted(set(modules)), 'missing': missing, 'warnings': warnings,
            'fingerprint': hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest(),
            'symbols': symbols, 'limitation': 'Index AST/XML statique ; héritage dynamique, registre, Studio et modules installés non observés.'}


def build(project, modules, sources_root=None, cache=None):
    project = Path(project).resolve()
    resolved = odoo_series.resolve(project)
    series = resolved['series']
    if resolved['origin'] == 'défaut':
        raise ValueError('déclarer la série du projet avant indexation')
    base = Path(sources_root or odoo_series.SOURCES_ROOT).resolve()
    standard = base / series
    if not standard.is_dir():
        raise ValueError('sources exactes absentes : ' + series)
    result = {'schema': 1, 'series': series, 'layers': [index(standard, modules, series, 'community')]}
    enterprise = base / (series + '-enterprise')
    if enterprise.is_dir():
        result['layers'].append(index(enterprise, modules, series, 'enterprise'))
    custom = sorted(p.parent.name for p in project.glob('*/__manifest__.py'))
    if (project / '__manifest__.py').is_file():
        custom.append(project.name)
    result['layers'].append(index(project, custom, series, 'custom'))
    if cache:
        cache = Path(cache).resolve()
        if cache.is_relative_to(base):
            raise ValueError('cache interdit dans les sources Odoo')
        for layer in result['layers']:
            if layer['layer'] != 'custom':
                target = cache / (series + '-' + layer['fingerprint'] + '.json')
                if not target.exists():
                    atomic(target, layer)
    return result


def verify(record):
    for layer in record['layers']:
        fresh = index(layer['root'], layer['modules'], layer['series'], layer['layer'])
        if layer != fresh or layer['series'] != record['series']:
            raise ValueError('index périmé ou série différente : ' + layer['layer'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path); parser.add_argument('--modules', nargs='+', default=['base'])
    parser.add_argument('--sources-root', type=Path); parser.add_argument('--cache', type=Path)
    parser.add_argument('--output', type=Path); parser.add_argument('--verify', type=Path)
    args = parser.parse_args()
    try:
        if args.verify:
            verify(json.loads(args.verify.read_text())); print('Index inchangé.')
        else:
            result = build(args.project, args.modules, args.sources_root, args.cache)
            if args.output:
                if args.output.resolve().is_relative_to(Path(args.sources_root or odoo_series.SOURCES_ROOT).resolve()):
                    raise ValueError('écriture interdite dans les sources Odoo')
                atomic(args.output, result)
            print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(2, str(exc) + '\n')
