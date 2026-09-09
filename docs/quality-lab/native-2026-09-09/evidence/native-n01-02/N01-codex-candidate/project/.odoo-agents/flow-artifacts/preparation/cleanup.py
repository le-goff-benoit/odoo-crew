records = env['lab.rental'].search([('name', '=like', 'D02-QA-before-%')])
assert len(records) == 4
records.unlink()
assert env['lab.rental'].search_count([]) == 0
env.cr.commit()
print('D-02 : 4 témoins supprimés ; copie revenue à 0 location comme avant la QA')
