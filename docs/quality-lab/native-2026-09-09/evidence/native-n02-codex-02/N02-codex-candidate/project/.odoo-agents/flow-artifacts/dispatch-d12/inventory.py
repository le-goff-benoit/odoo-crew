import json

assert env.cr.dbname == 'lab_client', env.cr.dbname
records = env['lab.dispatch'].search([])
print('INVENTORY', json.dumps({
    'database': env.cr.dbname,
    'dispatches': records.read(['name', 'state', 'snapshot_total', 'write_date', 'line_ids']),
    'lines': records.line_ids.read(['dispatch_id', 'quantity', 'price', 'cancelled']),
    'custom_fields': env['ir.model.fields'].search([
        ('model', 'in', ['lab.dispatch', 'lab.dispatch.line']), ('state', '=', 'manual'),
    ]).read(['model', 'name']),
    'server_actions': env['ir.actions.server'].search([
        ('model_id.model', 'in', ['lab.dispatch', 'lab.dispatch.line']),
    ]).read(['name', 'state']),
}, default=str, sort_keys=True))
