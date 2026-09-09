import json
model = 'lab.qualification'
result = {'database': env.cr.dbname}
result['installed_modules'] = env['ir.module.module'].search([('state', '=', 'installed')]).mapped('name')
result['manual_fields'] = env['ir.model.fields'].search([('model', '=', model), ('state', '=', 'manual')]).read(['name', 'ttype'])
result['views'] = env['ir.ui.view'].search([('model', '=', model)]).read(['name', 'inherit_id', 'active'])
result['server_actions'] = env['ir.actions.server'].search([('model_id.model', '=', model)]).read(['name', 'state'])
result['automation_installed'] = 'base.automation' in env
result['automations'] = env['base.automation'].search([('model_id.model', '=', model)]).read(['name', 'active']) if result['automation_installed'] else []
result['acl'] = env['ir.model.access'].search([('model_id.model', '=', model)]).read(['name', 'group_id', 'perm_read', 'perm_create', 'perm_write', 'perm_unlink'])
result['rules'] = env['ir.rule'].search([('model_id.model', '=', model)]).read(['name', 'domain_force'])
result['records'] = env[model].search([], order='id').read(['name', 'state', 'quantity', 'unit_price', 'amount'])
result['invalid_confirmed_count'] = env[model].search_count([('state', '=', 'confirmed'), ('quantity', '<=', 0)])
print('ANALYST_READONLY_JSON=' + json.dumps(result, sort_keys=True))
env.cr.rollback()
