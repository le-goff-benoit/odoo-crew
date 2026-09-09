import json

Rental = env['lab.rental']
assert not Rental.search_count([]), 'La copie doit être vide avant les témoins.'
records = Rental.create([
    {'name': 'D02 témoin location 3', 'days': 3, 'daily_rate': 10, 'kind': 'rental'},
    {'name': 'D02 témoin location 4', 'days': 4, 'daily_rate': 10, 'kind': 'rental'},
    {'name': 'D02 témoin location 5', 'days': 5, 'daily_rate': 10, 'kind': 'rental'},
    {'name': 'D02 témoin prêt 4', 'days': 4, 'daily_rate': 10, 'kind': 'loan'},
])
records.flush_recordset()
records.invalidate_recordset()
assert records.mapped('amount_total') == [30, 40, 50, 40]
print('LAB_BEFORE ' + json.dumps(records.read(['name', 'days', 'daily_rate', 'kind', 'amount_total']), ensure_ascii=False))
env.cr.commit()
