#!/usr/bin/env python3
"""Execute the frozen Odoo 19 multi-company rights contract in disposable Docker containers."""
import argparse
import hashlib
import json
import shutil
import subprocess
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'benchmarks/qualification/rights'


def extract(text, marker):
    matches = [line.split(marker, 1)[1] for line in text.splitlines() if line.startswith(marker)]
    if len(matches) != 1:
        raise ValueError(f'Expected one {marker} record, found {len(matches)}')
    return json.loads(matches[0])


def run(output):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    frozen = output / 'frozen'
    shutil.copytree(FIXTURES, frozen, ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy2(__file__, output / 'runner.py')
    hashes = {str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(output.rglob('*')) if p.is_file()}
    (output / 'frozen-sha256.json').write_text(json.dumps(hashes, indent=2) + '\n')
    protocol = json.loads((frozen / 'protocol.json').read_text())
    if len(protocol['variants']) > protocol['budget']['maximum_variants']:
        raise ValueError('Variant budget exceeded')
    started = time.monotonic()
    prefix = 'quality-rights-' + uuid.uuid4().hex[:10]
    network, pg = prefix + '-net', prefix + '-db'
    containers = []
    state = {'status': 'running', 'prefix': prefix, 'trials': [], 'protocol_sha256': hashes['frozen/protocol.json']}

    def save():
        (output / 'state.json').write_text(json.dumps(state, indent=2, ensure_ascii=False) + '\n')

    def command(args, log=None, source=None, check=True, cleanup=False):
        remaining = protocol['budget']['maximum_seconds'] - (time.monotonic() - started)
        timeout = 30 if cleanup else min(300, max(1, remaining))
        if remaining <= 0 and not cleanup:
            raise TimeoutError('Qualification budget exhausted')
        result = subprocess.run(args, input=source, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=timeout, check=False)
        if log:
            (output / log).write_text(result.stdout)
        if check and result.returncode:
            raise RuntimeError(f'Command failed ({result.returncode}); log={log}: {result.stdout[-1500:]}')
        return result

    def docker(name, detached=False):
        containers.append(name)
        return ['docker', 'run', '-d' if detached else '-i', '--rm', '--name', name,
                '--network', network, '--read-only', '--cap-drop=ALL',
                '--security-opt=no-new-privileges', '--memory=2g', '--cpus=2', '--pids-limit=256',
                '--tmpfs', '/tmp:rw,mode=1777', '--tmpfs', '/var/lib/odoo:rw,uid=101,gid=101',
                '-v', str(frozen / 'project') + ':/mnt/quality:ro',
                '-v', str(frozen) + ':/mnt/oracle:ro', '--entrypoint', 'odoo', 'odoo-qa:19.0']

    def options(db):
        return ['--db_host', pg, '--db_user', 'odoo', '--db_password', 'odoo',
                '--addons-path', '/usr/lib/python3/dist-packages/odoo/addons,/mnt/quality',
                '--without-demo=all', '--data-dir=/tmp/odoo', '--max-cron-threads=0', '-d', db]

    try:
        save()
        state['image_ids'] = {image: command(['docker', 'image', 'inspect', '--format={{.Id}}', image]).stdout.strip()
                              for image in ['odoo-qa:19.0', 'postgres:16']}
        command(['docker', 'network', 'create', '--internal', network], 'network-create.log')
        command(['docker', 'run', '-d', '--rm', '--name', pg, '--network', network,
                 '-e', 'POSTGRES_USER=odoo', '-e', 'POSTGRES_PASSWORD=odoo', '--memory=512m', 'postgres:16'], 'postgres-start.log')
        for _ in range(60):
            if command(['docker', 'exec', pg, 'pg_isready', '-U', 'odoo'], check=False).returncode == 0:
                break
            time.sleep(0.5)
        else:
            raise RuntimeError('PostgreSQL readiness timeout')
        for index, variant in enumerate(protocol['variants']):
            name, db = variant['name'], f'qualification_{index}'
            trial_started = time.monotonic()
            command(docker(prefix + f'-init-{index}') + options(db) +
                    ['--stop-after-init', '--no-http', '-i', 'quality_rights'], f'{name}-install.log')
            source = (frozen / 'seed.py').read_text()
            if not variant['rule_active']:
                source += "\nenv.ref('quality_rights.company_rule').write({'active': False})\nenv.cr.commit()\n"
            seeded = command(docker(prefix + f'-seed-{index}') + ['shell'] + options(db) + ['--no-http'],
                             f'{name}-seed.log', source=source)
            seed = extract(seeded.stdout, 'QUALIFICATION_SEED=')
            orm = command(docker(prefix + f'-orm-{index}') + ['shell'] + options(db) + ['--no-http'],
                          f'{name}-orm.log', source=(frozen / 'oracle_orm.py').read_text())
            orm_result = extract(orm.stdout, 'QUALIFICATION_ORM=')
            http = prefix + f'-http-{index}'
            command(docker(http, detached=True) + options(db) + ['--http-interface=127.0.0.1'], f'{name}-http-start.log')
            command(['docker', 'exec', http, 'odoo', '--version'], f'{name}-version.log')
            rpc = command(['docker', 'exec', http, 'python3', '/mnt/oracle/oracle_rpc.py', db, json.dumps(seed)], f'{name}-rpc.log')
            rpc_result = extract(rpc.stdout, 'QUALIFICATION_RPC=')
            command(['docker', 'logs', http], f'{name}-http.log')
            command(['docker', 'rm', '-f', http], f'{name}-http-stop.log')
            # The privileged audit is separate from the ordinary-user RPC observations.
            audit_source = "import json\nprint('QUALIFICATION_AUDIT=' + json.dumps(env['quality.rights.record'].search([]).read(['name','company_id','value'])))\n"
            audit = command(docker(prefix + f'-audit-{index}') + ['shell'] + options(db) + ['--no-http'],
                            f'{name}-audit.log', source=audit_source)
            rows = extract(audit.stdout, 'QUALIFICATION_AUDIT=')
            postconditions = {
                'rpc_foreign_unchanged': next(r for r in rows if r['id'] == seed['b'])['value'] == 20,
                'rpc_foreign_import_absent': not any(r['name'] == 'RPC foreign import' for r in rows),
                'rpc_own_exact_value': next(r for r in rows if r['id'] == seed['a'])['value'] == 12,
            }
            secure = orm_result['secure'] and rpc_result['secure'] and all(postconditions.values())
            trial = {'name': name, 'seed': seed, 'orm': orm_result, 'rpc': rpc_result,
                     'privileged_postconditions': postconditions, 'final_rows': rows,
                     'secure': secure, 'expected_secure': variant['expected_secure'],
                     'expectation_met': secure == variant['expected_secure'],
                     'seconds': round(time.monotonic() - trial_started, 2)}
            state['trials'].append(trial)
            save()
            print(json.dumps({'name': name, 'secure': secure, 'expectation_met': trial['expectation_met']}), flush=True)
            if index == 0 and not secure:
                raise RuntimeError('Reference invalid; mutation execution withheld')
        state['status'] = 'completed' if all(t['expectation_met'] for t in state['trials']) else 'failed'
    except Exception as exc:  # noqa: BLE001 - preserve any infrastructure incident before cleanup
        state.update(status='error', error=str(exc))
    finally:
        for name in containers + [pg]:
            command(['docker', 'rm', '-f', name], check=False, cleanup=True)
        command(['docker', 'network', 'rm', network], 'network-cleanup.log', check=False, cleanup=True)
        remaining_containers = command(['docker', 'ps', '-a', '--filter', f'name={prefix}', '--format', '{{.Names}}'], cleanup=True).stdout.strip()
        remaining_networks = command(['docker', 'network', 'ls', '--filter', f'name={network}', '--format', '{{.Name}}'], cleanup=True).stdout.strip()
        state['cleanup'] = {'containers': remaining_containers, 'networks': remaining_networks,
                            'verified': not remaining_containers and not remaining_networks}
        state['seconds'] = round(time.monotonic() - started, 2)
        if not state['cleanup']['verified']:
            state['status'] = 'error'
        save()
        evidence = {str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted(output.rglob('*')) if p.is_file() and p.name != 'SHA256.json'}
        (output / 'SHA256.json').write_text(json.dumps(evidence, indent=2) + '\n')
    return state


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = run(args.output)
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'], 'cleanup': result['cleanup']}, ensure_ascii=False))
    raise SystemExit(0 if result['status'] == 'completed' else 1)
