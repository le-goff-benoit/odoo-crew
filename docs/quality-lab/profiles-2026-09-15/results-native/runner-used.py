#!/usr/bin/env python3
"""Explicit eight-call documentary profile comparison; no native calls in tests."""
import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import signal
import socketserver
import subprocess
import sys
import threading
import tempfile
import time

from odoo_bench_native import (CLIENT, HOME_PATH, ROOT, atomic_json, digest, export_revision,
                               native_command, parse_output, provider_environment, sandbox,
                               source_hashes)

CORPUS = ROOT / 'benchmarks/qualification/profiles'


def judge(value, expected, inputs):
    """Structural facts + exact source citations; final semantic review stays separate."""
    problems = []
    if not isinstance(value, dict):
        return ['résultat JSON absent']
    for key in ('decision', 'axes', 'local_scope_received', 'deployment_verified', 'prior_memory_preserved'):
        if type(value.get(key)) is not type(expected[key]) or value.get(key) != expected[key]:
            problems.append('conclusion incorrecte : ' + key)
    observed = value.get('preserved_observations')
    if not isinstance(observed, list) or sorted(observed) != sorted(expected['preserved_observations']):
        problems.append('observations reçues perdues ou inventées')
    axes = set()
    for finding in value.get('findings', []):
        if not isinstance(finding, dict) or not finding.get('explanation'):
            problems.append('argumentation absente'); continue
        refs = finding.get('references', [])
        if len(refs) < 2:
            problems.append('citations des deux côtés absentes')
        good = True
        for ref in refs:
            name, quote = ref.get('file'), ref.get('quote')
            if name not in inputs or not isinstance(quote, str) or len(quote.strip()) < 12 or quote not in inputs[name]:
                problems.append('citation non étayée'); good = False
        if refs and good:
            axes.add(finding.get('axis'))
    if not {'request_contract', 'contract_evidence', 'source_memory'} <= axes:
        problems.append('axes argumentés incomplets')
    if not isinstance(value.get('limitations'), str) or not value['limitations'].strip():
        problems.append('limites non déclarées')
    return problems


def read_result(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def snapshot_candidate(source, target):
    """Only repository tooling, never personal configuration or client paths."""
    target.mkdir(parents=True)
    for name in ('roles', 'scripts', 'docs', 'workflows', 'tests', 'benchmarks'):
        def ignore(directory, names):
            return [n for n in names if n in ('__pycache__', 'quality-lab', 'runs') or n.endswith('.pyc')]
        shutil.copytree(source / name, target / name, ignore=ignore)
    for name in ('build.sh', 'AGENTS.md'):
        shutil.copy2(source / name, target / name)


class SourceServer(socketserver.UnixStreamServer):
    def __init__(self, socket, home, workspace, pack, audit):
        self.home, self.workspace, self.pack, self.audit = home, workspace, pack, audit
        super().__init__(socket, SourceHandler)

    def read_source(self, name):
        aliases = [('/work/input/', self.workspace / 'input'),
                   (str(HOME_PATH / '.odoo19-agents/docs') + '/', self.pack / 'docs'),
                   (str(HOME_PATH / '.odoo19-agents/roles') + '/', self.pack / 'roles'),
                   (str(HOME_PATH / '.codex/skills') + '/', self.home / '.codex/skills'),
                   (str(HOME_PATH / '.claude/agents') + '/', self.home / '.claude/agents')]
        if name.startswith('~/'):
            name = str(HOME_PATH) + name[1:]
        for prefix, root in aliases:
            if name.startswith(prefix):
                target = (root / name[len(prefix):]).resolve()
                if not target.is_relative_to(root.resolve()) or not target.is_file():
                    raise ValueError('source hors dossier ou absente')
                text = target.read_text()
                event = {'path': name, 'characters': len(text), 'sha256': digest(text.encode()), 'at': time.time()}
                with self.audit.open('a') as stream:
                    stream.write(json.dumps(event) + '\n')
                return text
        raise ValueError('source hors des profils, références ou pièces autorisés')


class SourceHandler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            args = json.loads(self.rfile.readline(65536))['args']
            if len(args) != 1:
                raise ValueError('un chemin requis')
            result = {'exit_code': 0, 'output': self.server.read_source(args[0])}
        except Exception as exc:
            result = {'exit_code': 2, 'output': str(exc) + '\n'}
        self.wfile.write(json.dumps(result).encode())


def run_trial(folder, pack, generated, case, request, expected, provider, config, timeout):
    folder.mkdir()
    work, home = folder / 'work', folder / 'home'
    bridge = Path(tempfile.mkdtemp(prefix='profiles-bridge-'))
    work.mkdir(); shutil.copytree(generated, home)
    shutil.copytree(case / 'input', work / 'input')
    (bridge / 'read-source').write_text(CLIENT)
    (bridge / 'read-source').chmod(0o755)
    # Reader keeps audit and oracles outside the provider's mounted workspace.
    audit = folder / 'reads.jsonl'
    server = SourceServer(str(bridge / 'control.sock'), home, work, pack, audit)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    entrypoint = HOME_PATH / ('.codex/skills/odoo-tester/SKILL.md' if provider == 'codex' else '.claude/agents/odoo-tester.md')
    prompt = request + '\nProfil généré à lire : ' + str(entrypoint) + '\nLe projet /work est entièrement synthétique, série19.0. Aucun projet client accessible.'
    (folder / 'prompt.txt').write_text(prompt)
    before = source_hashes(work)
    started = time.monotonic()
    outcome = 'completed'
    try:
        with (folder / 'raw.jsonl').open('w') as out, (folder / 'stderr.log').open('w') as err:
            process = subprocess.Popen(sandbox(home, work, pack, bridge, provider) + native_command(provider, config),
                                       stdin=subprocess.PIPE, stdout=out, stderr=err, text=True,
                                       env=provider_environment(), start_new_session=True)
            try:
                process.communicate(prompt, timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL); process.wait(); outcome = 'timeout'
        parsed = parse_output(folder / 'raw.jsonl', provider)
    finally:
        server.shutdown(); server.server_close(); thread.join()
        shutil.rmtree(bridge)
    (folder / 'answer.md').write_text(parsed['answer'])
    value = read_result(work / 'reception.json')
    inputs = {p.name: p.read_text() for p in (case / 'input').glob('*.md')}
    problems = judge(value, expected, inputs)
    after = source_hashes(work)
    if {k: v for k, v in after.items() if k != 'reception.json'} != before:
        problems.append('fichiers hors mandat modifiés')
    reads = [json.loads(line) for line in audit.read_text().splitlines()] if audit.exists() else []
    observed = {r['path'] for r in reads}
    if str(entrypoint) not in observed:
        problems.append('profil généré non lu via instrument')
    if not all('/work/input/' + name in observed for name in inputs):
        problems.append('pièces originales non lues via instrument')
    transport_ok = outcome == 'completed' and process.returncode == 0 and parsed['completed_event'] and not parsed['provider_error']
    state = {'provider': provider, 'case': case.name, 'config': config, 'seconds': round(time.monotonic()-started, 3),
             'transport': 'completed' if transport_ok else outcome if outcome != 'completed' else 'error',
             'exit_code': process.returncode, 'usage': parsed['usage'], 'actual_model': parsed['actual_model'],
             'actual_effort': parsed['actual_effort'], 'tool_calls': parsed['tool_calls'],
             'problems': problems, 'status': 'needs_semantic_review' if transport_ok and not problems else 'failed',
             'reading': {'calls': len(reads), 'total_characters_returned': sum(r['characters'] for r in reads),
                         'entrypoint_characters_returned': sum(r['characters'] for r in reads if r['path'] == str(entrypoint)),
                         'references_characters_returned': sum(r['characters'] for r in reads if '/.odoo19-agents/' in r['path']),
                         'unique_sources': len(observed), 'entrypoint': str(entrypoint)},
             'result_sha256': digest((work/'reception.json').read_bytes()) if (work/'reception.json').exists() else None,
             'semantic_review': None}
    atomic_json(folder / 'result.json', state)
    print(json.dumps({'trial': folder.name, **state}, ensure_ascii=False), flush=True)
    return state


def run(output, corpus, candidate, baseline, timeout):
    if output.exists() or not 1 <= timeout <= 600:
        raise ValueError('nouveau dossier requis et timeout1–600')
    output.mkdir(parents=True)
    cases = json.loads((corpus / 'cases.json').read_text())
    oracles = json.loads((corpus / 'oracles.json').read_text())
    if cases['cases'] != ['positive', 'holdout']:
        raise ValueError('deux cas prescrits requis pour budget8')
    packs = output / 'packs'; packs.mkdir()
    export_revision(baseline, packs / 'reference')
    snapshot_candidate(candidate, packs / 'candidate')
    frozen = {'created_at': time.time(), 'baseline': baseline, 'max_calls': 8, 'timeout': timeout,
              'runner_sha256': digest(Path(__file__).read_bytes()), 'corpus': source_hashes(corpus),
              'packs': {label: source_hashes(packs / label) for label in ('reference', 'candidate')},
              'config': {'codex': {'model': 'gpt-6-astra', 'effort': 'medium'}, 'claude': {'model': 'opus', 'effort': 'medium'}}}
    atomic_json(output / 'frozen.json', frozen)
    shutil.copytree(corpus, output / 'frozen-corpus')
    generated = output / 'generated'; generated.mkdir()
    for label in ('reference', 'candidate'):
        target = generated / label
        # Native profiles are generated by the unmodified build of each revision.
        built = subprocess.run(['bash', str(packs / label / 'build.sh'), '--output-root', str(target)],
                               cwd=packs / label, text=True, capture_output=True)
        (output / ('build-' + label + '.log')).write_text(built.stdout + built.stderr)
        if built.returncode:
            raise ValueError('génération échouée : ' + label)
    results = []
    # Sequential locally: another independent campaign may use the second slot.
    for case in cases['cases']:
        for provider in ('codex', 'claude'):
            order = ('reference', 'candidate') if provider == 'codex' else ('candidate', 'reference')
            for label in order:
                identifier = '-'.join((case, provider, label))
                result = run_trial(output / identifier, packs / label, generated / label,
                                   output / 'frozen-corpus/cases' / case, cases['request'], oracles[case],
                                   provider, frozen['config'][provider], timeout)
                results.append(dict(result, variant=label, id=identifier))
                atomic_json(output / 'results.json', {'trials': results, 'native_calls': len(results), 'frozen_sha256': digest((output/'frozen.json').read_bytes())})
                if result['transport'] != 'completed':
                    raise ValueError('incident natif ; arrêter avant tout autre appel et coordonner')
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--corpus', type=Path, default=CORPUS)
    parser.add_argument('--candidate', type=Path, default=ROOT)
    parser.add_argument('--baseline', default='4c6738c60c959fd1ceac7d24d6949d96909b6ab2')
    parser.add_argument('--timeout', type=int, default=600)
    args = parser.parse_args()
    try:
        run(args.output.resolve(), args.corpus.resolve(), args.candidate.resolve(), args.baseline, args.timeout)
    except (ValueError, OSError) as exc:
        sys.exit(str(exc))
