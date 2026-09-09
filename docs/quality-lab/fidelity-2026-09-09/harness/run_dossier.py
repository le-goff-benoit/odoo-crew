#!/usr/bin/env python3
"""Bounded native-CLI documentary reception; no Odoo/DB bridge."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path('/home/blegoff/.odoo19-agents')
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'scripts'))
from odoo_bench_native import copy_project, sandbox, native_command, execute, provider_environment, source_hashes, native_delegation_summary
from odoo_bench import atomic_json, parse_output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job')
    args = parser.parse_args()
    case, variant = args.job.split('-', 1)
    if case not in ('F01', 'F02', 'F03', 'F04', 'F05') or variant not in ('reference', 'candidate'):
        parser.error('expected F01..F05-reference|candidate')
    protocol = json.loads((BASE / 'protocol.json').read_text())
    limits = protocol['limits']['dossiers']
    config = {'model': protocol['model'], 'effort': protocol['effort'], 'delegate': protocol['delegation']}
    pack = BASE / variant
    if not pack.is_dir():
        raise ValueError(f'Frozen pack absent: {pack}')
    source = BASE / 'cases' / case
    expected = json.loads((source / 'input-sha256.json').read_text())
    if source_hashes(source / 'project') != expected:
        raise ValueError('Frozen case no longer matches its manifest')
    folder = BASE / args.job
    folder.mkdir()
    folder.chmod(0o700)
    home = folder / 'home'
    home.mkdir()
    project = folder / 'project'
    copy_project(source / 'project', project)
    before = source_hashes(project)
    atomic_json(folder / 'input-hashes.json', before)
    prompt = (source / 'prompt.txt').read_text()
    (folder / 'prompt.txt').write_text(prompt)
    state = {'job': args.job, 'case': case, 'variant': variant, 'provider': protocol['provider'],
             'config': config, 'limits': limits, 'mode': 'documentary_reception_no_new_odoo',
             'protocol_sha256': hashlib.sha256((BASE / 'protocol.json').read_bytes()).hexdigest(),
             'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
             'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'status': 'building', 'reference': protocol['reference']}
    atomic_json(folder / 'state.json', state)
    # The exact pack generates profiles in this trial's empty home. Inputs stay
    # unchanged; no initial Git commit is invented for the archived project.
    built = execute(sandbox(home, project, pack) + ['bash', '/home/blegoff/.odoo19-agents/build.sh'], env=provider_environment())
    (folder / 'build.log').write_text(built.stdout)
    if built.returncode:
        state.update(status='incident', error='isolated build failed', build_returncode=built.returncode)
        atomic_json(folder / 'state.json', state)
        return
    if source_hashes(project) != before:
        raise ValueError('Build changed archived inputs')
    state.update(status='running', started_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    atomic_json(folder / 'state.json', state)
    raw, errors = folder / 'raw.jsonl', folder / 'stderr.log'
    started = time.monotonic()
    command = sandbox(home, project, pack, provider='claude') + native_command('claude', config)
    command += ['--max-budget-usd', str(limits['max_budget_usd'])]
    with raw.open('w') as out, errors.open('w') as err:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=out, stderr=err,
                                   text=True, env=provider_environment(), start_new_session=True)
        state['pid'] = process.pid
        atomic_json(folder / 'state.json', state)
        try:
            process.communicate(prompt, timeout=limits['seconds'])
            status = 'completed' if process.returncode == 0 else 'error'
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            status = 'timeout'
    raw.chmod(0o600)
    errors.chmod(0o600)
    parsed = parse_output(raw, 'claude')
    (folder / 'answer.md').write_text(parsed['answer'])
    atomic_json(folder / 'parsed.json', parsed)
    atomic_json(folder / 'usage.json', parsed['usage'])
    delegation = native_delegation_summary(raw, 'claude')
    atomic_json(folder / 'delegation.json', delegation)
    after = source_hashes(project)
    atomic_json(folder / 'output-hashes.json', after)
    changed = [name for name, value in before.items() if after.get(name) != value]
    reception = project / 'reception.md'
    if reception.is_file():
        (folder / 'reception.md').write_bytes(reception.read_bytes())
    copy_project(project, folder / 'after')
    state.update(status='executed' if status == 'completed' and parsed['completed_event'] and not parsed['provider_error'] else 'incident',
                 process_status=status, returncode=process.returncode,
                 seconds=round(time.monotonic() - started, 2), usage=parsed['usage'],
                 actual_model=parsed['actual_model'], requested_effort=config['effort'],
                 actual_effort=None, provider_completed=parsed['completed_event'],
                 provider_error=parsed['provider_error'], tool_calls=parsed['tool_calls'],
                 delegation=delegation, input_files_changed=changed,
                 input_files_unchanged=not changed, new_files=sorted(set(after)-set(before)),
                 reception_exists=reception.is_file(),
                 answer_sha256=hashlib.sha256(parsed['answer'].encode()).hexdigest(),
                 semantic_verdict=None)
    atomic_json(folder / 'state.json', state)
    print(json.dumps({k: state[k] for k in ('job', 'status', 'seconds', 'usage', 'delegation', 'input_files_changed', 'reception_exists')}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
