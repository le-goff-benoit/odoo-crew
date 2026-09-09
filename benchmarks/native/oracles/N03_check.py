import json
model = env['x_lab_request']
field = model._fields.get('x_studio_needs_review')
checks = {'field_boolean_stored': bool(field and field.type == 'boolean' and field.store)}
if field:
    for days, kind, expected in [(5, 'rental', False), (6, 'rental', False), (7, 'rental', True), (8, 'rental', True), (9, 'loan', False)]:
        record = model.create({'x_name': 'oracle', 'x_studio_days': days, 'x_studio_kind': kind})
        checks[f'{days}_{kind}'] = record.x_studio_needs_review == expected
    record.write({'x_studio_kind': 'rental'})
    checks['dependency_kind'] = bool(record.x_studio_needs_review)
    record.write({'x_studio_days': 6})
    checks['dependency_days'] = not record.x_studio_needs_review
checks['original_fields'] = all(env.ref('studio_customization.lab_seed_' + name, raise_if_not_found=False) for name in ('x_name', 'x_studio_days', 'x_studio_kind'))
checks['single_model'] = env['ir.model'].search_count([('model', '=', 'x_lab_request')]) == 1
print('LAB_ORACLE ' + json.dumps(checks))
env.cr.rollback()
