import json
from odoo import Command

company_a, company_b = env['res.company'].create([
    {'name': 'Qualification company A'}, {'name': 'Qualification company B'},
])
user = env['res.users'].with_context(no_reset_password=True).create({
    'name': 'Synthetic limited user', 'login': 'qualification_user',
    'password': 'qualification_synthetic_only',
    'company_id': company_a.id, 'company_ids': [Command.set(company_a.ids)],
    'group_ids': [Command.set(env.ref('base.group_user').ids)],
})
records = env['quality.rights.record'].create([
    {'name': 'A original', 'company_id': company_a.id, 'value': 10},
    {'name': 'B original', 'company_id': company_b.id, 'value': 20},
])
env['ir.config_parameter'].set_param('qualification.user', user.id)
env['ir.config_parameter'].set_param('qualification.a', records[0].id)
env['ir.config_parameter'].set_param('qualification.b', records[1].id)
env.cr.commit()
print('QUALIFICATION_SEED=' + json.dumps({'user': user.id, 'company_a': company_a.id,
    'company_b': company_b.id, 'a': records[0].id, 'b': records[1].id}))
