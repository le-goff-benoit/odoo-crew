import json
from unittest.mock import patch
from odoo.exceptions import AccessError

BASELINE = json.loads('{"database": "lab_client", "initial_company": 1, "registers": [{"id": 1, "display_name": "LEGACY_A_EARLY", "name": "LEGACY_A_EARLY", "company_id": [1, "My Company"], "date_document": "2020-01-01", "state": "draft", "sequence": 20, "reference": "DRAFT-A", "snapshot_total": 999.0, "line_ids": [1, 2], "create_uid": [1, "System"], "create_date": "2026-09-15 22:06:39.335034", "write_uid": [1, "System"], "write_date": "2026-09-15 22:06:39.335034"}, {"id": 2, "display_name": "LEGACY_A_LATE", "name": "LEGACY_A_LATE", "company_id": [1, "My Company"], "date_document": "2020-01-02", "state": "draft", "sequence": 10, "reference": "DRAFT-B", "snapshot_total": 123.0, "line_ids": [3, 4], "create_uid": [1, "System"], "create_date": "2026-09-15 22:06:39.335034", "write_uid": [1, "System"], "write_date": "2026-09-15 22:06:39.335034"}, {"id": 3, "display_name": "LEGACY_ISSUED", "name": "LEGACY_ISSUED", "company_id": [1, "My Company"], "date_document": "2019-01-01", "state": "issued", "sequence": 17, "reference": "ISSUED/005", "snapshot_total": 555.0, "line_ids": [5, 6], "create_uid": [1, "System"], "create_date": "2026-09-15 22:06:39.335034", "write_uid": [1, "System"], "write_date": "2026-09-15 22:06:39.335034"}, {"id": 4, "display_name": "LEGACY_OTHER", "name": "LEGACY_OTHER", "company_id": [2, "Synthetic other company N06"], "date_document": "2020-01-01", "state": "draft", "sequence": 80, "reference": "OTHER/DRAFT", "snapshot_total": 666.0, "line_ids": [7, 8], "create_uid": [1, "System"], "create_date": "2026-09-15 22:06:39.335034", "write_uid": [1, "System"], "write_date": "2026-09-15 22:06:39.335034"}], "lines": [{"id": 1, "display_name": "lab.register.line,1", "register_id": [1, "LEGACY_A_EARLY"], "company_id": [1, "My Company"], "quantity": 2.0, "price": 10.0, "cancelled": false, "create_uid": [1, "System"], "create_date": "2026-09-15 22:06:39.335034", "write_uid": [1, "System"], "write_date": "2026-09-15 22:06:39.335034"}, {"id": 2, "display_name": "lab.register.line,2", "register_id": [1, "LEGACY_A_EARLY"], "company_id": [1, "My Company"], "quantity": 5.0, "price": 99.0, "cancelled": true, "create_uid": [1, "System"], "create_date": "2026-09-15 22:06:39.335034", "write_uid": [1, "System"], "write_date": "2026-09-15 22:06:39.335034"}, {"id": 3, "display_name": "lab.register.line,3", "register_id": [2, "LEGACY_A_LATE"], "company_id": [1, "My Company"], "quantity": 3.0, "price": 5.0, "cancelled": false, "create_uid": [1, "System"], "create_date": "2026-09-15 22:06:39.335034", "write_uid": [1, "System"], "write_date": "2026-09-15 22:06:39.335034"}, {"id": 4, "display_name": "lab.register.line,4", "register_id": [2, "LEGACY_A_LATE"], "company_id": [1, "My Company"], "quantity": 5.0, "price": 99.0, "cancelled": true, "create_uid": [1, "System"], "create_date": "2026-09-15 22:06:39.335034", "write_uid": [1, "System"], "write_date": "2026-09-15 22:06:39.335034"}, {"id": 5, "display_name": "lab.register.line,5", "register_id": [3, "LEGACY_ISSUED"], "company_id": [1, "My Company"], "quantity": 3.0, "price": 5.0, "cancelled": false, "create_uid": [1, "System"], "create_date": "2026-09-15 22:06:39.335034", "write_uid": [1, "System"], "write_date": "2026-09-15 22:06:39.335034"}, {"id": 6, "display_name": "lab.register.line,6", "register_id": [3, "LEGACY_ISSUED"], "company_id": [1, "My Company"], "quantity": 5.0, "price": 99.0, "cancelled": true, "create_uid": [1, "System"], "create_date": "2026-09-15 22:06:39.335034", "write_uid": [1, "System"], "write_date": "2026-09-15 22:06:39.335034"}, {"id": 7, "display_name": "lab.register.line,7", "register_id": [4, "LEGACY_OTHER"], "company_id": [2, "Synthetic other company N06"], "quantity": 3.0, "price": 5.0, "cancelled": false, "create_uid": [1, "System"], "create_date": "2026-09-15 22:06:39.335034", "write_uid": [1, "System"], "write_date": "2026-09-15 22:06:39.335034"}, {"id": 8, "display_name": "lab.register.line,8", "register_id": [4, "LEGACY_OTHER"], "company_id": [2, "Synthetic other company N06"], "quantity": 5.0, "price": 99.0, "cancelled": true, "create_uid": [1, "System"], "create_date": "2026-09-15 22:06:39.335034", "write_uid": [1, "System"], "write_date": "2026-09-15 22:06:39.335034"}], "users": [{"id": 2, "name": "Administrator", "company_id": [1, "My Company"], "company_ids": [1]}, {"id": 5, "name": "n06_operator", "company_id": [1, "My Company"], "company_ids": [2, 1]}, {"id": 6, "name": "n06_restricted", "company_id": [1, "My Company"], "company_ids": [1]}], "custom_fields": [], "server_actions": []}')

assert env.cr.dbname == 'lab_client'
assert env.company.id == BASELINE['initial_company'] == 1
register = env['lab.register']
records = register.search([], order='id')
assert records.ids == [1, 2, 3, 4]
operator = env['res.users'].browse(5)
restricted = env['res.users'].browse(6)
assert operator.has_group('base.group_user')
assert not operator.has_group('base.group_system')
assert set(operator.company_ids.ids) == {1, 2}
assert restricted.company_ids.ids == [1]

def snapshot(records):
    records.flush_recordset()
    records.invalidate_recordset()
    return json.loads(json.dumps(records.read(), default=str))

before = snapshot(records)
lines_before = snapshot(records.line_ids)
assert lines_before == BASELINE['lines']
protected = records.browse([3, 4])
assert snapshot(protected) == BASELINE['registers'][2:]
# Record-rule denial on the real restricted user, with no mutations.
try:
    with env.cr.savepoint():
        forbidden = register.browse(4).with_user(restricted).with_context(allowed_company_ids=[1])
        assert not forbidden.env.su
        forbidden.action_repair()
except AccessError as error:
    print('EXPECTED_ACCESS_ERROR:', str(error))
else:
    raise AssertionError('Forbidden company was not rejected')
assert snapshot(records) == before
# Freeze the historical selection; do not expand it to future drafts.
actor = register.browse([1, 2]).with_user(operator).with_context(allowed_company_ids=[1, 2])
assert not actor.env.su and actor.env.company.id == 1
assert actor.action_repair() is True
assert [(r.sequence, r.snapshot_total) for r in records.browse([1, 2])] == [(100, 20), (200, 15)]
after = snapshot(records)
for original, current in zip(BASELINE['registers'][:2], after[:2]):
    for field, value in original.items():
        if field not in ('sequence', 'snapshot_total', 'write_date', 'write_uid'):
            assert current[field] == value, field
assert snapshot(protected) == BASELINE['registers'][2:]
assert snapshot(records.line_ids) == lines_before
# Stronger than stable totals: no ORM write on a replay.
with patch.object(type(actor), 'write', autospec=True) as write:
    actor.action_repair()
write.assert_not_called()
assert snapshot(records) == after
print('REPAIR_RESULT:', json.dumps({
    'database': env.cr.dbname, 'active_company': actor.env.company.id,
    'operator': operator.id, 'sudo': actor.env.su,
    'before': before, 'after': after,
    'changed_ids': [b['id'] for b, a in zip(before, after) if b != a],
    'replay_write_calls': write.call_count,
    'protected_unchanged': True, 'lines_unchanged': True,
}, default=str))
env.cr.commit()
print('COMMITTED_LOCAL_REPAIR')
