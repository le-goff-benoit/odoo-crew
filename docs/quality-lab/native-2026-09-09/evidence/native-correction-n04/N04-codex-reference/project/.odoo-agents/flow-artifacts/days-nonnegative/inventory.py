import json
rentals = env['lab.rental'].search([])
print('INVENTORY', json.dumps(rentals.read(['name', 'days', 'daily_rate', 'kind', 'amount_total']), ensure_ascii=False))
print('NEGATIVE_COUNT', env['lab.rental'].search_count([('days', '<', 0)]))
print('CUSTOM_FIELDS', env['ir.model.fields'].search([('model', '=', 'lab.rental'), ('state', '=', 'manual')]).mapped('name'))
