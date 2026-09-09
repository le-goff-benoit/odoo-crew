import json
from odoo.tools import SQL

ids = [5, 6, 7, 8]
records = env['lab.rental'].browse(ids).exists()
assert len(records) == 4
assert records.mapped('amount_total') == [30, 52, 62, 40]
env.cr.execute(SQL('SELECT amount_total FROM lab_rental WHERE id IN %s ORDER BY id', tuple(ids)))
assert [row[0] for row in env.cr.fetchall()] == [30, 52, 62, 40]
print('RELECTURE_NOUVELLE_SESSION=' + json.dumps(records.read(['name', 'days', 'daily_rate', 'kind', 'amount_total']), ensure_ascii=False))
records.unlink()
env.cr.commit()
print('NETTOYAGE : les quatre essais QA sont supprimés, copie vide comme au départ.')
