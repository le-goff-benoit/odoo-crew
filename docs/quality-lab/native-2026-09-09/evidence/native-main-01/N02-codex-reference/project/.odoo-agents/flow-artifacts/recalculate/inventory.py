import json

assert env.cr.dbname == 'lab_client', env.cr.dbname
records = env['lab.dispatch'].search([])
print('INVENTORY ' + json.dumps({
    'database': env.cr.dbname,
    'dispatches': records.read(['name', 'state', 'snapshot_total', 'write_date']),
    'lines': records.line_ids.read(['dispatch_id', 'quantity', 'price', 'cancelled']),
    'studio_fields': env['ir.model.fields'].search_count([
        ('model', 'in', ['lab.dispatch', 'lab.dispatch.line']), ('state', '=', 'manual'),
    ]),
    'server_actions': env['ir.actions.server'].search([
        ('model_id.model', 'in', ['lab.dispatch', 'lab.dispatch.line']),
    ]).read(['name', 'state']),
}, default=str, ensure_ascii=False))
