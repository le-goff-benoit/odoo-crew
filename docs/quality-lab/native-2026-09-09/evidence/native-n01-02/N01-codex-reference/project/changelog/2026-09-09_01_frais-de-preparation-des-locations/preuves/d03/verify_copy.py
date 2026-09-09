import json
from odoo.tools import SQL

BEFORE = [{'id': 9, 'name': 'QA D-03 rental 3', 'kind': 'rental', 'days': 3, 'daily_rate': 10.0, 'write_date': '2026-09-09 01:17:56.286905', 'amount_total': 30.0}, {'id': 10, 'name': 'QA D-03 rental 4', 'kind': 'rental', 'days': 4, 'daily_rate': 10.0, 'write_date': '2026-09-09 01:17:56.286905', 'amount_total': 52.0}, {'id': 11, 'name': 'QA D-03 rental 5', 'kind': 'rental', 'days': 5, 'daily_rate': 10.0, 'write_date': '2026-09-09 01:17:56.286905', 'amount_total': 62.0}, {'id': 12, 'name': 'QA D-03 rental 6', 'kind': 'rental', 'days': 6, 'daily_rate': 10.0, 'write_date': '2026-09-09 01:17:56.286905', 'amount_total': 72.0}, {'id': 13, 'name': 'QA D-03 loan 3', 'kind': 'loan', 'days': 3, 'daily_rate': 10.0, 'write_date': '2026-09-09 01:17:56.286905', 'amount_total': 30.0}, {'id': 14, 'name': 'QA D-03 loan 4', 'kind': 'loan', 'days': 4, 'daily_rate': 10.0, 'write_date': '2026-09-09 01:17:56.286905', 'amount_total': 40.0}, {'id': 15, 'name': 'QA D-03 loan 5', 'kind': 'loan', 'days': 5, 'daily_rate': 10.0, 'write_date': '2026-09-09 01:17:56.286905', 'amount_total': 50.0}, {'id': 16, 'name': 'QA D-03 loan 6', 'kind': 'loan', 'days': 6, 'daily_rate': 10.0, 'write_date': '2026-09-09 01:17:56.286905', 'amount_total': 60.0}]
records = env['lab.rental'].browse([row['id'] for row in BEFORE]).exists().sorted('id')
assert len(records) == len(BEFORE) == 8
inputs = ['name', 'kind', 'days', 'daily_rate', 'write_date']
expected_inputs = [{key: row[key] for key in ['id', *inputs]} for row in BEFORE]

def check_inputs():
    actual = json.loads(json.dumps(records.read(inputs), default=str))
    assert actual == expected_inputs, (actual, expected_inputs)

def check_totals(expected):
    records.invalidate_recordset()
    assert records.mapped('amount_total') == expected
    env.cr.execute(SQL('SELECT amount_total FROM lab_rental WHERE id IN %s ORDER BY id', tuple(records.ids)))
    assert [row[0] for row in env.cr.fetchall()] == expected
    check_inputs()

check_totals([30, 40, 65, 75, 30, 40, 50, 60])
print('RELOAD_OK=' + json.dumps(records.read([*inputs, 'amount_total']), ensure_ascii=False, default=str))
records.unlink()
env.cr.commit()
assert not env['lab.rental'].search_count([])
print('CLEANUP_OK: seuls les 8 essais créés sont supprimés ; copie vide comme avant.')
