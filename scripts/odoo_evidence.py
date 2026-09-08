#!/usr/bin/env python3
"""Exécuter un contrôle et lier son résultat au contenu réellement contrôlé."""
import argparse
import hashlib
import json
import os
import signal
from pathlib import Path
import subprocess
import time

from odoo_test_result import inspect_log


def fingerprint(root, scopes):
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
    if not files:
        raise ValueError('périmètre de code vide')
    return files


def verify(proof, expected_project=None, require_success=True):
    if proof.get('format') != 'odoo-evidence/1':
        raise ValueError('format de preuve inconnu')
    root = Path(proof['project']).resolve()
    if expected_project and root != Path(expected_project).resolve():
        raise ValueError('preuve d’un autre projet')
    if require_success and (proof.get('result') != 'passed' or proof.get('exit_code') != 0):
        raise ValueError('contrôle non réussi')
    if fingerprint(root, proof['scopes']) != proof['sources']:
        raise ValueError('code changé depuis le contrôle')
    log = Path(proof['log']['path'])
    if hashlib.sha256(log.read_bytes()).hexdigest() != proof['log']['sha256']:
        raise ValueError('log changé depuis le contrôle')
    if require_success and proof.get('module') and not inspect_log(log.read_text(errors='replace'), proof['module'])['valid']:
        raise ValueError('aucune preuve de tests du module')


def execute(root, scopes, output, argv, timeout=600, module=None):
    root, output = Path(root).resolve(), Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    log = output.with_suffix('.log')
    for scope in scopes:
        path = (root / scope).resolve()
        if output == path or log == path or output.is_relative_to(path) or log.is_relative_to(path):
            raise ValueError('placer la preuve et son log hors du périmètre contrôlé')
    before = fingerprint(root, scopes)
    started = time.monotonic()
    error = None
    with log.open('w') as stream:
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
    output.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
    return proof


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    run = sub.add_parser('run')
    run.add_argument('--project', type=Path, required=True)
    run.add_argument('--scope', action='append', required=True)
    run.add_argument('--output', type=Path, required=True)
    run.add_argument('--module')
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
            proof = execute(args.project, args.scope, args.output, argv, args.timeout, args.module)
            print(proof['result'])
            raise SystemExit(0 if proof['result'] == 'passed' else 1)
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(2, str(exc) + '\n')
