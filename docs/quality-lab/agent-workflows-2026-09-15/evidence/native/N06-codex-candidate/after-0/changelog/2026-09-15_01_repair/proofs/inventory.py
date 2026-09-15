import json

registers = env['lab.register'].search([])
payload = {
    'initial_company_id': env.company.id,
    'companies': env['res.company'].search([]).read(['name']),
    'registers': registers.read(),
    'lines': registers.line_ids.read(),
    'server_actions': env['ir.actions.server'].search([
        ('model_id.model', '=', 'lab.register'),
    ]).read(['name', 'state', 'code']),
    'custom_fields': env['ir.model.fields'].search([
        ('model', 'in', ['lab.register', 'lab.register.line']),
        ('state', '=', 'manual'),
    ]).read(['name']),
}
print('INVENTORY_JSON=' + json.dumps(payload, default=str, sort_keys=True))
