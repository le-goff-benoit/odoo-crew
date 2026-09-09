"""Applique deux fois un pack livré inchangé dans une nouvelle copie synthétique."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import xmlrpc.client

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import odoo_bench_native as native


def main():
    supplied, folder = (Path(value).resolve() for value in sys.argv[1:])
    folder.mkdir(parents=True, exist_ok=False)
    pack = folder / 'pack-original.json'
    shutil.copy2(supplied, pack)
    project = folder / 'project'
    native.copy_project(ROOT / 'benchmarks/native/cases/N03/project', project)
    protocol = {'purpose': 'Independent artifact QA, not native-agent credit',
                'pack_sha256': hashlib.sha256(pack.read_bytes()).hexdigest(),
                'cases': 'two real apply, unchanged IDs/counts, RPC boundary and dependency checks',
                'model_calls': 0, 'max_seconds': 300}
    (folder / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    case = json.loads((ROOT / 'benchmarks/native/cases/N03/case.json').read_text())
    lab = native.Lab(folder, ROOT, project, case)
    started = time.monotonic()
    report = {'status': 'incident', 'checks': {}}
    try:
        lab.start()
        with xmlrpc.client.ServerProxy(lab.url + '/xmlrpc/2/common', transport=native.RpcTransport()) as common:
            uid = common.authenticate('lab_client', 'admin', 'admin', {})
        with xmlrpc.client.ServerProxy(lab.url + '/xmlrpc/2/object', transport=native.RpcTransport(), allow_none=True) as rpc:
            def call(model, method, args, kwargs=None):
                return rpc.execute_kw('lab_client', uid, 'admin', model, method, args, kwargs or {})
            def snapshot():
                return {
                    'fields': call('ir.model.fields', 'search_read', [[['model', '=', 'x_lab_request']]], {'fields': ['name', 'ttype', 'store', 'depends'], 'order': 'id'}),
                    'xmlids': call('ir.model.data', 'search_read', [[['module', '=', 'studio_customization']]], {'fields': ['name', 'model', 'res_id'], 'order': 'id'}),
                    'acl': call('ir.model.access', 'search_read', [[['model_id.model', '=', 'x_lab_request']]], {'fields': ['group_id', 'perm_read', 'perm_write', 'perm_create', 'perm_unlink'], 'order': 'id'}),
                }
            before = snapshot()
            report['before'] = before
            snapshots = []
            for index in (1, 2):
                result = subprocess.run([sys.executable, str(ROOT / 'scripts/odoo_pack.py'), 'apply', str(pack),
                                         '--db', 'lab_client', '--url', lab.url, '--login', 'admin', '--password', 'admin'],
                                        capture_output=True, text=True, timeout=60)
                (folder / f'apply-{index}.log').write_text(result.stdout + result.stderr)
                report['checks'][f'apply_{index}_exit'] = result.returncode == 0
                snapshots.append(snapshot())
            report['after_first'], report['after_second'] = snapshots
            report['checks']['second_identical'] = snapshots[0] == snapshots[1]
            report['checks']['one_added_field'] = len(snapshots[1]['fields']) == len(before['fields']) + 1
            report['checks']['one_added_xmlid'] = len(snapshots[1]['xmlids']) == len(before['xmlids']) + 1
            report['checks']['acl_unchanged'] = before['acl'] == snapshots[1]['acl']
            target_ref = json.loads(pack.read_text())['records'][0]['xml_id'].split('.', 1)[1]
            report['checks']['delivered_xmlid'] = sum(row['name'] == target_ref for row in snapshots[1]['xmlids']) == 1
            field = call('x_lab_request', 'fields_get', [['x_studio_needs_review']], {'attributes': ['type', 'store']})
            report['checks']['boolean_stored'] = field['x_studio_needs_review']['type'] == 'boolean' and field['x_studio_needs_review']['store']
            ids = []
            observations = []
            for days, kind, expected in ((6, 'rental', False), (7, 'rental', True), (8, 'rental', True), (7, 'loan', False)):
                record = call('x_lab_request', 'create', [{'x_name': 'qualification pack', 'x_studio_days': days, 'x_studio_kind': kind}])
                record = record[0] if isinstance(record, list) else record
                ids.append(record)
                value = call('x_lab_request', 'read', [[record]], {'fields': ['x_studio_needs_review']})[0]['x_studio_needs_review']
                observations.append({'days': days, 'kind': kind, 'value': value})
                report['checks'][f'rpc_{days}_{kind}'] = value == expected
            record = ids[0]
            call('x_lab_request', 'write', [[record], {'x_studio_days': 7}])
            report['checks']['dependency_days'] = call('x_lab_request', 'read', [[record]], {'fields': ['x_studio_needs_review']})[0]['x_studio_needs_review'] is True
            call('x_lab_request', 'write', [[record], {'x_studio_kind': 'loan'}])
            report['checks']['dependency_kind'] = call('x_lab_request', 'read', [[record]], {'fields': ['x_studio_needs_review']})[0]['x_studio_needs_review'] is False
            call('x_lab_request', 'unlink', [ids])
            report['checks']['test_records_removed'] = not call('x_lab_request', 'search', [[['id', 'in', ids]]])
            report['rpc'] = observations
        report['checks']['pack_unchanged'] = hashlib.sha256(pack.read_bytes()).hexdigest() == protocol['pack_sha256'] == hashlib.sha256(supplied.read_bytes()).hexdigest()
        report['status'] = 'pass' if all(report['checks'].values()) else 'fail'
    except Exception as exc:
        report['error'] = str(exc)
    finally:
        lab.close()
        cleanup = {}
        for kind in ('container', 'volume', 'network'):
            command = ['docker', kind, 'ls', '-q', '--filter', 'label=com.docker.compose.project=' + lab.prefix]
            if kind == 'container': command.insert(3, '-a')
            result = subprocess.run(command, capture_output=True, text=True)
            cleanup[kind] = {'exit_code': result.returncode, 'remaining': result.stdout.split()}
        report['checks']['cleanup'] = all(value['exit_code'] == 0 and not value['remaining'] for value in cleanup.values())
        report.update(cleanup=cleanup, seconds=round(time.monotonic() - started, 3), prefix=lab.prefix)
        (folder / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({'status': report['status'], 'checks': report['checks'], 'seconds': report['seconds'], 'error': report.get('error')}, indent=2))
    return 0 if report['status'] == 'pass' and all(report['checks'].values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
