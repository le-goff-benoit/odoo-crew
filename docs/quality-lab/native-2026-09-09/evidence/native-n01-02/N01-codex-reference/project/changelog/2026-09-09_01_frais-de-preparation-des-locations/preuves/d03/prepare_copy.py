import json

assert not env['lab.rental'].search_count([]), 'Copie attendue vide selon inventaire'
records = env['lab.rental'].create([
    {'name': f'QA D-03 {kind} {days}', 'kind': kind, 'days': days, 'daily_rate': 10}
    for kind in ('rental', 'loan') for days in (3, 4, 5, 6)
])
records.flush_recordset()
assert records.mapped('amount_total') == [30, 52, 62, 72, 30, 40, 50, 60]
print('COPY_BEFORE=' + json.dumps(records.read(['name', 'kind', 'days', 'daily_rate', 'write_date', 'amount_total']), ensure_ascii=False, default=str))
env.cr.commit()
print('PREPARE_OK: 8 essais D-02 persistés avant modification du compute.')
