#!/usr/bin/env python3
"""Explicit eight-call local implementation comparison; no calls in CI."""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time

from odoo_bench import digest, parse_output, provider_environment
from odoo_bench_native import sandbox, native_command, copy_project, source_hashes

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / 'benchmarks/qualification/implementation'
RECEIPT_CHECK = '''import json,sys
from pathlib import Path
sys.path.insert(0, str(Path.home()/'.odoo19-agents/scripts'))
from odoo_evidence import verify
p=json.loads(Path('/work/evidence.json').read_text())
verify(p, expected_project='/work', expected_environment='implementation-bench-v1')
assert p['command'] == ['python3','-m','unittest','discover','-s','.','-p','test_*.py','-v']
required={sys.argv[1], 'test_public.py'} | {str(x) for x in Path('.').glob('test_*.py')}
assert required <= set(p['sources']), ('missing coverage',required-set(p['sources']))
print('source-bound test receipt passed')
'''


def immutable_inputs(project, original):
    for name in ('CONTRACT.md', 'test_public.py'):
        path = project / name
        if path.is_symlink() or not path.is_file() or path.read_bytes() != (original / name).read_bytes():
            return False
    return True


def run_trial(folder, pack, cases, case, variant, timeout):
    folder.mkdir()
    project, home = folder / 'project', folder / 'home'
    copy_project(cases / case / 'project', project)
    home.mkdir()
    prompt = (cases / 'developer.md').read_text() + '\nLis CONTRACT.md puis réalise le travail maintenant. '
    prompt += 'Le helper de preuve est ~/.odoo19-agents/scripts/odoo_evidence.py. Aucun oracle ni corrigé ne t’est accessible.'
    (folder / 'prompt.txt').write_text(prompt)
    raw, stderr = folder / 'raw.jsonl', folder / 'stderr.log'
    started = time.monotonic()
    with raw.open('x') as out, stderr.open('x') as err:
        process = subprocess.Popen(sandbox(home, project, pack, provider=variant['provider']) + native_command(variant['provider'], variant),
                                   stdin=subprocess.PIPE, stdout=out, stderr=err, text=True,
                                   env=provider_environment(), start_new_session=True)
        try:
            process.communicate(prompt, timeout=timeout)
            transport = 'completed' if process.returncode == 0 else 'error'
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            transport = 'timeout'
    returned = time.monotonic()
    parsed = parse_output(raw, variant['provider'])
    (folder / 'answer.md').write_text(parsed['answer'])
    result = dict(variant, case=case, transport=transport, actual_model=parsed['actual_model'], actual_effort=parsed['actual_effort'],
                  tool_calls=parsed['tool_calls'], usage=parsed['usage'], provider_error=parsed['provider_error'],
                  return_seconds=round(returned-started, 3), principal_rework_seconds=None, rework_performed=False,
                  raw_sha256=digest(raw.read_bytes()), source_hashes=source_hashes(project))
    # Oracle runs after the agent has exited, in a separate sandbox without provider credentials.
    checks = [(['python3', '/oracle/oracle.py', '/work', case], 'oracle'),
              (['python3', '-c', RECEIPT_CHECK, 'scheduler.py' if case == 'I01' else 'quotas.py'], 'receipt')]
    good_transport = transport == 'completed' and parsed['completed_event'] and not parsed['provider_error']
    result['immutable_inputs_passed'] = immutable_inputs(project, cases / case / 'project')
    all_passed = good_transport and parsed['tool_calls'] > 0 and result['immutable_inputs_passed']
    for argv, label in checks:
        try:
            completed = subprocess.run(sandbox(home, project, pack) + ['--ro-bind', str(cases), '/oracle'] + argv,
                                       env=provider_environment(), capture_output=True, text=True, timeout=30)
            log = folder / (label + '.log')
            log.write_text(completed.stdout + completed.stderr)
            passed = completed.returncode == 0
        except subprocess.TimeoutExpired:
            passed = False
            (folder / (label + '.log')).write_text('independent reception timed out\n')
        result[label + '_passed'] = passed
        all_passed = all_passed and passed
    result.update(status=('accepted' if all_passed else 'rejected') if good_transport else 'transport_error',
                  reception_seconds=round(time.monotonic()-returned, 3),
                  total_to_reception_seconds=round(time.monotonic()-started, 3))
    (folder / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def campaign(output, pack, cases=DEFAULT_CASES):
    output, pack, cases = Path(output).resolve(), Path(pack).resolve(), Path(cases).resolve()
    output.mkdir(parents=True, exist_ok=False)
    protocol = json.loads((cases / 'protocol.json').read_text())
    if len(protocol['cases']) * len(protocol['variants']) > 8 or protocol['timeout_seconds'] > 600:
        raise ValueError('campaign exceeds eight calls / 600 seconds')
    frozen_cases = output / 'frozen-cases'
    copy_project(cases, frozen_cases)
    frozen_pack = output / 'frozen-pack'
    (frozen_pack / 'scripts').mkdir(parents=True)
    for filename in ('odoo_evidence.py', 'odoo_test_result.py'):
        shutil.copy2(pack / 'scripts' / filename, frozen_pack / 'scripts' / filename)
    state = {'scope': protocol['scope'], 'protocol': protocol, 'frozen_hashes': source_hashes(frozen_cases),
             'pack_hashes': source_hashes(frozen_pack), 'trials': [], 'status': 'running'}
    (output / 'state.json').write_text(json.dumps(state, indent=2))
    for index, case in enumerate(protocol['cases']):
        variants = protocol['variants'] if index % 2 == 0 else list(reversed(protocol['variants']))
        for variant in variants:
            identity = case + '-' + variant['provider'] + '-' + variant['kind']
            try:
                result = run_trial(output / identity, frozen_pack, frozen_cases, case, variant, protocol['timeout_seconds'])
            except Exception as exc:
                result = dict(variant, case=case, status='incident', error=str(exc))
            state['trials'].append(result)
            (output / 'state.json').write_text(json.dumps(state, indent=2) + '\n')
            print(json.dumps({k: result.get(k) for k in ('case', 'provider', 'kind', 'status', 'total_to_reception_seconds', 'error')}), flush=True)
    state['status'] = 'completed'
    (output / 'state.json').write_text(json.dumps(state, indent=2) + '\n')
    return state


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--pack', type=Path, default=ROOT)
    parser.add_argument('--cases', type=Path, default=DEFAULT_CASES)
    args = parser.parse_args()
    campaign(args.output, args.pack, args.cases)
