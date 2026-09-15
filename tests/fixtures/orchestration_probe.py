#!/usr/bin/env python3
"""Prepare/run a bounded native hook probe; synthetic flow completion, no Odoo DB.

Prepare: python3 THIS_FILE prepare /tmp/new-probe
Run from native agent: python3 THIS_FILE run /tmp/new-probe A
The fixture deliberately bypasses Odoo node execution, not plan receipts: each task
launches a real Python assertion subprocess and seals its immutable proof. It tests
native continuation/receipt order only, never claims Odoo workflow qualification.
"""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
# The file is in tests/fixtures: parents[2] is Crew's root.
import odoo_evidence as evidence
import odoo_flow as flow
import odoo_plan as plan


def prepare(root):
    root.mkdir(parents=True, exist_ok=False)
    release = root / 'changelog/probe'; release.mkdir(parents=True)
    (release / 'README.md').write_text('# Native continuation probe\n')
    (root / 'request.md').write_text('A: value 1\nB: value 2 after A\nC: value 3 after B\n')
    tasks = []
    for index, identifier in enumerate('ABC', 1):
        (root / identifier).mkdir()
        (root / identifier / 'code.py').write_text('value = ' + str(index) + '\n')
        tasks.append({'id': identifier, 'title': 'Assert value ' + str(index), 'request': 'request.md',
                      'route': 'module', 'risk': 'normal', 'acceptance': ['value equals ' + str(index)],
                      'scopes': [identifier], 'depends_on': [] if index == 1 else ['ABC'[index - 2]]})
    plan.initialise(release, {'schema': 1, 'tasks': tasks})
    print(release)


def run(root, identifier):
    if identifier not in 'ABC' or len(identifier) != 1:
        raise ValueError('A/B/C only')
    release = root / 'changelog/probe'
    snapshot = Path(plan.mutate(release, 'start', identifier))
    log = root / 'launches.jsonl'
    with log.open('a') as stream:
        stream.write(json.dumps({'task': identifier, 'event': 'started', 'at': flow.now()}) + '\n')
    index = 'ABC'.index(identifier) + 1
    result = evidence.execute(root, [identifier], release / (identifier + '-proof.json'),
        [sys.executable, '-c', "from pathlib import Path; scope = {}; code = {{}}; exec(Path(scope, 'code.py').read_text(), code); assert code['value'] == {}".format(repr(identifier), index)])
    if result['result'] != 'passed':
        raise ValueError('probe assertion failed')
    state = json.loads(snapshot.read_text()); state['status'] = 'complete'
    state['probe_only'] = 'synthetic flow completion; only receipt+native continuation qualified'
    flow.write_state(snapshot, state)
    for suffix in ('acceptance', 'memory'):
        (release / (identifier + '-' + suffix + '.md')).write_text('Probe ' + identifier + ': assertion passed; no business decision.\n')
    plan.mutate(release, 'finish', identifier, proof='changelog/probe/' + identifier + '-proof.json',
                acceptance='changelog/probe/' + identifier + '-acceptance.md', memory='changelog/probe/' + identifier + '-memory.md')
    with log.open('a') as stream:
        stream.write(json.dumps({'task': identifier, 'event': 'received', 'at': flow.now()}) + '\n')
    print(identifier + ' launched, asserted and received')


if __name__ == '__main__':
    root = Path(sys.argv[2]).resolve()
    if sys.argv[1] == 'prepare': prepare(root)
    elif sys.argv[1] == 'run': run(root, sys.argv[3])
    else: raise SystemExit('prepare|run required')
