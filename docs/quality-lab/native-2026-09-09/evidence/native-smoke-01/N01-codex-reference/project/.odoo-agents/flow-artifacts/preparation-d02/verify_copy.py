import json

records = env['lab.rental'].search([], order='id')
env.flush_all()
records.invalidate_recordset()
assert records.mapped('name') == ['D02 QA location 3', 'D02 QA location 4', 'D02 QA pret 4']
assert records.mapped('days') == [3, 4, 4]
assert records.mapped('daily_rate') == [10, 10, 10]
assert records.mapped('kind') == ['rental', 'rental', 'loan']
assert records.mapped('amount_total') == [30, 52, 40]
assert env['lab.rental'].search([('amount_total', '=', 52)]) == records[1]
print('LAB_COPY_OK ' + json.dumps(records.read(['name', 'days', 'daily_rate', 'kind', 'amount_total'])))
