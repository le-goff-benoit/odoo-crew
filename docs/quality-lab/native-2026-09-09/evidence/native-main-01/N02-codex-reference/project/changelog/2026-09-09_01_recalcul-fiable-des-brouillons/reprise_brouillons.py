"""Run explicitly through labctl shell, only on the authorized synthetic copy."""
import json
from unittest.mock import patch


assert env.cr.dbname == 'lab_client', 'Only the synthetic lab_client copy is authorized'
records = env['lab.dispatch'].search([], order='id')
fields_to_check = ['name', 'state', 'snapshot_total', 'write_date']
before = records.read(fields_to_check)
lines_before = records.line_ids.read(['dispatch_id', 'quantity', 'price', 'cancelled', 'write_date'])
drafts = records.filtered(lambda record: record.state == 'draft')
validated_before = [row for row in before if row['state'] == 'done']
writes = []
original_write = type(records).write


def checked_write(recordset, values):
    """Prove that the repair writes only draft totals."""
    assert all(record.state == 'draft' for record in recordset)
    assert set(values) == {'snapshot_total'}
    writes.append({'ids': recordset.ids, 'values': values.copy()})
    return original_write(recordset, values)


with patch.object(type(records), 'write', checked_write):
    assert drafts.action_recalculate() is True
env.flush_all()
env.invalidate_all()
after = records.read(fields_to_check)
assert [row for row in after if row['state'] == 'done'] == validated_before
assert records.line_ids.read(['dispatch_id', 'quantity', 'price', 'cancelled', 'write_date']) == lines_before
assert [(row['id'], row['name'], row['state']) for row in before] == [
    (row['id'], row['name'], row['state']) for row in after
]
for draft in drafts:
    assert draft.snapshot_total == sum(
        line.quantity * line.price for line in draft.line_ids if not line.cancelled
    )
env.cr.commit()
print('REPRISE ' + json.dumps({
    'database': env.cr.dbname, 'before': before, 'after': after,
    'draft_ids': drafts.ids, 'writes': writes, 'committed': True,
}, default=str, ensure_ascii=False))
