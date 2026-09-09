"""Reproduire le défaut sur les dossiers synthétiques existants, puis rollback."""

import json

from odoo.fields import Domain

assert env.cr.dbname == 'lab_client', 'Copie synthétique uniquement'
records = env['lab.dispatch'].search(Domain.TRUE, order='id')
before = records.read(['name', 'state', 'snapshot_total', 'write_date'])
try:
    records.action_recalculate()
    env.flush_all()
    env.invalidate_all()
    faulty = records.read(['name', 'state', 'snapshot_total', 'write_date'])
    assert [(row['name'], row['snapshot_total']) for row in faulty] == [
        ('LEGACY_DRAFT', 110), ('LEGACY_DONE', 110),
    ]
finally:
    env.cr.rollback()
    env.invalidate_all()
restored = records.read(['name', 'state', 'snapshot_total', 'write_date'])
assert restored == before
print('RED_COPY_JSON=' + json.dumps({  # ruff: ignore[print] - preuve shell
    'before': before, 'faulty': faulty, 'after_rollback': restored,
}, default=str, sort_keys=True))
