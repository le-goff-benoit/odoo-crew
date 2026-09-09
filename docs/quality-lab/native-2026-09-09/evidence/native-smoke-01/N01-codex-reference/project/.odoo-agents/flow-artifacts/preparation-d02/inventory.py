import json

Rental = env['lab.rental']
records = Rental.search([])
print('LAB_INVENTORY ' + json.dumps({
    'records': records.read(['name', 'days', 'daily_rate', 'kind', 'amount_total']),
    'manual_fields': env['ir.model.fields'].search_count([
        ('model', '=', 'lab.rental'), ('state', '=', 'manual'),
    ]),
    'server_actions': env['ir.actions.server'].search([
        ('model_id.model', '=', 'lab.rental'),
    ]).read(['name', 'state']),
    'automations': env['base.automation'].search_count([
        ('model_id.model', '=', 'lab.rental'),
    ]) if 'base.automation' in env else 0,
}, ensure_ascii=False))
