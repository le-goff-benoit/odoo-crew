import json

records = env['lab.rental'].create([
    {'name': 'D02-QA-before-rental-3', 'days': 3, 'daily_rate': 10, 'kind': 'rental'},
    {'name': 'D02-QA-before-rental-4', 'days': 4, 'daily_rate': 10, 'kind': 'rental'},
    {'name': 'D02-QA-before-rental-5', 'days': 5, 'daily_rate': 10, 'kind': 'rental'},
    {'name': 'D02-QA-before-loan-4', 'days': 4, 'daily_rate': 10, 'kind': 'loan'},
])
records.flush_recordset()
assert records.mapped('amount_total') == [30, 40, 50, 40]
print(json.dumps(records.read(['name', 'days', 'daily_rate', 'kind', 'amount_total'])))
env.cr.commit()
