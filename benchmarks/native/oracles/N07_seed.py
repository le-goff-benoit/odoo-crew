env['res.users'].browse(2).write({'login': 'admin', 'password': 'admin'})
for name, state, ordered, delivered, prepared, manual in [
    ('LEGACY_AUTO', 'draft', 10, 3, 999, False),
    ('LEGACY_MANUAL_ZERO', 'draft', 10, 0, 0, True),
    ('LEGACY_MANUAL_PARTIAL', 'draft', 10, 3, 2, True),
    ('LEGACY_DONE', 'done', 10, 4, 88, False),
]:
    env['lab.preparation'].create({'name': name, 'state': state, 'ordered_qty': ordered, 'delivered_qty': delivered, 'prepared_qty': prepared, 'manual': manual})
env.cr.commit()
print('LAB_SEEDED')
