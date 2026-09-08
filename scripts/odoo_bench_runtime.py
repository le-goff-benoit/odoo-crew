#!/usr/bin/env python3
"""Oracle Odoo 19 synthétique dans des conteneurs jetables sans accès aux clients."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import uuid

from odoo_test_result import inspect_log

ROOT = Path(__file__).resolve().parents[1]


def command(args, *, log=None, timeout=300):
    if log:
        with Path(log).open('w') as stream:
            result = subprocess.run(args, stdout=stream, stderr=subprocess.STDOUT, timeout=timeout)
    else:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    return result


def campaign(output, candidates, mutations=False, studio=False):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    prefix = 'quality-lab-' + uuid.uuid4().hex[:10]
    network, database = prefix + '-net', prefix + '-db'
    state = {'studio': studio, 'status': 'running', 'scope': 'Odoo 19 synthetic isolated business oracle', 'trials': []}
    active = None
    try:
        command(['docker', 'network', 'create', '--internal', network]).check_returncode()
        command(['docker', 'run', '-d', '--rm', '--name', database, '--network', network,
                 '-e', 'POSTGRES_USER=odoo', '-e', 'POSTGRES_PASSWORD=odoo',
                 '--memory=512m', 'postgres:16']).check_returncode()
        for _ in range(60):
            if command(['docker', 'exec', database, 'pg_isready', '-U', 'odoo']).returncode == 0:
                break
            time.sleep(0.5)
        else:
            raise RuntimeError('PostgreSQL synthétique indisponible')
        original = (ROOT / 'benchmarks/odoo/quality_case/models/delivery.py').read_text()
        versions = [('reference', original, True)]
        for name, path in candidates.items():
            versions.append((name, Path(path).read_text(), True))
        if mutations:
            mutations_map = {
                'threshold_exclusive': ('record.ordered_qty * 0.6, precision_digits=6) >= 0', 'record.ordered_qty * 0.6, precision_digits=6) > 0'),
                'self_approval': ('if any(record.create_uid == self.env.user for record in self):', 'if False:'),
                'stale_approval': ("super(QualityDelivery, invalidate).write({'approved': False})", 'pass'),
            }
            for name, (before, after) in mutations_map.items():
                if original.count(before) != 1:
                    raise ValueError('mutation devenue ambiguë : ' + name)
                versions.append((name, original.replace(before, after), False))
        with tempfile.TemporaryDirectory(prefix='quality-addons-') as tmp:
            addons = Path(tmp)
            addons.chmod(0o755)
            for module in ('quality_case', 'quality_oracle'):
                shutil.copytree(ROOT / 'benchmarks/odoo' / module, addons / module, ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copy2(ROOT / 'scripts/odoo_pack.py', addons / 'quality_oracle/tests/pack_driver.py')
            base = ['docker', 'run', '--rm', '--network', network, '--read-only', '--cap-drop=ALL',
                    '--security-opt=no-new-privileges', '--memory=2g', '--cpus=2', '--pids-limit=256',
                    '--tmpfs', '/tmp:rw,mode=1777', '--tmpfs', '/var/lib/odoo:rw,uid=101,gid=101',
                    '-v', str(addons) + ':/mnt/quality:ro', '--entrypoint', 'odoo']
            if studio:
                base[base.index('--entrypoint'):base.index('--entrypoint')] = ['-v', str(Path.home() / 'odoo-sources/19.0-enterprise') + ':/mnt/enterprise:ro']
            options = ['--db_host', database, '--db_user', 'odoo', '--db_password', 'odoo',
                       '--addons-path', '/usr/lib/python3/dist-packages/odoo/addons,/mnt/quality' + (',/mnt/enterprise' if studio else ''),
                       '--stop-after-init', '--no-http', '--without-demo=all', '--data-dir=/tmp/odoo', '--max-cron-threads=0']
            active = prefix + '-base'
            started = time.monotonic()
            result = command(base + ['--name', active, 'odoo-qa:19.0'] + options + ['-d', 'lab_template', '-i', 'web_studio' if studio else 'base'], log=output / 'template.log')
            result.check_returncode()
            state['template_seconds'] = round(time.monotonic() - started, 2)
            state['image_id'] = command(['docker', 'image', 'inspect', '--format={{.Id}}', 'odoo-qa:19.0']).stdout.strip()
            for number, (name, code, expected) in enumerate(versions):
                (addons / 'quality_case/models/delivery.py').write_text(code)
                snapshot = output / f'{number}-source'
                shutil.copytree(addons, snapshot)
                sources = {str(p.relative_to(snapshot)): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sorted(snapshot.rglob('*')) if p.is_file()}
                (output / f'{number}-sources.json').write_text(json.dumps(sources, indent=2) + '\n')
                trial_db = f'lab_trial_{number}'
                command(['docker', 'exec', database, 'createdb', '-U', 'odoo', '-T', 'lab_template', trial_db]).check_returncode()
                active = prefix + '-' + str(number)
                started = time.monotonic()
                log = output / f'{number}.log'
                result = command(base + ['--name', active, 'odoo-qa:19.0'] + options +
                                 ['-d', trial_db, '-i', 'quality_oracle', '--test-enable', '--test-tags=/quality_oracle', '--log-level=test'], log=log)
                proof = inspect_log(log.read_text(errors='replace'), 'quality_oracle')
                passed = result.returncode == 0 and proof['valid']
                trial = {'name': name, 'seconds': round(time.monotonic() - started, 2), 'exit_code': result.returncode,
                         'passed': passed, 'expected_pass': expected, 'expectation_met': passed == expected,
                         'proof': proof, 'log': log.name, 'sources': f'{number}-sources.json',
                         'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest()}
                state['trials'].append(trial)
                (output / 'state.json').write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
                print(json.dumps(trial, ensure_ascii=False), flush=True)
                # A broken reference invalidates mutation conclusions, not just one row.
                if name == 'reference' and not passed:
                    raise RuntimeError('référence invalide : corriger le banc avant toute comparaison')
                command(['docker', 'exec', database, 'dropdb', '-U', 'odoo', trial_db]).check_returncode()
        state['status'] = 'completed' if all(t['expectation_met'] for t in state['trials']) else 'failed'
    except Exception as exc:
        state.update(status='error', error=str(exc))
        raise
    finally:
        if active:
            command(['docker', 'rm', '-f', active], timeout=30)
        command(['docker', 'rm', '-f', database], timeout=30)
        command(['docker', 'network', 'rm', network], timeout=30)
        (output / 'state.json').write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
    return state


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--candidate', action='append', default=[], help='label=chemin du fichier Python')
    parser.add_argument('--mutations', action='store_true')
    parser.add_argument('--studio', action='store_true')
    args = parser.parse_args()
    candidates = dict(item.split('=', 1) for item in args.candidate)
    result = campaign(args.output, candidates, args.mutations, args.studio)
    raise SystemExit(0 if result['status'] == 'completed' else 1)
