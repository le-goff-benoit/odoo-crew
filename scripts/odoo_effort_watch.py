#!/usr/bin/env python3
"""Récupération locale des sessions dédiées : aucune attente système convertie en travail."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def folder():
    path = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache')) / 'odoo-crew' / 'effort'
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    return path


def register(release, task, agent, provider, source):
    from odoo_documents import atomic
    key = hashlib.sha256((str(release) + '\0' + str(source)).encode()).hexdigest()
    path = folder() / (key + '.json')
    if (Path(release) / 'closure.json').exists():
        raise ValueError('release scellée')
    value = dict(release=str(release), task=task, agent=agent, provider=provider, source=str(source))
    with path.with_suffix('.sample.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if path.exists() and json.loads(path.read_text()) != value:
            raise ValueError('session déjà affectée ou scellée : nouvelle session dédiée requise')
        atomic(path, value)
        path.chmod(0o600)
    return path


def sample(path):
    from odoo_effort import import_usage
    path = Path(path)
    with path.with_suffix('.sample.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        row = json.loads(path.read_text())
        if row.get('sealed'):
            return {'status': 'sealed'}
        release = Path(row['release'])
        if (release / 'closure.json').exists() or '<!-- release close -->' in (release / 'README.md').read_text():
            return {'status': 'sealed'}
        return import_usage(Path(row['release']), row['task'], row['agent'], row['provider'], Path(row['source']))


def launch(path):
    # Source paths remain in a private local cache, never in the versioned project.
    subprocess.Popen([sys.executable, str(Path(__file__).resolve()), str(path)],
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, start_new_session=True, close_fds=True)


def reconcile(project, restart=True):
    result = {'recovered': 0, 'warnings': []}
    root = Path(project).resolve()
    incomplete = []
    for path in folder().glob('*.json'):
        try:
            row = json.loads(path.read_text())
            target = Path(row['release']).resolve()
            if not (target.is_relative_to(root / 'changelog') or target.is_relative_to(root / '.odoo-agents/express')):
                continue
            if sample(path).get('status') == 'sealed': continue
            result['recovered'] += 1
            if restart: launch(path)
        except (OSError, ValueError, KeyError) as exc:
            result['warnings'].append('Mesure à reprendre : ' + str(exc))
    return result


def seal(project):
    from odoo_documents import atomic
    root = Path(project).resolve()
    incomplete = []
    for path in folder().glob('*.json'):
        row = json.loads(path.read_text())
        if Path(row['release']).resolve() != root: continue
        observed = sample(path)
        if observed.get('status') not in ('complete','sealed'):
            incomplete.append({'task':row['task'],'agent':row['agent'],'reason':'dernier relevé incomplet ; durée manquante conservée inconnue'})
        with path.with_suffix('.sample.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            row['sealed'] = True
            atomic(path, row)
    return {'sealed': str(root), 'incomplete': incomplete}


def watch(path, idle_seconds=600, interval=15):
    path = Path(path)
    with path.with_suffix('.lock').open('a') as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: return
        last = None; changed_at = time.monotonic()
        while True:
            try:
                value = sample(path)
                if value.get('status') == 'sealed': return
                fingerprint = value.get('source_sha256')
                if fingerprint != last:
                    last = fingerprint; changed_at = time.monotonic()
                path.with_suffix('.error').unlink(missing_ok=True)
                if value.get('status') == 'complete' and time.monotonic() - changed_at >= idle_seconds:
                    return
            except (OSError, ValueError, KeyError) as exc:
                path.with_suffix('.error').write_text(str(exc))
                return
            time.sleep(interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('binding', type=Path)
    watch(parser.parse_args().binding)
