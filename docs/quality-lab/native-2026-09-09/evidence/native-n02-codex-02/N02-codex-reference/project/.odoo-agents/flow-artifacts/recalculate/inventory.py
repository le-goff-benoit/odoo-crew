import json

assert env.cr.dbname == 'lab_client', 'Copie synthétique uniquement'
records = env['lab.dispatch'].search([])
result = {
    'database': env.cr.dbname,
    'dispatches': records.read(['name', 'state', 'snapshot_total', 'write_date']),
    'lines': env['lab.dispatch.line'].search([]).read(
        ['dispatch_id', 'quantity', 'price', 'cancelled']
    ),
    'manual_fields': env['ir.model.fields'].search([
        ('model', 'in', ['lab.dispatch', 'lab.dispatch.line']),
        ('state', '=', 'manual'),
    ]).read(['model', 'name']),
    'server_actions': env['ir.actions.server'].search([
        ('model_id.model', 'in', ['lab.dispatch', 'lab.dispatch.line']),
    ]).read(['name', 'state']),
    'automations': env['base.automation'].search([
        ('model_id.model', 'in', ['lab.dispatch', 'lab.dispatch.line']),
    ]).read(['name']) if 'base.automation' in env else [],
}
print('INVENTORY_JSON=' + json.dumps(result, default=str, sort_keys=True))
