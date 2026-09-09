import importlib.util
import json
from pathlib import Path
import sys
import time

ROOT = Path('/home/blegoff/.odoo19-agents')
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'scripts'))
from odoo_bench_native import Lab, copy_project, execute, source_hashes

folder = BASE / 'rpc-runtime'; folder.mkdir()
project = folder / 'project'
copy_project(ROOT / 'docs/quality-lab/delegation-2026-09-09/evidence/resumed/project', project)
case = json.loads((ROOT / 'benchmarks/native/cases/N04/case.json').read_text())
lab = Lab(folder, ROOT, project, case)
expected = "Le nombre de jours d'une location ne peut pas être négatif."
results = {'checks': {}, 'calls': [], 'prefix': lab.prefix}
start = time.monotonic()
def call(label, method, args):
    path = project / (label + '.json')
    path.write_text(json.dumps({'model': case['model'], 'method': method, 'args': args, 'kwargs': {}}))
    response = lab.handle(['rpc', str(path)])
    value = json.loads(response['output'])
    results['calls'].append({'label': label, 'exit_code': response['exit_code'], 'response': value})
    print(label, value.get('outcome'), flush=True)
    return value
try:
    lab.start()
    original_spec = importlib.util.spec_from_file_location('reference_native', BASE / 'reference/scripts/odoo_bench_native.py')
    original = importlib.util.module_from_spec(original_spec); original_spec.loader.exec_module(original)
    path = project / 'probe.json'; path.write_text('{}')
    try:
        original.Lab.handle(lab, ['rpc', str(path)])
    except ValueError as exc:
        results['reference_missing_transport'] = str(exc)
    else:
        raise AssertionError('La référence exposait déjà ce transport')
    model_path = project / 'lab_rental/models/business.py'
    good_code = model_path.read_text()
    results['model_sha256'] = source_hashes(project / 'lab_rental')
    valid = call('valid', 'create', [{'name': 'RPC valide', 'days': 5, 'daily_rate': 12.5}])['result']
    zero = call('zero', 'create', [{'name': 'RPC zéro', 'days': 0}])['result']
    bad_create = call('negative_create', 'create', [{'name': 'RPC refus', 'days': -1}])
    bad_write = call('negative_write', 'write', [[valid], {'days': -3}])
    records = call('preserved', 'read', [[valid, zero], ['days', 'amount_total']])['result']
    count = call('count', 'search_count', [[]])['result']
    for name, reply in [('create', bad_create), ('write', bad_write)]:
        results['checks'][name + '_configured_message'] = reply.get('outcome') == 'fault' and expected in reply.get('fault_string', '')
    results['checks']['valid_preserved'] = records[0]['days'] == 5 and records[0]['amount_total'] == 62.5
    results['checks']['zero_allowed'] = records[1]['days'] == 0 and records[1]['amount_total'] == 0
    results['checks']['no_failed_create_persisted'] = count == 2
    # Muter uniquement le texte, sans toucher SQL : le serveur suivant doit lire
    # le nouveau code et l'oracle doit rejeter ce mauvais message malgré le Fault.
    assert expected in good_code
    model_path.write_text(good_code.replace(expected, 'Message incorrect de contre-épreuve.'))
    mutant = call('mutant_message', 'create', [{'name': 'RPC mutation', 'days': -1}])
    results['checks']['mutant_rejected'] = mutant.get('outcome') == 'fault' and expected not in mutant.get('fault_string', '') and 'Message incorrect de contre-épreuve.' in mutant.get('fault_string', '')
    model_path.write_text(good_code)
    restored = call('restored_message', 'create', [{'name': 'RPC rétabli', 'days': -1}])
    results['checks']['fresh_registry_after_restore'] = expected in restored.get('fault_string', '')
    results['sql_oracle'] = lab.oracle()
    results['seconds'] = round(time.monotonic()-start, 2)
    (folder / 'result.json').write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results['checks'], ensure_ascii=False), flush=True)
finally:
    lab.close()
    cleanup = execute(['docker', 'ps', '-a', '--filter', 'name=' + lab.prefix, '--format', '{{.Names}}'])
    (folder / 'cleanup.json').write_text(json.dumps({'prefix': lab.prefix, 'returncode': cleanup.returncode, 'remaining_containers': cleanup.stdout.splitlines()}, indent=2))
