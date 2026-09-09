#!/usr/bin/env python3
"""Bounded, synthetic E03 runtime. Preparation and cleanup are outside trial timing.

prepare-pair --seed-project PATH --run-s RUN --run-d RUN --state PATH
--run RUN test [--tags TAGS] [--expect Class.test_method ...]
--run RUN update|inventory|shell [--script PATH]
cleanup --state PATH
Each RUN contains project/ and runtime.json. No database selector is exposed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

LABEL = 'delegation-comparison-owner'
DEFAULT_TESTS = ['TestQuantity.test_' + n for n in ('zero', 'negative_create', 'negative_write', 'confirmation')]
PASSWORD = 'synthetic-lab-only'


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')


def command(args, logs, name, stdin=None, timeout=360, check=True):
    logs.mkdir(parents=True, exist_ok=True)
    base = logs / (name + '-' + time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8])
    started = time.monotonic()
    try:
        result = subprocess.run(args, input=stdin, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=timeout)
        rc, output = result.returncode, result.stdout
    except subprocess.TimeoutExpired as exc:
        rc, output = 124, exc.stdout or ''
        if isinstance(output, bytes):
            output = output.decode(errors='replace')
    base.with_suffix('.log').write_text(output)
    report = dict(command=args, returncode=rc, seconds=round(time.monotonic()-started, 3), log=str(base.with_suffix('.log')))
    write_json(base.with_suffix('.json'), report)
    print(json.dumps(report), flush=True)
    if check and rc:
        raise RuntimeError(f'{name} failed ({rc}): {base}.log')
    return rc, output, base


def remove_owned(name, kind, cfg, logs):
    rc, out, _ = command(['docker', kind, 'inspect', name], logs, 'inspect-cleanup', timeout=30, check=False)
    if rc:
        # Missing resources are normal for --rm; daemon errors are not.
        if 'No such' not in out:
            raise RuntimeError(out)
        return
    obj = json.loads(out)[0]
    labels = obj.get('Config', {}).get('Labels', {}) if kind == 'container' else obj.get('Labels', {})
    if (labels or {}).get(LABEL) != cfg['owner']:
        raise RuntimeError('Cleanup owner mismatch: ' + name)
    cmd = ['docker', 'rm', '-f', name] if kind == 'container' else ['docker', 'network', 'rm', name]
    command(cmd, logs, 'cleanup-' + kind, timeout=30)


def odoo(cfg, action, logs, tags='/lab_qualification', expected=None, script=None):
    name = cfg['prefix'] + '-odoo-' + uuid.uuid4().hex[:10]
    # Each ephemeral container gets its own persistent receipt, avoiding shared-state races.
    write_json(logs / ('container-' + name + '.json'), dict(name=name, owner=cfg['owner']))
    args = ['docker', 'run', '--rm', '-i', '--name', name, '--label', LABEL+'='+cfg['owner'],
            '--network', cfg['network'], '--tmpfs', '/var/lib/odoo:mode=1777',
            '--mount', f'type=bind,src={cfg["project"]},dst=/mnt/extra-addons,readonly',
            '--entrypoint', 'odoo', cfg['images']['odoo-qa:19.0']['id']]
    if action in ('shell', 'inventory'):
        args += ['shell']
    args += ['--db_host', cfg['postgres'], '--db_user', 'odoo', '--db_password', PASSWORD,
             '-d', cfg['database'], '--addons-path', '/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons',
             '--data-dir', '/tmp/odoo-data', '--without-demo', '--no-http', '--max-cron-threads', '0', '--workers', '0']
    if action not in ('shell', 'inventory'):
        args += ['--stop-after-init', '-i' if action == 'install' else '-u', 'lab_qualification']
    if action == 'test':
        args += ['--test-enable', '--test-tags', tags, '--log-level', 'test']
    try:
        rc, out, base = command(args, logs, action, stdin=script, check=False)
        if action == 'test':
            summaries = [tuple(map(int, match)) for match in re.findall(r'(\d+) failed, (\d+) error\(s\) of (\d+) tests', out)]
            started = sorted(set(re.findall(r'Starting (Test\w+\.test_\w+)', out)))
            required = expected or cfg['expected_tests']
            missing = sorted(set(required)-set(started))
            skipped = bool(re.search(r'\bskipped\b', out, re.I))
            passed = rc == 0 and bool(summaries) and any(n > 0 for _, _, n in summaries) and all(f == e == 0 for f, e, _ in summaries) and not missing and not skipped
            report = dict(passed=passed, process_exit=rc, tags=tags, summaries=summaries,
                          started_tests=started, expected_tests=required, missing_tests=missing, skipped=skipped)
            write_json(base.with_suffix('.tests.json'), report)
            print(json.dumps(report), flush=True)
            rc = 0 if passed else (rc or 1)
        return rc, out, base
    finally:
        remove_owned(name, 'container', cfg, logs)


def inventory(cfg, logs):
    script = """import json
records=env['lab.qualification'].search([],order='id')
print('INVENTORY_JSON='+json.dumps({'records':records.read(['name','state','quantity','unit_price','amount']),'module':env['ir.module.module'].search([('name','=','lab_qualification')]).read(['name','state','installed_version'])},sort_keys=True))
"""
    rc, out, base = odoo(cfg, 'inventory', logs, script=script)
    matches = re.findall(r'INVENTORY_JSON=(\{[^\n]*\})', out)
    if rc or len(matches) != 1:
        raise RuntimeError('Inventory missing or failed')
    data = json.loads(matches[0])
    data['semantic_sha256'] = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    write_json(base.with_suffix('.inventory.json'), data)
    return data


def hashes(project):
    return {str(p.relative_to(project)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(project.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}


def prepare(args):
    state = args.state.resolve()
    state.mkdir(parents=True, exist_ok=False)
    logs = state / 'evidence'
    prefix = 'delegcmp-' + uuid.uuid4().hex[:12]
    cfg = dict(owner=uuid.uuid4().hex, prefix=prefix, network=prefix+'-net', postgres=prefix+'-pg',
               database='comparison_seed', images={}, expected_tests=DEFAULT_TESTS)
    seed = state / 'seed-project'
    shutil.copytree(args.seed_project.resolve(), seed)
    cfg['project'] = str(seed)
    cfg['runs'] = [str(args.run_s.resolve()), str(args.run_d.resolve())]
    statefile = state / 'resources.json'
    write_json(statefile, cfg)
    for tag in ('odoo-qa:19.0', 'postgres:16'):
        _, out, _ = command(['docker', 'image', 'inspect', tag], logs, 'image', timeout=30)
        obj = json.loads(out)[0]
        cfg['images'][tag] = dict(id=obj['Id'], digests=obj.get('RepoDigests', []))
    write_json(statefile, cfg)
    command(['docker', 'network', 'create', '--internal', '--label', LABEL+'='+cfg['owner'], cfg['network']], logs, 'network')
    command(['docker', 'run', '-d', '--name', cfg['postgres'], '--label', LABEL+'='+cfg['owner'],
             '--network', cfg['network'], '--tmpfs', '/var/lib/postgresql/data', '-e', 'POSTGRES_USER=odoo',
             '-e', 'POSTGRES_PASSWORD='+PASSWORD, cfg['images']['postgres:16']['id']], logs, 'postgres')
    for _ in range(30):
        rc, _, _ = command(['docker', 'exec', cfg['postgres'], 'pg_isready', '-U', 'odoo'], logs, 'pg-ready', check=False, timeout=10)
        if rc == 0:
            break
        time.sleep(1)
    else:
        raise RuntimeError('Postgres unavailable')
    rc, _, _ = odoo(cfg, 'install', logs)
    if rc:
        raise RuntimeError('Seed installation failed')
    seed_script = """model=env['lab.qualification']
assert not model.search_count([])
model.create([{'name':'Seed priced','quantity':3,'unit_price':12},{'name':'Seed free','quantity':4,'unit_price':0},{'name':'Seed empty','quantity':0,'unit_price':11}])
env.cr.commit()
"""
    rc, _, _ = odoo(cfg, 'shell', logs, script=seed_script)
    if rc:
        raise RuntimeError('Seed data failed')
    cfg['seed_hashes'] = hashes(seed)
    cfg['seed_inventory'] = inventory(cfg, logs)
    for i, run in enumerate((args.run_s.resolve(), args.run_d.resolve())):
        run.mkdir(parents=True, exist_ok=True)
        project = run / 'project'
        if project.exists():
            if hashes(project) != cfg['seed_hashes']:
                raise RuntimeError('Existing run project differs from seed: ' + str(project))
        else:
            shutil.copytree(seed, project)
        run_cfg = {k:v for k,v in cfg.items() if k not in ('runs', 'seed_inventory', 'seed_hashes')}
        run_cfg.update(database='comparison_run_'+str(i), project=str(project))
        command(['docker', 'exec', cfg['postgres'], 'createdb', '-U', 'odoo', '-T', cfg['database'], run_cfg['database']], logs, 'clone')
        write_json(run / 'runtime.json', run_cfg)
        data = inventory(run_cfg, run / 'runtime-evidence')
        if data != cfg['seed_inventory']:
            raise RuntimeError('Cloned inventory mismatch')
        write_json(run / 'runtime-evidence' / 'initial-state.json', dict(inventory=data, project_hashes=hashes(project), images=cfg['images']))
    cfg['prepared'] = True
    write_json(statefile, cfg)
    print(json.dumps(dict(prepared=True, state=str(state), runs=cfg['runs'], semantic_sha256=cfg['seed_inventory']['semantic_sha256'])))


def cleanup(state):
    cfg = json.loads((state / 'resources.json').read_text())
    logs = state / 'evidence'
    names = {cfg['postgres']}
    for folder in [logs] + [Path(run) / 'runtime-evidence' for run in cfg['runs']]:
        for receipt in folder.glob('container-*.json'):
            data = json.loads(receipt.read_text())
            if data['owner'] == cfg['owner']:
                names.add(data['name'])
    for name in sorted(names):
        remove_owned(name, 'container', cfg, logs)
    remove_owned(cfg['network'], 'network', cfg, logs)
    # Verify the owner's entire resource set, without deleting unknown names.
    _, out, _ = command(['docker', 'ps', '-aq', '--filter', 'label='+LABEL+'='+cfg['owner']], logs, 'verify-containers')
    _, networks, _ = command(['docker', 'network', 'ls', '-q', '--filter', 'label='+LABEL+'='+cfg['owner']], logs, 'verify-networks')
    verified = not out.strip() and not networks.strip()
    write_json(logs / 'cleanup.json', dict(verified=verified, remaining_containers=out.split(), remaining_networks=networks.split()))
    if not verified:
        raise RuntimeError('Cleanup incomplete; unregistered resources preserved')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path)
    subs = parser.add_subparsers(dest='action', required=True)
    prep = subs.add_parser('prepare-pair')
    for opt in ('seed-project', 'run-s', 'run-d', 'state'):
        prep.add_argument('--'+opt, type=Path, required=True)
    clean = subs.add_parser('cleanup')
    clean.add_argument('--state', type=Path, required=True)
    test = subs.add_parser('test')
    test.add_argument('--tags', default='/lab_qualification')
    test.add_argument('--expect', action='append')
    subs.add_parser('update')
    subs.add_parser('inventory')
    shell = subs.add_parser('shell')
    shell.add_argument('--script', type=Path)
    args = parser.parse_args()
    if args.action == 'prepare-pair':
        prepare(args)
        return 0
    if args.action == 'cleanup':
        cleanup(args.state.resolve())
        return 0
    if args.run is None:
        parser.error('--run required')
    run = args.run.resolve()
    cfg = json.loads((run / 'runtime.json').read_text())
    if Path(cfg['project']).resolve() != run / 'project' or not re.fullmatch(r'comparison_run_[01]', cfg['database']):
        parser.error('Run configuration does not designate its assigned project/database')
    logs = run / 'runtime-evidence'
    if args.action == 'inventory':
        print(json.dumps(inventory(cfg, logs)))
        return 0
    script = (args.script.read_text() if args.script else sys.stdin.read()) if args.action == 'shell' else None
    return odoo(cfg, args.action, logs, tags=getattr(args, 'tags', None), expected=getattr(args, 'expect', None), script=script)[0]


if __name__ == '__main__':
    raise SystemExit(main())
