import json

records = env['lab.rental'].search([('name', '=like', 'D02-QA-before-%')], order='id')
assert len(records) == 4
records.invalidate_recordset()
assert records.mapped('amount_total') == [30, 52, 62, 40], records.mapped('amount_total')
print(json.dumps(records.read(['name', 'days', 'daily_rate', 'kind', 'amount_total'])))
print('D-02 : 4/4 totaux persistés conformes dans une nouvelle session')
