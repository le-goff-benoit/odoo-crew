"""Préflight RPC de la fixture N03 corrigée, sans appel de modèle."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import xmlrpc.client

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import odoo_bench_native as native


def main():
    folder = Path(sys.argv[1]).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    project = folder / 'project'
    native.copy_project(ROOT / 'benchmarks/native/cases/N03/project', project)
    protocol = {'series': '19.0', 'model_calls': 0,
                'expected': ['authenticate_admin', 'create_read_existing_fields', 'write_read_existing_fields',
                             'unlink', 'stable_acl_xmlid', 'no_requested_field_yet', 'cleanup'],
                'seed_sha256': hashlib.sha256((ROOT / 'benchmarks/native/oracles/N03_seed.py').read_bytes()).hexdigest()}
    (folder / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    case = json.loads((ROOT / 'benchmarks/native/cases/N03/case.json').read_text())
    lab = native.Lab(folder, ROOT, project, case)
    started = time.monotonic()
    report = {'checks': {}, 'status': 'incident'}
    try:
        lab.start()
        with xmlrpc.client.ServerProxy(lab.url + '/xmlrpc/2/common', transport=native.RpcTransport()) as common:
            uid = common.authenticate('lab_client', 'admin', 'admin', {})
        with xmlrpc.client.ServerProxy(lab.url + '/xmlrpc/2/object', transport=native.RpcTransport(), allow_none=True) as rpc:
            def call(model, method, args, kwargs=None):
                return rpc.execute_kw('lab_client', uid, 'admin', model, method, args, kwargs or {})
            checks = report['checks']
            checks['authenticate_admin'] = uid == 2
            record = call('x_lab_request', 'create', [{'x_name': 'qualification preflight', 'x_studio_days': 6, 'x_studio_kind': 'rental'}])
            first = call('x_lab_request', 'read', [[record]], {'fields': ['x_name', 'x_studio_days', 'x_studio_kind']})
            checks['create_read_existing_fields'] = first[0]['x_studio_days'] == 6 and first[0]['x_studio_kind'] == 'rental'
            call('x_lab_request', 'write', [[record], {'x_studio_days': 7, 'x_studio_kind': 'loan'}])
            second = call('x_lab_request', 'read', [[record]], {'fields': ['x_studio_days', 'x_studio_kind']})
            checks['write_read_existing_fields'] = second[0]['x_studio_days'] == 7 and second[0]['x_studio_kind'] == 'loan'
            call('x_lab_request', 'unlink', [[record]])
            checks['unlink'] = not call('x_lab_request', 'search', [[['id', '=', record]]])
            refs = call('ir.model.data', 'search_read', [[['module', '=', 'studio_customization'], ['name', '=', 'lab_seed_access']]], {'fields': ['model', 'res_id']})
            acl = call('ir.model.access', 'read', [[refs[0]['res_id']]], {'fields': ['model_id', 'group_id', 'perm_read', 'perm_write', 'perm_create', 'perm_unlink']})
            checks['stable_acl_xmlid'] = len(refs) == 1 and refs[0]['model'] == 'ir.model.access' and all(acl[0][key] for key in ('perm_read', 'perm_write', 'perm_create', 'perm_unlink'))
            checks['no_requested_field_yet'] = 'x_studio_needs_review' not in call('x_lab_request', 'fields_get', [], {'attributes': ['type']})
            report.update(uid=uid, before=first, after=second, acl=acl, acl_xmlid='studio_customization.lab_seed_access')
        report['status'] = 'pass' if all(checks.values()) else 'fail'
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
        print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'pass' and all(report['checks'].values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
