import json

records = env['lab.rental'].search([], order='id')
assert len(records) == 4, 'Quatre témoins attendus, sans ajout ni suppression.'
assert records.mapped('name') == [
    'D02 témoin location 3', 'D02 témoin location 4',
    'D02 témoin location 5', 'D02 témoin prêt 4',
]
assert records.mapped('days') == [3, 4, 5, 4]
assert records.mapped('daily_rate') == [10, 10, 10, 10]
assert records.mapped('kind') == ['rental', 'rental', 'rental', 'loan']
assert records._fields['amount_total'].store
records.flush_recordset()
records.invalidate_recordset()
assert records.mapped('amount_total') == [30, 52, 62, 40]
print('LAB_COPY_OK ' + json.dumps(records.read(['name', 'days', 'daily_rate', 'kind', 'amount_total']), ensure_ascii=False))
