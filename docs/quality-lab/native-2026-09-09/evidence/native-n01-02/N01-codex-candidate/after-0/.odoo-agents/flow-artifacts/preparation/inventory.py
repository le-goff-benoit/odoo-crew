import json

Rental = env['lab.rental']
print(json.dumps({
    'records': Rental.search([]).read(['days', 'daily_rate', 'kind', 'amount_total']),
    'manual_fields': env['ir.model.fields'].search([
        ('model', '=', 'lab.rental'), ('state', '=', 'manual'),
    ]).mapped('name'),
    'views': env['ir.ui.view'].search_count([('model', '=', 'lab.rental')]),
    'automations_available': 'base.automation' in env,
    'server_actions': env['ir.actions.server'].search_count([
        ('model_id.model', '=', 'lab.rental'),
    ]),
}, sort_keys=True))
