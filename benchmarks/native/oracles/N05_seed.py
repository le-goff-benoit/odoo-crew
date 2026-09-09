env['res.users'].browse(2).write({'login': 'admin', 'password': 'admin'})
for name, state, total in [('LEGACY_DRAFT', 'draft', 999), ('LEGACY_DONE', 'done', 777)]:
    record = env['lab.dispatch'].create({'name': name, 'state': state, 'snapshot_total': total})
    env['lab.dispatch.line'].create([{'dispatch_id': record.id, 'quantity': 2, 'price': 10}, {'dispatch_id': record.id, 'quantity': 3, 'price': 30, 'cancelled': True}])
r = env['lab.dispatch'].create({'name': 'LEGACY_FRACTION', 'state': 'draft', 'snapshot_total': 20.004})
env['lab.dispatch.line'].create({'dispatch_id': r.id, 'quantity': 2, 'price': 10})
env.cr.commit()
print('LAB_SEEDED')
