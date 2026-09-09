#!/usr/bin/env python3
"""Qualifie le vrai restaurateur dans une stack synthétique dédiée, sans ports."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'benchmarks/qualification/restore'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    project = 'qualification-restore-' + uuid.uuid4().hex[:10]
    started = time.monotonic()
    stack = output / 'pack/stack'
    scripts = output / 'pack/scripts'
    for path in (stack, scripts, stack / 'artifacts', output / 'addons'):
        path.mkdir(parents=True, exist_ok=True)
        path.chmod(0o777)
    for name in ('odoo-restore.sh', 'series-env.sh', 'odoo_series.py'):
        shutil.copy2(ROOT / 'scripts' / name, scripts / name)
    shutil.copy2(ROOT / 'stack/odoo.conf', stack / 'odoo.conf')
    shutil.copy2(FIXTURE / 'protocol.json', output / 'protocol.json')
    # Exécuter les entrées figées, pas des fixtures susceptibles de changer en parallèle.
    shutil.copy2(Path(__file__), output / 'runner-executed.py')
    for name in ('seed.py', 'check.py'):
        shutil.copy2(FIXTURE / name, output / name)
    config = {
        'name': project,
        'services': {
            'db': {'image': 'pgvector/pgvector:pg16',
                   'environment': {'POSTGRES_USER': 'odoo', 'POSTGRES_PASSWORD': 'odoo', 'POSTGRES_DB': 'postgres'},
                   'volumes': ['pgdata:/var/lib/postgresql/data']},
            'odoo': {'image': 'odoo-qa:19.0', 'command': ['sleep', 'infinity'],
                     'environment': {'HOST': 'db', 'USER': 'odoo', 'PASSWORD': 'odoo'},
                     'volumes': ['./odoo.conf:/etc/odoo/odoo.conf:ro',
                                 'filestore:/var/lib/odoo',
                                 str(output / 'addons') + ':/mnt/extra-addons:ro',
                                 './artifacts:/mnt/artifacts']},
        },
        'volumes': {'pgdata': {}, 'filestore': {}},
        'networks': {'default': {'internal': True}},
    }
    (stack / 'compose.json').write_text(json.dumps(config, indent=2) + '\n')
    # No inherited Compose routing, Docker remote target, client addons or Odoo DB.
    environment = {key: os.environ[key] for key in ('PATH', 'HOME', 'LANG', 'USER') if key in os.environ}
    environment.update(COMPOSE_PROJECT_NAME=project, COMPOSE_FILE=str(stack / 'compose.json'),
                       ODOO_SERIES='19.0', ODOO_ADDONS_DIR=str(output / 'addons'))
    events = []

    def run(label, command, stdin=None, check=True):
        remaining = 900 - (time.monotonic() - started)
        if remaining <= 0:
            raise TimeoutError('Budget de 900 secondes épuisé')
        before = time.monotonic()
        result = subprocess.run(command, cwd=stack, env=environment, input=stdin,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=min(remaining, 240))
        (output / f'{label}.stdout').write_bytes(result.stdout)
        (output / f'{label}.stderr').write_bytes(result.stderr)
        events.append({'label': label, 'command': command, 'exit_code': result.returncode,
                       'seconds': round(time.monotonic() - before, 3)})
        (output / 'events.json').write_text(json.dumps(events, indent=2) + '\n')
        if check and result.returncode:
            raise RuntimeError(f'{label}: exit {result.returncode}; voir les logs')
        return result

    def compose(label, *command, **kwargs):
        return run(label, ['docker', 'compose', *command], **kwargs)

    def sql(label, db, query):
        return compose(label, 'exec', '-T', 'db', 'psql', '-U', 'odoo', '-d', db,
                       '-v', 'ON_ERROR_STOP=1', '-Atc', query).stdout.decode().strip()

    def shell(label, db, code):
        return compose(label, 'exec', '-T', 'odoo', 'odoo', 'shell', '-c', '/etc/odoo/odoo.conf',
                       '-d', db, '--no-http', stdin=code)

    def parsed(result):
        return json.loads(next(line.split('=', 1)[1] for line in result.stdout.decode().splitlines()
                               if line.startswith('QUALIFICATION_JSON=')))

    def neighbor(label):
        db_value = sql(label + '-db', 'qualification_neighbor', 'SELECT value FROM sentinel')
        content = compose(label + '-file', 'exec', '-T', 'odoo', 'cat',
                          '/var/lib/odoo/filestore/qualification_neighbor/sentinel').stdout
        return {'database': db_value, 'filestore_sha256': hashlib.sha256(content).hexdigest()}

    report = {'project': project, 'scenarios': {}, 'status': 'running', 'limits': json.loads((output / 'protocol.json').read_text())['limits']}
    try:
        identity = run('images', ['docker', 'image', 'inspect', 'odoo-qa:19.0', 'pgvector/pgvector:pg16'])
        (output / 'identity.json').write_text(json.dumps({
            'reference': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
            'images': [{'id': item['Id'], 'tags': item['RepoTags']} for item in json.loads(identity.stdout)],
            'restore_sha256': digest(scripts / 'odoo-restore.sh'),
            'protocol_sha256': digest(output / 'protocol.json'),
        }, indent=2) + '\n')
        compose('config', 'config', '--format', 'json')
        compose('up', 'up', '-d')
        for attempt in range(30):
            if compose(f'ready-{attempt}', 'exec', '-T', 'db', 'pg_isready', '-U', 'odoo', check=False).returncode == 0:
                break
            time.sleep(1)
        compose('initialize', 'exec', '-T', 'odoo', 'odoo', '-c', '/etc/odoo/odoo.conf',
                '-d', 'qualification_source', '-i', 'base', '--without-demo=all', '--stop-after-init', '--no-http')
        metadata = parsed(shell('seed', 'qualification_source', (output / 'seed.py').read_bytes()))
        sql('neighbor-create', 'postgres', 'CREATE DATABASE qualification_neighbor')
        sql('neighbor-seed', 'qualification_neighbor', "CREATE TABLE sentinel (value text); INSERT INTO sentinel VALUES ('qualification unchanged')")
        compose('neighbor-file', 'exec', '-T', 'odoo', 'sh', '-c',
                'mkdir -p /var/lib/odoo/filestore/qualification_neighbor && printf qualification-neighbor > /var/lib/odoo/filestore/qualification_neighbor/sentinel')
        initial = neighbor('neighbor-before')
        dump = compose('source-dump', 'exec', '-T', 'db', 'pg_dump', '-U', 'odoo', '--no-owner', '--no-privileges', 'qualification_source').stdout
        payload = compose('source-filestore', 'exec', '-T', 'odoo', 'cat',
                          '/var/lib/odoo/filestore/qualification_source/' + metadata['store_fname']).stdout
        backup = output / 'qualification-complete.zip'
        with zipfile.ZipFile(backup, 'w', zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('dump.sql', dump)
            archive.writestr('manifest.json', json.dumps({'version': '19.0'}))
            archive.writestr('filestore/' + metadata['store_fname'], payload)
        incomplete = output / 'qualification-missing.zip'
        with zipfile.ZipFile(incomplete, 'w') as archive:
            archive.writestr('manifest.json', json.dumps({'version': '19.0'}))
        for scenario, archive, extra in (
            ('complete', backup, []), ('missing_dump', incomplete, []),
            ('invalid_update', backup, ['--update', 'qualification_nonexistent_module']),
        ):
            db = 'qualification_' + scenario
            result = run(scenario, ['bash', str(scripts / 'odoo-restore.sh'), str(archive), '--db', db, '--series', '19.0', *extra], check=False)
            exists = sql(scenario + '-exists', 'postgres', f"SELECT count(*) FROM pg_database WHERE datname='{db}'") == '1'
            checks = {'neighbor_unchanged': neighbor(scenario + '-neighbor') == initial}
            checks['expected_exit'] = (result.returncode == 0) if scenario == 'complete' else result.returncode != 0
            checks['expected_banner'] = (f'Base {db} prête :'.encode() in result.stdout) == (scenario == 'complete')
            checks['expected_database'] = exists == (scenario != 'missing_dump')
            if exists:
                checks.update(parsed(shell(scenario + '-postconditions', db, (output / 'check.py').read_bytes())))
            report['scenarios'][scenario] = {'exit_code': result.returncode, 'checks': checks, 'pass': all(checks.values())}
        source = parsed(shell('source-after', 'qualification_source', (output / 'check.py').read_bytes()))
        report['source_unchanged'] = source['attachment_bytes'] and not source['cron_disabled'] and not source['mail_disabled'] and not source['neutralized'] and not source['local_url']
        report['status'] = 'pass' if report['source_unchanged'] and all(case['pass'] for case in report['scenarios'].values()) else 'fail'
    except Exception as exc:
        report['status'] = 'incident'
        report['error'] = str(exc)
    finally:
        # Cleanup independent of the experiment deadline, confined to its exact project.
        cleanup = subprocess.run(['docker', 'compose', 'down', '-v', '--remove-orphans'], cwd=stack,
                                 env=environment, capture_output=True, timeout=60)
        (output / 'cleanup.stdout').write_bytes(cleanup.stdout)
        (output / 'cleanup.stderr').write_bytes(cleanup.stderr)
        leftovers = {}
        for kind in ('container', 'volume', 'network'):
            command = ['docker', kind, 'ls', '-q', '--filter', f'label=com.docker.compose.project={project}']
            if kind == 'container':
                command.insert(3, '-a')
            result = subprocess.run(command, env=environment, capture_output=True, timeout=15)
            leftovers[kind] = {'exit_code': result.returncode, 'ids': result.stdout.decode().split()}
        report['cleanup'] = {'exit_code': cleanup.returncode, 'remaining': leftovers}
        report['seconds'] = round(time.monotonic() - started, 3)
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        hashes = {str(path.relative_to(output)): digest(path) for path in output.rglob('*') if path.is_file() and path.name != 'SHA256.json'}
        (output / 'SHA256.json').write_text(json.dumps(hashes, indent=2, sort_keys=True) + '\n')
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['status'] == 'pass' and cleanup.returncode == 0 and all(not item['ids'] and item['exit_code'] == 0 for item in leftovers.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
