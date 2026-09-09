"""Reprise D-12, uniquement via labctl shell sur la copie synthétique."""

import json


def snapshot(records):
    """Relire tous les champs persistés utiles au contrôle de non-régression."""
    records.flush_recordset()
    records.invalidate_recordset()
    return records.read(['name', 'state', 'snapshot_total', 'write_date', 'write_uid', 'line_ids'])


assert env.cr.dbname == 'lab_client', 'Reprise limitée à lab_client'
records = env['lab.dispatch'].search([])
before = snapshot(records)
lines_before = records.line_ids.read(['dispatch_id', 'quantity', 'price', 'cancelled', 'write_date'])
drafts = records.filtered(lambda record: record.state == 'draft')
expected = {
    record.id: sum(line.quantity * line.price for line in record.line_ids if not line.cancelled)
    for record in drafts
}
drafts.action_recalculate()
after = snapshot(records)
changed = []
for old, new in zip(before, after, strict=True):
    assert old['id'] == new['id']
    if old['state'] != 'draft':
        assert new == old, ('Dossier figé modifié', old, new)
    else:
        assert new['snapshot_total'] == expected[old['id']], new
        assert all(new[key] == old[key] for key in ('name', 'state', 'line_ids'))
    if old != new:
        changed.append(old['id'])
records.line_ids.invalidate_recordset()
assert records.line_ids.read(['dispatch_id', 'quantity', 'price', 'cancelled', 'write_date']) == lines_before
env.cr.commit()
assert snapshot(records) == after
print('REPRISE_D12', json.dumps({
    'database': env.cr.dbname,
    'draft_count': len(drafts),
    'frozen_count': len(records - drafts),
    'changed_ids': changed,
    'changed_count': len(changed),
    'before': before,
    'after': after,
    'lines_unchanged': True,
    'committed': True,
}, default=str, sort_keys=True))
