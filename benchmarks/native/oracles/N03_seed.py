env['res.users'].browse(2).write({'login': 'admin', 'password': 'admin'})
ctx = {'studio': True, 'install_mode': True}
model = env['ir.model'].with_context(**ctx).create({'name': 'Demande Aster', 'model': 'x_lab_request', 'state': 'manual'})
for name, ttype, extra in [('x_name', 'char', {}), ('x_studio_days', 'integer', {}), ('x_studio_kind', 'selection', {'selection': "[('rental', 'Location'), ('loan', 'Prêt')]"})]:
    field = env['ir.model.fields'].search([('model', '=', model.model), ('name', '=', name)])
    if not field:
        field = env['ir.model.fields'].with_context(**ctx).create(dict(name=name, field_description=name, model_id=model.id, ttype=ttype, state='manual', **extra))
    env['ir.model.data'].with_context(**ctx).create({'module': 'studio_customization', 'name': 'lab_seed_' + name, 'model': 'ir.model.fields', 'res_id': field.id, 'noupdate': True, 'studio': True})
env['ir.model.data'].with_context(**ctx).create({'module': 'studio_customization', 'name': 'lab_seed_model', 'model': 'ir.model', 'res_id': model.id, 'noupdate': True, 'studio': True})
env.cr.commit()
print('LAB_SEEDED')
