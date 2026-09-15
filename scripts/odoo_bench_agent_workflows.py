#!/usr/bin/env python3
"""Explicit staged reference → correction → holdout campaign (eight native calls)."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import fcntl
import json
from pathlib import Path

from odoo_bench import atomic_json, now
import odoo_bench_native as native

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'docs/quality-lab/agent-workflows-2026-09-15/protocol.json'


def jobs_for(phase):
    if phase == 'baseline':
        return [('N06', p, 'reference') for p in ('codex', 'claude')]
    return [('N06', p, 'candidate') for p in ('codex', 'claude')] + [
        ('N07', p, label) for p in ('codex', 'claude')
        for label in (('reference', 'candidate') if p == 'codex' else ('candidate', 'reference'))]


def run(output, phase, candidate=None):
    output = Path(output).resolve()
    if phase == 'baseline':
        output.mkdir(parents=True, exist_ok=False)
    if not output.is_dir():
        raise ValueError('baseline campaign absent')
    with (output / '.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        statefile = output / 'campaign.json'
        if phase == 'baseline':
            protocol = json.loads(PROTOCOL.read_text())
            reference = native.export_revision(protocol['baseline'], output / 'packs/reference')
            corpus = output / 'frozen/benchmarks/native'
            corpus.mkdir(parents=True)
            for name in ('cases', 'oracles'):
                native.copy_project(ROOT / 'benchmarks/native' / name, corpus / name)
            state = {'created_at': now(), 'protocol': protocol, 'reference': reference,
                     'phases': {}, 'trials': {}, 'corpus_hashes': native.source_hashes(corpus),
                     'runner_hashes': {p.name: native.digest(p.read_bytes()) for p in
                                       (Path(__file__), ROOT / 'scripts/odoo_bench_native.py',
                                        ROOT / 'scripts/odoo_bench.py', ROOT / 'scripts/odoo_test_result.py')}}
        else:
            state = json.loads(statefile.read_text())
            protocol = state['protocol']
            if state['phases'].get('baseline') != 'completed' or not candidate:
                raise ValueError('completed baseline and explicit candidate revision required')
            if phase in state['phases']:
                raise ValueError('phase already started; preserve incident, no hidden retry')
            state['candidate'] = native.export_revision(candidate, output / 'packs/candidate')
        corpus = output / 'frozen/benchmarks/native'
        if native.source_hashes(corpus) != state['corpus_hashes']:
            raise ValueError('frozen corpus changed')
        for name, digest in state['runner_hashes'].items():
            if native.digest((ROOT / 'scripts' / name).read_bytes()) != digest:
                raise ValueError('runner changed: ' + name)
        jobs = jobs_for(phase)
        if len(state['trials']) + len(jobs) > protocol['max_native_calls']:
            raise ValueError('native call cap exceeded')
        for case, provider, label in jobs:
            identifier = f'{case}-{provider}-{label}'
            state['trials'][identifier] = {'status': 'reserved'}
        state['phases'][phase] = 'started'
        atomic_json(statefile, state)
        # Only fixture and oracle lookups use ROOT during trial; exported packs stay fixed.
        native.ROOT = output / 'frozen'
        def trial(job):
            case, provider, label = job
            identifier = f'{case}-{provider}-{label}'
            specification = json.loads((corpus / 'cases' / case / 'case.json').read_text())
            result = native.trial(output / identifier, output / 'packs' / label, specification,
                                  provider, protocol['config'][provider], protocol['timeout_per_call_seconds'])
            return identifier, result
        with ThreadPoolExecutor(max_workers=protocol['max_parallel_trials']) as pool:
            for identifier, result in pool.map(trial, jobs):
                state['trials'][identifier] = result
                atomic_json(statefile, state)
        state['phases'][phase] = 'completed'
        atomic_json(statefile, state)
    return state


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['baseline', 'candidate', 'status'])
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--candidate')
    args = parser.parse_args()
    if args.phase == 'status':
        state = json.loads((args.output / 'campaign.json').read_text())
        print(json.dumps({'phases': state['phases'], 'trials': {
            k: {'status': v['status'], 'runtime_gate': v.get('reception', {}).get('passed'),
                'agent_seconds': v.get('agent_seconds')} for k, v in state['trials'].items()}}, indent=2))
    else:
        run(args.output, args.phase, args.candidate)
