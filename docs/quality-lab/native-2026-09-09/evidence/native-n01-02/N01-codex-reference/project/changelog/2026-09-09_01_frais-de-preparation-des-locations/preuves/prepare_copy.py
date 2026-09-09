import json

records = env['lab.rental'].create([
    {'name': 'QA D-02 location 3', 'kind': 'rental', 'days': 3, 'daily_rate': 10},
    {'name': 'QA D-02 location 4', 'kind': 'rental', 'days': 4, 'daily_rate': 10},
    {'name': 'QA D-02 location 5', 'kind': 'rental', 'days': 5, 'daily_rate': 10},
    {'name': 'QA D-02 prêt 4', 'kind': 'loan', 'days': 4, 'daily_rate': 10},
])
records.flush_recordset()
data = records.read(['name', 'kind', 'days', 'daily_rate', 'amount_total'])
assert [row['amount_total'] for row in data] == [30, 40, 50, 40]
print('COPY_BEFORE=' + json.dumps(data, ensure_ascii=False))
env.cr.commit()
print('AVANT D-02 : 4 essais persistés, totaux 30 / 40 / 50 / 40.')
