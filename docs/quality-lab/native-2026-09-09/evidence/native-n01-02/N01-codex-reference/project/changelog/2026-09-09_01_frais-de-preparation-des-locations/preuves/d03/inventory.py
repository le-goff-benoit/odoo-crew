import json
model = env['lab.rental']
result = {
    'records': model.search([]).read(['name', 'days', 'daily_rate', 'kind', 'amount_total']),
    'manual_fields': env['ir.model.fields'].search([('model', '=', 'lab.rental'), ('state', '=', 'manual')]).read(['name', 'compute']),
    'server_actions': env['ir.actions.server'].search([('model_id.model', '=', 'lab.rental')]).read(['name', 'state']),
    'views': env['ir.ui.view'].search([('model', '=', 'lab.rental')]).read(['name', 'type']),
}
if 'base.automation' in env:
    result['automations'] = env['base.automation'].search([('model_id.model', '=', 'lab.rental')]).read(['name'])
print(json.dumps(result, ensure_ascii=False, indent=2))
