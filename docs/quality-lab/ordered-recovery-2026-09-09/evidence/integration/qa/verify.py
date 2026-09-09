#!/usr/bin/env python3
"""Independent review verification; only reads databases and existing evidence.

Does not run Odoo tests or lint. Their original executions are explicitly reused.
All newly written artifacts stay in this qa directory.
"""
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

QA = Path(__file__).resolve().parent
ROOT = QA.parent
PROJECT = ROOT / 'run/project'
MODULE = PROJECT / 'lab_qualification'
DEV = ROOT / 'developer'
checks = []
references = {}


def check(condition, name):
    checks.append({'check': name, 'pass': bool(condition)})
    if not condition:
        raise AssertionError(name)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reference(path):
    references[str(path)] = digest(path)
    return path


def read_json(path):
    return json.loads(reference(path).read_text())


def command(name, args):
    start = time.monotonic()
    result = subprocess.run(args, text=True, capture_output=True, timeout=60)
    log = QA / (name + '.log')
    log.write_text(result.stdout + result.stderr)
    meta = {'command': args, 'returncode': result.returncode,
            'seconds': round(time.monotonic() - start, 3), 'log': str(log)}
    (QA / (name + '.command.json')).write_text(json.dumps(meta, indent=2) + '\n')
    print(json.dumps(meta), flush=True)
    check(result.returncode == 0, name + ' exit zero')
    reference(log)
    reference(QA / (name + '.command.json'))
    return result.stdout


final = read_json(DEV / 'green/final-hashes.json')
initial = read_json(DEV / 'red/initial-hashes.json')
red_tests = read_json(DEV / 'red/test-hashes.json')
bootstrap = read_json(ROOT / 'evidence/bootstrap-result.json')
live_hashes = {str(p.relative_to(MODULE)): digest(p) for p in MODULE.rglob('*')
               if p.is_file() and '__pycache__' not in p.parts}
check(live_hashes == final, 'complete live module file set and hashes equal tested green snapshot')
for filename, sha in final.items():
    check(digest(DEV / 'green/module' / filename) == sha, 'green archive ' + filename)
for filename, sha in initial.items():
    check(digest(DEV / 'red/initial-module' / filename) == sha, 'initial archive ' + filename)
    check(bootstrap['initial_module_hashes']['lab_qualification/' + filename] == sha,
          'initial archive equals bootstrap ' + filename)
for filename, sha in red_tests.items():
    check(digest(DEV / 'red' / filename) == sha == final[filename], 'same red/green test bytes ' + filename)
for filename in ('__init__.py', '__manifest__.py', 'views/quantity.xml',
                 'security/ir.model.access.csv', 'tests/test_quantity.py', 'tests/test_browser.py'):
    check(initial[filename] == final[filename], 'preserved existing file ' + filename)
current_diff = command('reviewed-module-diff', ['git', '-C', str(PROJECT), 'diff', 'HEAD', '--', 'lab_qualification'])
check(current_diff == reference(DEV / 'module.diff').read_text(), 'reviewed diff equals developer archived diff')
lint = reference(DEV / 'lint.log').read_text()
check('Périmètre --changed (HEAD) : 4 fichier(s)' in lint and '0 erreur(s), 0 avertissement(s)' in lint
      and 'lint OK' in lint and 'Série cible : 19.0' in lint, 'reused changed lint reports success on target series')
contract = PROJECT / 'changelog/2026-09-09_01_quantite-positive-a-la-confirmation/revue_fonctionnelle.md'
criteria = read_json(contract.parent / 'criteria.json')
sys.path.insert(0, str(ROOT.parent / 'reference/scripts'))
from odoo_coverage import contract as read_contract
bound_contract = read_contract(PROJECT, str(contract.relative_to(PROJECT)))
check(bound_contract['sha256'] == criteria['contract_sha256'], 'contract unchanged from bound criteria')
reference(contract)
reference(contract.parent / 'demande.md')
reference(contract.parent / 'consolidation-contrat.md')

executions = {}
for phase, basename, expected in (
    ('red', 'test-ordered_copy-20260909-190409-e2e7801f', (8, 0, 20)),
    ('green', 'test-ordered_copy-20260909-190501-1a622b24', (0, 0, 20)),
):
    path = DEV / phase / basename
    metadata = read_json(path.with_suffix('.json'))
    parsed = read_json(path.with_suffix('.tests.json'))
    log = reference(path.with_suffix('.log')).read_text()
    check(digest(Path(metadata['log'])) == digest(path.with_suffix('.log')), phase + ' copied log equals runtime original')
    reference(Path(metadata['log']))
    summaries = [tuple(map(int, match)) for match in re.findall(r'(\d+) failed, (\d+) error\(s\) of (\d+) tests', log)]
    names = re.findall(r'Starting (Test\w+\.test_\w+)', log)
    check(summaries == [expected], phase + ' original Odoo result summary')
    check(len(names) == len(set(names)) == 20 and names == parsed['started_tests'], phase + ' 20 distinct actual started test names')
    check([list(item) for item in summaries] == parsed['summaries'], phase + ' archived parser matches original log')
    check(metadata['command'][metadata['command'].index('-d') + 1] == 'ordered_copy', phase + ' tested only copy')
    check('-u' in metadata['command'] and 'creating or updating database tables' in log, phase + ' real module update')
    check('WARNING' not in log and 'invalid module names' not in log, phase + ' no warnings or ignored module')
    failures = re.findall(r'FAIL: (Test\w+\.test_\w+)', log)
    check(len(failures) == expected[0], phase + ' counted real failed cases')
    executions[phase] = {'reuse_only': True, 'new_qa_test_execution': False,
                         'original_metadata': str(path.with_suffix('.json')),
                         'original_log': str(path.with_suffix('.log')),
                         'summary_from_original_log': summaries,
                         'started_tests_from_original_log': names,
                         'failed_cases_from_original_log': failures,
                         'original_seconds': metadata['seconds']}
check(executions['red']['started_tests_from_original_log'] == executions['green']['started_tests_from_original_log'],
      'identical actual red/green test selection')

# Live state inspection uses the actual PostgreSQL psql, no Python substitute.
# READ ONLY is enforced by PostgreSQL for each entire transaction, including seed.
resources = read_json(ROOT / 'resources.json')
container = json.loads(command('live-container', ['docker', 'container', 'inspect', resources['postgres']]))[0]
check(container['State']['Running'], 'registered PostgreSQL is running')
check(container['Config']['Labels']['ordered-recovery-owner'] == resources['owner'], 'PostgreSQL ownership label')
check(container['Image'] == resources['images']['postgres:16']['id'], 'same PostgreSQL immutable image')
image = json.loads(command('live-odoo-image', ['docker', 'image', 'inspect', resources['images']['odoo-qa:19.0']['id']]))[0]
check(image['Id'] == resources['images']['odoo-qa:19.0']['id'], 'same immutable Odoo image available')
for phase in ('red', 'green'):
    metadata = json.loads(Path(executions[phase]['original_metadata']).read_text())
    check(image['Id'] in metadata['command'], phase + ' execution used same immutable Odoo image')

sql = """BEGIN READ ONLY;
SELECT json_build_object(
 'database', current_database(),
 'read_only', current_setting('transaction_read_only'),
 'records', (SELECT json_agg(t ORDER BY id) FROM
   (SELECT id,name,state,quantity,unit_price,amount FROM lab_qualification ORDER BY id) t),
 'module', (SELECT json_agg(t) FROM
   (SELECT id,name,state,latest_version FROM ir_module_module WHERE name='lab_qualification') t),
 'constraints', (SELECT json_agg(t ORDER BY conname) FROM
   (SELECT conname,pg_get_constraintdef(oid) AS definition,convalidated
    FROM pg_constraint WHERE conrelid='lab_qualification'::regclass) t),
 'invalid_confirmed_count', (SELECT count(*) FROM lab_qualification WHERE state='confirmed' AND COALESCE(quantity,0)<=0)
);
ROLLBACK;"""
(QA / 'inventory-readonly.sql').write_text(sql + '\n')
observations = {}
for db, baseline_name in (
    ('ordered_copy', 'inventory-ordered_copy-20260909-183801-79429f03.inventory.json'),
    ('ordered_seed', 'inventory-ordered_seed-20260909-183759-07173621.inventory.json'),
):
    output = command('live-' + db, ['docker', 'exec', resources['postgres'], 'psql', '-U', 'odoo',
                     '-d', db, '-X', '-q', '-t', '-A', '-v', 'ON_ERROR_STOP=1', '-c', sql])
    live = json.loads(output)
    baseline = read_json(ROOT / 'evidence' / baseline_name)
    check(live['database'] == db and live['read_only'] == 'on', db + ' actual target and enforced read-only')
    check(live['records'] == baseline['records'], db + ' all original identities and business values preserved')
    check([r['id'] for r in live['records']] == [1, 2, 3], db + ' exactly three original records')
    check(live['module'][0]['state'] == 'installed' and live['module'][0]['id'] == baseline['module'][0]['id'], db + ' module installed identity retained')
    check(live['module'][0]['latest_version'] == '19.0.1.0.0', db + ' stored version')
    constraints = {item['conname']: item for item in live['constraints']}
    check('lab_qualification_quantity_nonnegative' in constraints, db + ' initial nonnegative constraint remains')
    check(('lab_qualification_confirmed_quantity_positive' in constraints) == (db == 'ordered_copy'), db + ' new constraint copy only')
    check(all(item['convalidated'] for item in live['constraints']), db + ' effective validated constraints')
    check(live['invalid_confirmed_count'] == 0, db + ' no invalid confirmed history')
    observations[db] = live
check(live_hashes == {str(p.relative_to(MODULE)): digest(p) for p in MODULE.rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts}, 'module stable during independent verification')
result = {'kind': 'independent QA verification; not an Odoo test run', 'module': 'lab_qualification',
          'series': '19.0', 'mode': 'task', 'checks': checks, 'references_sha256': references,
          'verified_live_module_sha256': live_hashes, 'reused_developer_executions': executions,
          'fresh_live_observations': observations, 'new_odoo_test_runs': 0,
          'new_lint_runs': 0, 'database_writes': 0,
          'pending_after_qa': ['independent documentary reception', 'memory publication', 'flow completion', 'plan reception'],
          'limitations': ['synthetic copy, not customer restore', 'no browser', 'no release certification', 'no invalid historical fixture']}
(QA / 'verification.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
print('QA_VERIFICATION_OK ' + json.dumps({'checks': len(checks), 'new_odoo_tests': 0, 'read_only_databases': list(observations)}))
