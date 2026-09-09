"""Independent secure-contract oracle; never receives a variant or expected outcome."""
import json
from odoo.exceptions import AccessError

params = env['ir.config_parameter']
uid = int(params.get_param('qualification.user'))
a = int(params.get_param('qualification.a'))
b = int(params.get_param('qualification.b'))
user = env['res.users'].browse(uid)
company_a = user.company_id.id
company_b = env['quality.rights.record'].browse(b).company_id.id
model = env['quality.rights.record'].with_user(user).with_context(allowed_company_ids=[company_a])
checks = {}
observations = {'uid': model.env.uid, 'su': model.env.su, 'company_ids': user.company_ids.ids}
checks['ordinary_user'] = (model.env.uid == uid and not model.env.su
    and not user.has_group('base.group_system') and user.company_ids.ids == [company_a])
observations['search_ids'] = model.search([]).ids
checks['search_isolated'] = observations['search_ids'] == [a]
for action in ('read', 'write'):
    try:
        with env.cr.savepoint():
            observations[action + '_foreign_result'] = (
                model.browse(b).read(['name', 'value']) if action == 'read'
                else model.browse(b).write({'value': 999}))
        checks[action + '_foreign_denied'] = False
    except AccessError as exc:
        observations[action + '_foreign_error'] = str(exc)
        checks[action + '_foreign_denied'] = True
model.browse(a).write({'value': 11})
checks['write_own_succeeds'] = model.browse(a).read(['value'])[0] == {'id': a, 'value': 11}
for label, company in [('own', company_a), ('foreign', company_b)]:
    result = model.load(['name', 'company_id/.id', 'value'], [[f'ORM {label} import', str(company), '31']])
    observations['import_' + label] = result
    if label == 'own':
        checks['import_own_succeeds'] = bool(result['ids']) and model.browse(result['ids']).read(['value'])[0]['value'] == 31
    else:
        checks['import_foreign_denied'] = not result['ids'] and any(m['type'] == 'error' for m in result['messages'])
# Privileged audit observes damage independently; it does not prove user authorization.
env.invalidate_all()
audit = env['quality.rights.record']
observations['admin_postconditions'] = audit.search([]).read(['name', 'company_id', 'value'])
checks['foreign_unchanged'] = audit.browse(b).value == 20
checks['foreign_import_absent'] = not audit.search_count([('name', '=', 'ORM foreign import')])
env.cr.commit()
print('QUALIFICATION_ORM=' + json.dumps({'checks': checks, 'observations': observations, 'secure': all(checks.values())}, ensure_ascii=False))
