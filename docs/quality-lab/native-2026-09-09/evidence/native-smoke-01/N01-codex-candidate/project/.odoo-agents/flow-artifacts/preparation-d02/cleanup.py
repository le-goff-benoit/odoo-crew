records = env['lab.rental'].search([])
assert len(records) == 4
assert all(name.startswith('D02 témoin ') for name in records.mapped('name'))
records.unlink()
env.cr.commit()
assert not env['lab.rental'].search_count([])
print('LAB_CLEANUP_OK : quatre témoins retirés, copie vide comme avant la QA.')
