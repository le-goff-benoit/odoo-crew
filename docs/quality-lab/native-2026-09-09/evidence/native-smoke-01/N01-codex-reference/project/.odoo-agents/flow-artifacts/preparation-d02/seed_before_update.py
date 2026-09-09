import json

Rental = env['lab.rental']
assert not Rental.search_count([]), 'Le jeu initial doit être vide.'
records = Rental.create([
    {'name': 'D02 QA location 3', 'days': 3, 'daily_rate': 10, 'kind': 'rental'},
    {'name': 'D02 QA location 4', 'days': 4, 'daily_rate': 10, 'kind': 'rental'},
    {'name': 'D02 QA pret 4', 'days': 4, 'daily_rate': 10, 'kind': 'loan'},
])
env.flush_all()
records.invalidate_recordset()
assert records.mapped('amount_total') == [30, 40, 40]
print('LAB_BEFORE ' + json.dumps(records.read(['name', 'days', 'daily_rate', 'kind', 'amount_total'])))
env.cr.commit()
