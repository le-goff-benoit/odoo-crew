import json

assert env.cr.dbname == 'lab_client'
records = env['lab.dispatch'].search([])
result = {
    'database': env.cr.dbname,
    'dispatches': records.read(['name', 'state', 'snapshot_total', 'write_date']),
    'lines': records.line_ids.read(['dispatch_id', 'quantity', 'price', 'cancelled']),
    'manual_fields': env['ir.model.fields'].search([('model', 'in', ['lab.dispatch', 'lab.dispatch.line']), ('state', '=', 'manual')]).mapped('name'),
    'server_actions': env['ir.actions.server'].search([('model_id.model', '=', 'lab.dispatch')]).mapped('name'),
}
print(json.dumps(result, default=str, indent=2))
