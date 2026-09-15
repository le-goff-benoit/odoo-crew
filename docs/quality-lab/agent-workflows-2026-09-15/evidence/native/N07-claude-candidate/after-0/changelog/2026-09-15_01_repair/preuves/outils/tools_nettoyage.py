# Retire les enregistrements créés par le parcours XML-RPC de la QA.
rpc = env['lab.preparation'].search([('name', 'like', 'RPC_')])
print('à supprimer : %s' % rpc.mapped('name'))
rpc.unlink()
env.cr.commit()
print('restant = %s' % env['lab.preparation'].search_count([]))
