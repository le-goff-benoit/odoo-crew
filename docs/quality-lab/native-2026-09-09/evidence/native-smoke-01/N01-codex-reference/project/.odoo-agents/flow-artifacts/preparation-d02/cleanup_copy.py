records = env['lab.rental'].search([('name', 'in', [
    'D02 QA location 3', 'D02 QA location 4', 'D02 QA pret 4',
])])
assert len(records) == 3
records.unlink()
assert not env['lab.rental'].search_count([])
env.cr.commit()
print('LAB_CLEANUP_OK : les trois fixtures QA ont été supprimées, modèle vide comme avant.')
