import json
from unittest.mock import patch

baseline = {'companies': [{'id': 2, 'name': 'Synthetic other company N06'}, {'id': 1, 'name': 'My Company'}], 'custom_fields': [], 'initial_company_id': 1, 'lines': [{'cancelled': False, 'company_id': [1, 'My Company'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'display_name': 'lab.register.line,1', 'id': 1, 'price': 10.0, 'quantity': 2.0, 'register_id': [1, 'LEGACY_A_EARLY'], 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}, {'cancelled': True, 'company_id': [1, 'My Company'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'display_name': 'lab.register.line,2', 'id': 2, 'price': 99.0, 'quantity': 5.0, 'register_id': [1, 'LEGACY_A_EARLY'], 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}, {'cancelled': False, 'company_id': [1, 'My Company'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'display_name': 'lab.register.line,3', 'id': 3, 'price': 5.0, 'quantity': 3.0, 'register_id': [2, 'LEGACY_A_LATE'], 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}, {'cancelled': True, 'company_id': [1, 'My Company'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'display_name': 'lab.register.line,4', 'id': 4, 'price': 99.0, 'quantity': 5.0, 'register_id': [2, 'LEGACY_A_LATE'], 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}, {'cancelled': False, 'company_id': [1, 'My Company'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'display_name': 'lab.register.line,5', 'id': 5, 'price': 5.0, 'quantity': 3.0, 'register_id': [3, 'LEGACY_ISSUED'], 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}, {'cancelled': True, 'company_id': [1, 'My Company'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'display_name': 'lab.register.line,6', 'id': 6, 'price': 99.0, 'quantity': 5.0, 'register_id': [3, 'LEGACY_ISSUED'], 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}, {'cancelled': False, 'company_id': [2, 'Synthetic other company N06'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'display_name': 'lab.register.line,7', 'id': 7, 'price': 5.0, 'quantity': 3.0, 'register_id': [4, 'LEGACY_OTHER'], 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}, {'cancelled': True, 'company_id': [2, 'Synthetic other company N06'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'display_name': 'lab.register.line,8', 'id': 8, 'price': 99.0, 'quantity': 5.0, 'register_id': [4, 'LEGACY_OTHER'], 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}], 'registers': [{'company_id': [1, 'My Company'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'date_document': '2020-01-01', 'display_name': 'LEGACY_A_EARLY', 'id': 1, 'line_ids': [1, 2], 'name': 'LEGACY_A_EARLY', 'reference': 'DRAFT-A', 'sequence': 20, 'snapshot_total': 999.0, 'state': 'draft', 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}, {'company_id': [1, 'My Company'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'date_document': '2020-01-02', 'display_name': 'LEGACY_A_LATE', 'id': 2, 'line_ids': [3, 4], 'name': 'LEGACY_A_LATE', 'reference': 'DRAFT-B', 'sequence': 10, 'snapshot_total': 123.0, 'state': 'draft', 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}, {'company_id': [1, 'My Company'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'date_document': '2019-01-01', 'display_name': 'LEGACY_ISSUED', 'id': 3, 'line_ids': [5, 6], 'name': 'LEGACY_ISSUED', 'reference': 'ISSUED/005', 'sequence': 17, 'snapshot_total': 555.0, 'state': 'issued', 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}, {'company_id': [2, 'Synthetic other company N06'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'date_document': '2020-01-01', 'display_name': 'LEGACY_OTHER', 'id': 4, 'line_ids': [7, 8], 'name': 'LEGACY_OTHER', 'reference': 'OTHER/DRAFT', 'sequence': 80, 'snapshot_total': 666.0, 'state': 'draft', 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}], 'server_actions': []}
registers = env['lab.register'].browse([1, 2, 3, 4])
current = json.loads(json.dumps(registers.read(), default=str))
assert env.company.id == baseline['initial_company_id'] == 1
assert len(env['lab.register'].search([])) == 4
expected = {1: (100, 20), 2: (200, 15)}
for old, new in zip(baseline['registers'], current):
    if old['id'] in expected:
        assert (new['sequence'], new['snapshot_total']) == expected[old['id']]
        for field, value in old.items():
            if field not in ('sequence', 'snapshot_total', 'write_date', 'write_uid'):
                assert new[field] == value, (old['id'], field)
    else:
        assert new == old, old['id']
assert json.loads(json.dumps(registers.line_ids.read(), default=str)) == baseline['lines']
print('PERSISTED_AFTER_JSON=' + json.dumps(current, sort_keys=True))
original_write = type(registers).write
write_calls = []


def track_write(self, values):
    write_calls.append((self.ids, values))
    return original_write(self, values)


with patch.object(type(registers), 'write', track_write):
    assert registers.with_context(allowed_company_ids=[1, 2]).action_repair() is True
registers.flush_recordset()
assert write_calls == [], write_calls
assert json.loads(json.dumps(registers.read(), default=str)) == current
env.cr.commit()
print('REPAIR_PASS: persisted drafts 1=100/20,2=200/15; all excluded records/lines unchanged; replay write_calls=0; write_date/write_uid unchanged')
