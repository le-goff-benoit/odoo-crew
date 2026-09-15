#!/usr/bin/env python3
"""Explicit bounded comparison. No calls during ordinary tests or generation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from odoo_bench import parse_output, provider_command

EXPECTED = {
    'local': {'ready_tasks': ['B'], 'principal_model_changed': False, 'tests': ['lint', 'rendu'], 'received_A': False},
    'holdout': {'ready_tasks': ['F'], 'received_D': False, 'invalidate_F': False, 'next_action': 'examine_result'},
}


def judge(answer, case):
    value = answer.strip()
    if value.startswith('```'):
        value = '\n'.join(value.splitlines()[1:-1])
    try:
        data = json.loads(value)
        return all((sorted(data.get(key)) == sorted(expected) if isinstance(expected, list) and isinstance(data.get(key), list)
                    else type(data.get(key)) is type(expected) and data.get(key) == expected)
                   for key, expected in EXPECTED[case].items())
    except (TypeError, ValueError):
        return False


def run(output):
    raw = (Path(__file__).parent / 'protocol.json').read_bytes()
    protocol = json.loads(raw)
    output.mkdir(parents=True, exist_ok=False)
    output.chmod(0o700)
    (output / 'protocol.json').write_bytes(raw)
    # Synthetic context only. No user/project instruction files or CLI tools.
    scratch = output / 'workspace'
    scratch.mkdir()
    results = []
    unavailable = set()
    for case in protocol['cases']:
        for variant in protocol['variants']:
            row = dict(variant, case=case['id'], actual_model=None, actual_effort=None,
                       principal_rework_seconds=0, corrections=0)
            results.append(row)
            provider = variant['provider']
            if provider in unavailable:
                row.update(status='not_run', reason='provider_unavailable')
                continue
            binary = shutil.which(provider)
            if not binary:
                row.update(status='unavailable', reason='cli_missing')
                unavailable.add(provider)
                continue
            args = provider_command(provider, variant)
            args[0] = binary
            filename = case['id'] + '-' + provider + '-' + variant['kind']
            stdout = output / (filename + '.jsonl')
            start = time.monotonic()
            with stdout.open('w') as out, (output / (filename + '.stderr')).open('w') as err:
                process = subprocess.Popen(args, cwd=scratch, stdin=subprocess.PIPE, stdout=out, stderr=err,
                                           start_new_session=True)
                try:
                    process.communicate(case['prompt'].encode(), timeout=protocol['timeout_seconds'])
                    parsed = parse_output(stdout, provider)
                    # No transport retry and no evidence inferred from an exit code alone.
                    good_transport = process.returncode == 0 and parsed['completed_event'] and not parsed['provider_error']
                    row.update(status=('accepted' if judge(parsed['answer'], case['id']) else 'critical_failure')
                               if good_transport else 'transport_error',
                               actual_model=parsed['actual_model'], usage=parsed['usage'], tool_calls=parsed['tool_calls'])
                    if not good_transport:
                        unavailable.add(provider)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                    row.update(status='timeout')
                    unavailable.add(provider)
            row['elapsed_seconds'] = round(time.monotonic() - start, 3)
            row['answer_sha256'] = hashlib.sha256(stdout.read_bytes()).hexdigest()
            print(json.dumps({k: row.get(k) for k in ('provider','model','case','status','elapsed_seconds')}, ensure_ascii=False), flush=True)
            (output / 'results.json').write_text(json.dumps({'protocol_sha256': hashlib.sha256(raw).hexdigest(), 'trials': results}, indent=2))
    (output / 'results.json').write_text(json.dumps({'protocol_sha256': hashlib.sha256(raw).hexdigest(), 'trials': results}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', required=True, help='Lancement explicite de huit appels au maximum')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.output.resolve())
