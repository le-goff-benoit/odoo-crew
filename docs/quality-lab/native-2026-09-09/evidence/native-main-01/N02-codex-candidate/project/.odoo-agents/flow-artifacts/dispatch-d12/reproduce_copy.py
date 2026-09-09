import json

assert env.cr.dbname == 'lab_client'
records = env['lab.dispatch'].search([], order='id')
before = records.read(['name', 'state', 'snapshot_total', 'write_date'])
records.action_recalculate()
records.flush_recordset()
records.invalidate_recordset()
after = records.read(['name', 'state', 'snapshot_total', 'write_date'])
assert [item['snapshot_total'] for item in after] == [110, 110]
assert [item['snapshot_total'] for item in before] == [999, 777]
env.cr.rollback()
records.invalidate_recordset()
assert records.read(['name', 'state', 'snapshot_total', 'write_date']) == before
print(json.dumps({'before': before, 'defect': after, 'rollback_verified': True}, default=str, indent=2))
