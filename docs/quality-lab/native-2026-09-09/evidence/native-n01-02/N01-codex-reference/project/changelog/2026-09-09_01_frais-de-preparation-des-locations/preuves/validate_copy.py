import json
import runpy
from pathlib import Path

from odoo.addons import lab_rental
from odoo.tools import SQL

BEFORE = [{'id': 5, 'name': 'QA D-02 location 3', 'kind': 'rental', 'days': 3, 'daily_rate': 10.0, 'amount_total': 30.0}, {'id': 6, 'name': 'QA D-02 location 4', 'kind': 'rental', 'days': 4, 'daily_rate': 10.0, 'amount_total': 40.0}, {'id': 7, 'name': 'QA D-02 location 5', 'kind': 'rental', 'days': 5, 'daily_rate': 10.0, 'amount_total': 50.0}, {'id': 8, 'name': 'QA D-02 prêt 4', 'kind': 'loan', 'days': 4, 'daily_rate': 10.0, 'amount_total': 40.0}]
records = env['lab.rental'].browse([row['id'] for row in BEFORE]).exists()
assert len(records) == 4
inputs = ['name', 'kind', 'days', 'daily_rate']
assert records.read(inputs) == [{key: row[key] for key in ['id', *inputs]} for row in BEFORE]
records.invalidate_recordset()
print('AFTER_UPDATE=' + json.dumps(records.read(['amount_total'])))
# La version reste inchangée pendant la release ; jouer explicitement la migration livrée.
path = Path(lab_rental.__file__).parent / 'migrations/19.0.1.0.1/post-recompute-amount-total.py'
migrate = runpy.run_path(str(path))['migrate']
expected = [30, 52, 62, 40]
for attempt in (1, 2):
    migrate(env.cr, '19.0.1.0.0')
    records.invalidate_recordset()
    assert records.mapped('amount_total') == expected
    env.cr.execute(SQL('SELECT amount_total FROM lab_rental WHERE id IN %s ORDER BY id', tuple(records.ids)))
    assert [row[0] for row in env.cr.fetchall()] == expected
    assert records.read(inputs) == [{key: row[key] for key in ['id', *inputs]} for row in BEFORE]
    print('MIGRATION_PASS=' + str(attempt) + ' TOTALS=' + json.dumps(expected))
env.cr.commit()
print('COPY_AFTER=' + json.dumps(records.read([*inputs, 'amount_total']), ensure_ascii=False))
