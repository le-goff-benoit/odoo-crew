import json

records = env['lab.register'].search([], order='id')
payload = {
    'database': env.cr.dbname,
    'initial_company': env.company.id,
    'registers': records.read(),
    'lines': env['lab.register.line'].search([]).read(),
    'users': env['res.users'].search([('share', '=', False)]).read(['name', 'company_id', 'company_ids']),
    'custom_fields': env['ir.model.fields'].search([('model', 'like', 'lab.register'), ('state', '=', 'manual')]).read(['name']),
    'server_actions': env['ir.actions.server'].search([('model_id.model', 'like', 'lab.register')]).read(['name', 'state']),
}
print(json.dumps(payload, default=str, indent=2))
