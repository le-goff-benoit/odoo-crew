import json

rentals = env['lab.rental'].search([])
fields = env['ir.model.fields'].search([
    ('model', '=', 'lab.rental'),
])
actions = env['ir.actions.server'].search([('model_id.model', '=', 'lab.rental')])
print('LAB_INVENTORY ' + json.dumps({
    'records': rentals.read(['name', 'days', 'daily_rate', 'kind', 'amount_total']),
    'fields': fields.read(['name', 'state', 'compute', 'store']),
    'server_actions': actions.read(['name', 'state']),
    'studio_installed': bool(env['ir.module.module'].search_count([
        ('name', '=', 'web_studio'), ('state', '=', 'installed'),
    ])),
}, ensure_ascii=False))
