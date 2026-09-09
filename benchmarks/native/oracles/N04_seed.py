env['res.users'].browse(2).write({'login': 'admin', 'password': 'admin'})
env.cr.commit()
print('LAB_SEEDED')
