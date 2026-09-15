import json

model = env['lab.preparation']
fields = ['name', 'state', 'ordered_qty', 'delivered_qty', 'prepared_qty', 'manual', 'parent_id', 'write_date']
rows = model.search([]).read(fields)
print('COHORTE_N17=' + json.dumps(rows, default=str, ensure_ascii=False))
print('CHAMPS_STUDIO=' + str(env['ir.model.fields'].search_count([('model', '=', 'lab.preparation'), ('state', '=', 'manual')])))
print('CRONS=' + repr(env['ir.cron'].search([('model_id.model', '=', 'lab.preparation')]).read(['name', 'code', 'active'])))
print('SERVER_ACTIONS=' + repr(env['ir.actions.server'].search([('model_id.model', '=', 'lab.preparation')]).read(['name', 'state', 'code'])))
