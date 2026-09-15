#!/usr/bin/env python3
"""Exécuter un contrôle et lier son résultat au contenu réellement contrôlé."""
import argparse
import hashlib
import json
import os
import platform
import signal
from pathlib import Path
import subprocess
import time

from odoo_test_result import inspect_log


def fingerprint(root, scopes, *, allow_empty=False):
    root = Path(root).resolve()
    files = {}
    for scope in scopes:
        path = (root / scope).resolve()
        if not path.is_relative_to(root) or not path.exists():
            raise ValueError('périmètre absent ou hors projet : ' + scope)
        candidates = sorted(path.rglob('*')) if path.is_dir() else [path]
        for item in candidates:
            if '.git' in item.parts or '__pycache__' in item.parts or item.suffix == '.pyc' or item.is_dir():
                continue
            real = item.resolve()
            if not real.is_relative_to(root) or not real.is_file():
                raise ValueError('source hors projet ou non régulière : ' + str(item))
            files[str(item.relative_to(root))] = {'sha256': hashlib.sha256(item.read_bytes()).hexdigest(),
                                                 'mode': item.stat().st_mode & 0o777}
    if not files and not allow_empty:
        raise ValueError('périmètre de code vide')
    return files


def repository_identity(root):
    """Git's common directory identifies local worktrees without trusting a name/remote."""
    try:
        common = subprocess.check_output(['git', '-C', str(root), 'rev-parse', '--git-common-dir'],
                                         stderr=subprocess.DEVNULL, text=True).strip()
        revision = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'],
                                           stderr=subprocess.DEVNULL, text=True).strip()
        return {'common_dir': str((Path(root) / common).resolve()), 'revision': revision}
    except (OSError, subprocess.CalledProcessError):
        return None


def verify(proof, expected_project=None, require_success=True, expected_environment=None):
    if proof.get('format') != 'odoo-evidence/1':
        raise ValueError('format de preuve inconnu')
    original_root = Path(proof['project']).resolve()
    root = Path(expected_project).resolve() if expected_project else original_root
    if root != original_root:
        recorded, current = proof.get('repository'), repository_identity(root)
        if not recorded or not current or recorded != current:
            raise ValueError('preuve d’un autre projet ou révision : nouvelle vérification requise')
    if expected_environment is not None and proof.get('environment') != expected_environment:
        raise ValueError('environnement de contrôle différent ou non identifié')
    if require_success and (proof.get('result') != 'passed' or proof.get('exit_code') != 0):
        raise ValueError('contrôle non réussi')
    if fingerprint(root, proof['scopes']) != proof['sources']:
        raise ValueError('code changé depuis le contrôle')
    log = Path(proof['log']['path'])
    if root != original_root and proof['log'].get('relative_path'):
        log = (root / proof['log']['relative_path']).resolve()
        if not log.is_relative_to(root):
            raise ValueError('log hors projet')
    if hashlib.sha256(log.read_bytes()).hexdigest() != proof['log']['sha256']:
        raise ValueError('log changé depuis le contrôle')
    if require_success and proof.get('module') and not inspect_log(log.read_text(errors='replace'), proof['module'])['valid']:
        raise ValueError('aucune preuve de tests du module')


def execute(root, scopes, output, argv, timeout=600, module=None, environment=None):
    root, output = Path(root).resolve(), Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    log = output.with_suffix('.log')
    if output.exists() or log.exists():
        raise ValueError('preuve/log existant : choisir un nouveau chemin immuable')
    for scope in scopes:
        path = (root / scope).resolve()
        if output == path or log == path or output.is_relative_to(path) or log.is_relative_to(path):
            raise ValueError('placer la preuve et son log hors du périmètre contrôlé')
    before = fingerprint(root, scopes)
    started = time.monotonic()
    error = None
    with log.open('x') as stream:
        try:
            process = subprocess.Popen(argv, cwd=root, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                rc = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                raise
        except (subprocess.TimeoutExpired, OSError) as exc:
            rc, error = -1, type(exc).__name__
    try:
        unchanged = fingerprint(root, scopes) == before
    except (ValueError, OSError) as exc:
        unchanged, error = False, str(exc)
    passed = rc == 0 and unchanged
    if module:
        passed = passed and inspect_log(log.read_text(errors='replace'), module)['valid']
    proof = {'format': 'odoo-evidence/1', 'project': str(root), 'scopes': scopes,
             'sources': before, 'command': argv, 'exit_code': rc,
             'result': 'passed' if passed else 'failed', 'module': module, 'error': error,
             'seconds': round(time.monotonic() - started, 3),
             'log': {'path': str(log), 'sha256': hashlib.sha256(log.read_bytes()).hexdigest()}}
    proof['repository'] = repository_identity(root)
    proof['environment'] = environment
    proof['runner'] = {'python': platform.python_version(), 'platform': platform.system(), 'machine': platform.machine()}
    if log.is_relative_to(root):
        proof['log']['relative_path'] = str(log.relative_to(root))
    with output.open('x') as stream:
        stream.write(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
    return proof


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    run = sub.add_parser('run')
    run.add_argument('--project', type=Path, required=True)
    run.add_argument('--scope', action='append', required=True,
                     help='chemin de sources relatif au projet, répétable')
    run.add_argument('--output', type=Path, required=True,
                     help='nouveau fichier JSON hors des sources ; le helper crée aussi son .log, sans redirection manuelle')
    run.add_argument('--module',
                     help='exiger un bilan de tests Odoo pour ce module ; uniquement si la commande joue des tests, pas pour lint ou update seul')
    run.add_argument('--environment', help='identité stable de l’environnement contrôlé (image/données/outils)')
    run.add_argument('--timeout', type=int, default=600)
    run.add_argument('command', nargs=argparse.REMAINDER)
    check = sub.add_parser('verify')
    check.add_argument('proof', type=Path)
    args = parser.parse_args()
    try:
        if args.action == 'verify':
            verify(json.loads(args.proof.read_text()))
            print('Preuve valide et périmètre inchangé.')
        else:
            argv = args.command[1:] if args.command[:1] == ['--'] else args.command
            if not argv:
                raise ValueError('commande de contrôle requise')
            proof = execute(args.project, args.scope, args.output, argv, args.timeout, args.module, args.environment)
            print(proof['result'])
            raise SystemExit(0 if proof['result'] == 'passed' else 1)
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(2, str(exc) + '\n')
