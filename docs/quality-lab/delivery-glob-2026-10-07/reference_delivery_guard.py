#!/usr/bin/env python3
"""Contrôler un commit livrable et des preuves de déploiement, sans rien déployer."""
import argparse
import ast
import fnmatch
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from odoo_evidence import verify as verify_evidence


def digest(data):
    return hashlib.sha256(data).hexdigest()


def same_value(left, right):
    return json.dumps(left, sort_keys=True) == json.dumps(right, sort_keys=True)


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.PIPE)


def tree(repo, revision):
    commit = git(repo, 'rev-parse', '--verify', '--end-of-options', revision + '^{commit}').decode().strip()
    entries = {}
    for row in git(repo, 'ls-tree', '-rz', commit).split(b'\0'):
        if not row:
            continue
        meta, name = row.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        path = name.decode()
        if kind == 'blob':
            entries[path] = {'mode': mode, 'data': git(repo, 'cat-file', 'blob', oid)}
        elif kind == 'commit':
            # Preserve gitlinks so the module check rejects them explicitly.
            entries[path] = {'mode': mode, 'data': b''}
    return commit, entries


def version(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d+(?:\.\d+)+', value):
        raise ValueError('version numérique complète attendue : ' + str(value))
    parts = tuple(int(x) for x in value.split('.'))
    return parts + (0,) * max(0, 8 - len(parts))


def fields(entries, prefix):
    found = {}
    for path, item in entries.items():
        if not path.startswith(prefix + '/') or not path.endswith('.py'):
            continue
        syntax = ast.parse(item['data'], filename=path)
        for cls in (n for n in ast.walk(syntax) if isinstance(n, ast.ClassDef)):
            for node in cls.body:
                if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                    continue
                call = node.value
                if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute):
                    continue
                if not isinstance(call.func.value, ast.Name) or call.func.value.id != 'fields':
                    continue
                # Keep even computed/non-stored declarations: conversion in either direction matters.
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target, ast.Name):
                        found[path + ':' + cls.name + '.' + target.id] = ast.dump(call)
    return found


def check_module(entries, prefix, errors):
    for path, item in entries.items():
        if not path.startswith(prefix + '/'):
            continue
        if item['mode'] not in ('100644', '100755'):
            errors.append('fichier non régulier : ' + path)
        if not path.endswith('.py'):
            continue
        syntax = ast.parse(item['data'], filename=path)
        for node in ast.walk(syntax):
            if not isinstance(node, ast.ImportFrom) or not node.level:
                continue
            parent = PurePosixPath(path).parent
            for _ in range(node.level - 1):
                parent = parent.parent
            bases = [str(parent / node.module.replace('.', '/'))] if node.module else [str(parent / n.name) for n in node.names if n.name != '*']
            for base in bases:
                if base + '.py' not in entries and base + '/__init__.py' not in entries:
                    errors.append('import local absent du commit : ' + path + ' → ' + base)
    manifest_path = prefix + '/__manifest__.py'
    if manifest_path not in entries:
        raise ValueError('manifest absent du commit : ' + manifest_path)
    manifest = ast.literal_eval(entries[manifest_path]['data'].decode())
    for key in ('data', 'demo'):
        for name in manifest.get(key, []):
            if str(PurePosixPath(prefix) / name) not in entries:
                errors.append('fichier déclaré absent : ' + prefix + '/' + name)
    for bundle in manifest.get('assets', {}).values():
        for directive in bundle:
            names = directive if isinstance(directive, (list, tuple)) else [directive]
            for name in names:
                if isinstance(name, str) and name.startswith(PurePosixPath(prefix).name + '/'):
                    pattern = str(PurePosixPath(prefix).parent / name)
                    if not any(fnmatch.fnmatch(p, pattern) for p in entries):
                        errors.append('asset déclaré absent : ' + pattern)
    return manifest


def prepare(repo, base, target, modules, build_command, build_environment, target_environment, effects):
    repo = Path(repo).resolve()
    if not build_command or not all(isinstance(x, str) and x for x in build_command):
        raise ValueError('commande de build argv explicite requise')
    if not build_environment or not target_environment or not isinstance(effects, dict) or not effects or not all(isinstance(x, str) and x for x in effects):
        raise ValueError('environnements et identifiants des effets à relire requis')
    base_commit, old = tree(repo, base)
    target_commit, new = tree(repo, target)
    errors, reports, sources = [], {}, {}
    for prefix in modules:
        if prefix.startswith('/') or '..' in PurePosixPath(prefix).parts:
            raise ValueError('chemin de module relatif requis')
        prefix = str(PurePosixPath(prefix))
        if prefix == '.':
            raise ValueError('répertoire de module relatif non vide requis')
        manifest = check_module(new, prefix, errors)
        before = ast.literal_eval(old[prefix + '/__manifest__.py']['data'].decode()) if prefix + '/__manifest__.py' in old else None
        start = before.get('version') if before else None
        end = manifest.get('version')
        end_v = version(end)
        start_v = version(start) if start else None
        if start_v and end_v < start_v:
            errors.append('version régressive : ' + prefix)
        old_fields, new_fields = fields(old, prefix), fields(new, prefix)
        changed = sorted(k for k in old_fields.keys() | new_fields.keys() if old_fields.get(k) != new_fields.get(k))
        if changed and start_v and end_v <= start_v:
            errors.append('changement potentiel de schéma sans hausse de version : ' + prefix)
        migrations, expected_migrations = [], []
        for path, item in new.items():
            if not path.startswith(prefix + '/'):
                continue
            sources[path] = {'sha256': digest(item['data']), 'mode': int(item['mode'], 8) & 0o777}
            local = path[len(prefix) + 1:].split('/')
            if local[0] not in ('migrations', 'upgrades') or not path.endswith('.py'):
                continue
            changed_script = old.get(path) != item
            if changed_script:
                migrations.append(path)
            well_placed = len(local) == 3 and re.fullmatch(r'(pre|post|end)-.+\.py', local[-1])
            if not well_placed:
                if changed_script:
                    errors.append('migration nouvelle/modifiée mal placée : ' + path)
                continue
            mv = version(local[1])
            in_range = start_v is not None and start_v < mv <= end_v
            if changed_script and not in_range:
                errors.append('migration nouvelle/modifiée hors plage base < version <= cible : ' + path)
            if in_range:
                # Execution depends on installed/target versions, not the Git diff.
                expected_migrations.append(path)
            if changed_script or in_range:
                syntax = ast.parse(item['data'])
                if not any(isinstance(n, ast.FunctionDef) and n.name == 'migrate' for n in syntax.body):
                    errors.append('fonction migrate absente : ' + path)
        name = PurePosixPath(prefix).name
        if name in reports:
            raise ValueError('nom de module ambigu : ' + name)
        reports[name] = {'path': prefix, 'base_version': start, 'target_version': end, 'potential_schema_changes': changed, 'changed_migrations': migrations, 'expected_migrations': expected_migrations}
    if not reports:
        raise ValueError('au moins un module requis')
    return {'format': 'odoo-delivery/1', 'repository': str(repo), 'base_commit': base_commit, 'target_commit': target_commit,
            'modules': reports, 'sources': sources, 'build_command': build_command, 'build_environment': build_environment,
            'target_environment': target_environment, 'expected_effects': effects, 'errors': errors,
            'status': 'blocked' if errors else 'prepared', 'created_at': datetime.now(timezone.utc).isoformat()}


def load_source(reference):
    if not isinstance(reference, dict) or not reference.get('path') or not reference.get('sha256'):
        raise ValueError('attestation non sourcée : chemin et empreinte requis')
    raw = Path(reference['path']).read_bytes()
    if digest(raw) != reference['sha256']:
        raise ValueError('source de preuve modifiée')
    return json.loads(raw)


def evaluate(contract, build_reference, deployment_reference=None):
    if contract.get('format') != 'odoo-delivery/1':
        raise ValueError('format de contrat inconnu')
    # Recompute against immutable Git objects: do not trust edited summaries/errors.
    fresh = prepare(contract['repository'], contract['base_commit'], contract['target_commit'],
                    [v['path'] for v in contract['modules'].values()], contract['build_command'],
                    contract['build_environment'], contract['target_environment'], contract['expected_effects'])
    for key in ('modules', 'sources', 'errors'):
        if fresh[key] != contract[key]:
            raise ValueError('contrat incohérent avec le commit : ' + key)
    if fresh['errors']:
        raise ValueError('; '.join(fresh['errors']))
    proof = load_source(build_reference)
    verify_evidence(proof, expected_environment=contract['build_environment'])
    if proof.get('repository', {}).get('revision') != contract['target_commit']:
        raise ValueError('build sur un autre commit')
    if proof.get('command') != contract['build_command']:
        raise ValueError('commande de build différente du contrat')
    if any(proof['sources'].get(p, {}).get('sha256') != record['sha256'] or
           bool(proof['sources'].get(p, {}).get('mode', 0) & 0o111) != bool(record['mode'] & 0o111)
           for p, record in contract['sources'].items()) or any(
            p not in contract['sources'] and any(p.startswith(m['path'] + '/') for m in contract['modules'].values())
            for p in proof['sources']):
        raise ValueError('build ne couvre pas tous les fichiers du commit cible')
    result = {'format': 'odoo-delivery-result/1', 'status': 'ready_to_deliver', 'target_commit': contract['target_commit'],
              'target_environment': contract['target_environment'], 'build': build_reference}
    if deployment_reference is not None:
        observed = load_source(deployment_reference)
        if observed.get('format') != 'odoo-deployment-observation/1':
            raise ValueError('format d’observation inconnu')
        if observed.get('target_environment') != contract['target_environment'] or observed.get('commit') != contract['target_commit']:
            raise ValueError('environnement/commit installé différent de la cible')
        if observed.get('build_status') != 'success' or not observed.get('build_id'):
            raise ValueError('build distant échoué ou non identifié')
        stamp = datetime.fromisoformat(observed['observed_at'])
        if stamp.tzinfo is None or stamp < datetime.fromisoformat(contract['created_at']) or stamp > datetime.now(timezone.utc):
            raise ValueError('observation antérieure au contrat, future ou sans fuseau')
        before = load_source(observed.get('before'))
        if (before.get('format') != 'odoo-deployment-baseline/1' or
                before.get('target_environment') != contract['target_environment'] or
                before.get('commit') != contract['base_commit']):
            raise ValueError('état installé avant livraison différent de la base/cible convenue')
        before_stamp = datetime.fromisoformat(before['observed_at'])
        if (before_stamp.tzinfo is None or before_stamp > stamp or
                before_stamp < datetime.fromisoformat(contract['created_at'])):
            raise ValueError('capture avant livraison périmée ou chronologie incohérente')
        for name, module in contract['modules'].items():
            previous = before.get('installed_modules', {}).get(name, {})
            expected_state = 'installed' if module['base_version'] is not None else 'uninstalled'
            if previous.get('state') != expected_state or previous.get('version') != module['base_version']:
                raise ValueError('version installée avant livraison différente de la base : ' + name)
            installed = observed.get('installed_modules', {}).get(name, {})
            if installed.get('state') != 'installed' or installed.get('version') != module['target_version']:
                raise ValueError('version installée ancienne ou état incorrect : ' + name)
        for effect in contract['expected_effects']:
            item = observed.get('effects', {}).get(effect, {})
            if item.get('passed') is not True or not item.get('read_command') or 'actual' not in item or not same_value(item['actual'], contract['expected_effects'][effect]):
                raise ValueError('effet non relu : ' + effect)
            # The read itself must have a separate hash-bound raw output, not just passed:true.
            read = load_source(item.get('source'))
            if read.get('target_environment') != contract['target_environment'] or not same_value(read.get('actual'), item['actual']) or read.get('commit') != contract['target_commit'] or read.get('effect') != effect:
                raise ValueError('source de lecture différente : ' + effect)
        for module in contract['modules'].values():
            for migration in module['expected_migrations']:
                migration_proof = load_source(observed.get('migrations', {}).get(migration))
                if (migration_proof.get('target_environment') != contract['target_environment'] or
                        migration_proof.get('commit') != contract['target_commit'] or
                        migration_proof.get('migration') != migration or migration_proof.get('executed') is not True):
                    raise ValueError('migration non prouvée sur la cible : ' + migration)
        result.update(status='deployed_verified', deployment=deployment_reference)
    return result


def write_new(path, data):
    with Path(path).open('x') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    prep = commands.add_parser('prepare')
    prep.add_argument('--repo', required=True)
    prep.add_argument('--base', required=True)
    prep.add_argument('--target', required=True)
    prep.add_argument('--module', action='append', required=True)
    prep.add_argument('--build-command-json', required=True)
    prep.add_argument('--build-environment', required=True)
    prep.add_argument('--target-environment', required=True)
    prep.add_argument('--effects-json', required=True, help='objet identifiant → valeur attendue de chaque lecture')
    prep.add_argument('--output', required=True)
    check = commands.add_parser('verify')
    check.add_argument('contract')
    check.add_argument('--build-proof', required=True)
    check.add_argument('--build-sha256', required=True)
    check.add_argument('--deployment')
    check.add_argument('--deployment-sha256')
    check.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        if args.action == 'prepare':
            result = prepare(args.repo, args.base, args.target, args.module, json.loads(args.build_command_json),
                             args.build_environment, args.target_environment, json.loads(args.effects_json))
        else:
            deployment = {'path': args.deployment, 'sha256': args.deployment_sha256} if args.deployment else None
            result = evaluate(json.loads(Path(args.contract).read_text()),
                              {'path': args.build_proof, 'sha256': args.build_sha256}, deployment)
        write_new(args.output, result)
        print(result['status'])
        return 1 if result['status'] == 'blocked' else 0
    except (ValueError, KeyError, OSError, SyntaxError, TypeError, subprocess.CalledProcessError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())
