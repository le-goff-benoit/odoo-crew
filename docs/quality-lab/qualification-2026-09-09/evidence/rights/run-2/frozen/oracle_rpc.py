"""Run inside the isolated HTTP container; authentication is the ordinary user only."""
import json
import sys
import time
import xmlrpc.client

database, seed_json = sys.argv[1:]
seed = json.loads(seed_json)
common = xmlrpc.client.ServerProxy('http://127.0.0.1:8069/xmlrpc/2/common', allow_none=True)
for attempt in range(60):
    try:
        uid = common.authenticate(database, 'qualification_user', 'qualification_synthetic_only', {})
        break
    except (OSError, xmlrpc.client.ProtocolError):
        time.sleep(0.5)
else:
    raise RuntimeError('Synthetic HTTP server unavailable')
if uid != seed['user']:
    raise RuntimeError('Authentication did not yield the fixed ordinary user')
proxy = xmlrpc.client.ServerProxy('http://127.0.0.1:8069/xmlrpc/2/object', allow_none=True)
def call(method, args):
    return proxy.execute_kw(database, uid, 'qualification_synthetic_only', 'quality.rights.record', method, args,
        {'context': {'allowed_company_ids': [seed['company_a']]}})

checks = {'ordinary_user_authenticated': uid == seed['user']}
observations = {'uid': uid}
rows = call('search_read', [[], ['name', 'company_id', 'value']])
observations['search_rows'] = rows
checks['search_isolated'] = bool(rows) and all(r['company_id'][0] == seed['company_a'] for r in rows)
for action, args in [('read', [[seed['b']], ['value']]), ('write', [[seed['b']], {'value': 888}])]:
    try:
        observations[action + '_foreign_result'] = call(action, args)
        checks[action + '_foreign_denied'] = False
    except xmlrpc.client.Fault as exc:
        observations[action + '_foreign_fault'] = {'code': exc.faultCode, 'message': exc.faultString}
        # Odoo 19 /xmlrpc/2 maps AccessError to integer fault code 4, without a class name.
        checks[action + '_foreign_denied'] = exc.faultCode == 4 and bool(exc.faultString)
call('write', [[seed['a']], {'value': 12}])
checks['write_own_succeeds'] = call('read', [[seed['a']], ['value']]) == [{'id': seed['a'], 'value': 12}]
for label, company in [('own', seed['company_a']), ('foreign', seed['company_b'])]:
    result = call('load', [['name', 'company_id/.id', 'value'], [[f'RPC {label} import', str(company), '41']]])
    observations['import_' + label] = result
    if label == 'own':
        checks['import_own_succeeds'] = bool(result['ids']) and call('read', [result['ids'], ['value']])[0]['value'] == 41
    else:
        checks['import_foreign_denied'] = not result['ids'] and any(m['type'] == 'error' for m in result['messages'])
print('QUALIFICATION_RPC=' + json.dumps({'checks': checks, 'observations': observations, 'secure': all(checks.values())}, ensure_ascii=False))
