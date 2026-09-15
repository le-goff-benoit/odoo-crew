import json
Model = env['lab.preparation']
print('COHORT ' + json.dumps(Model.search([]).read(['name', 'state', 'ordered_qty', 'delivered_qty', 'prepared_qty', 'manual', 'parent_id']), sort_keys=True))
print('CRONS ' + repr(env['ir.cron'].search([('model_id.model', '=', 'lab.preparation')]).read(['name', 'code', 'active'])))
print('STUDIO_FIELDS ' + repr(env['ir.model.fields'].search([('model', '=', 'lab.preparation'), ('state', '=', 'manual')]).mapped('name')))
print('SERVER_ACTIONS ' + repr(env['ir.actions.server'].search([('model_id.model', '=', 'lab.preparation')]).read(['name', 'state', 'code'])))
