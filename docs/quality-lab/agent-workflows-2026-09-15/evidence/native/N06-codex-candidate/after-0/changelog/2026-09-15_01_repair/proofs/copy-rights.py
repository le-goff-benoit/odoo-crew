import json

from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests.common import new_test_user

baseline = {'companies': [{'id': 2, 'name': 'Synthetic other company N06'}, {'id': 1, 'name': 'My Company'}], 'custom_fields': [], 'initial_company_id': 1, 'lines': [{'cancelled': False, 'company_id': [1, 'My Company'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'display_name': 'lab.register.line,1', 'id': 1, 'price': 10.0, 'quantity': 2.0, 'register_id': [1, 'LEGACY_A_EARLY'], 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}, {'cancelled': True, 'company_id': [1, 'My Company'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'display_name': 'lab.register.line,2', 'id': 2, 'price': 99.0, 'quantity': 5.0, 'register_id': [1, 'LEGACY_A_EARLY'], 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}, {'cancelled': False, 'company_id': [1, 'My Company'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'display_name': 'lab.register.line,3', 'id': 3, 'price': 5.0, 'quantity': 3.0, 'register_id': [2, 'LEGACY_A_LATE'], 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}, {'cancelled': True, 'company_id': [1, 'My Company'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'display_name': 'lab.register.line,4', 'id': 4, 'price': 99.0, 'quantity': 5.0, 'register_id': [2, 'LEGACY_A_LATE'], 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}, {'cancelled': False, 'company_id': [1, 'My Company'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'display_name': 'lab.register.line,5', 'id': 5, 'price': 5.0, 'quantity': 3.0, 'register_id': [3, 'LEGACY_ISSUED'], 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}, {'cancelled': True, 'company_id': [1, 'My Company'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'display_name': 'lab.register.line,6', 'id': 6, 'price': 99.0, 'quantity': 5.0, 'register_id': [3, 'LEGACY_ISSUED'], 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}, {'cancelled': False, 'company_id': [2, 'Synthetic other company N06'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'display_name': 'lab.register.line,7', 'id': 7, 'price': 5.0, 'quantity': 3.0, 'register_id': [4, 'LEGACY_OTHER'], 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}, {'cancelled': True, 'company_id': [2, 'Synthetic other company N06'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'display_name': 'lab.register.line,8', 'id': 8, 'price': 99.0, 'quantity': 5.0, 'register_id': [4, 'LEGACY_OTHER'], 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}], 'registers': [{'company_id': [1, 'My Company'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'date_document': '2020-01-01', 'display_name': 'LEGACY_A_EARLY', 'id': 1, 'line_ids': [1, 2], 'name': 'LEGACY_A_EARLY', 'reference': 'DRAFT-A', 'sequence': 20, 'snapshot_total': 999.0, 'state': 'draft', 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}, {'company_id': [1, 'My Company'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'date_document': '2020-01-02', 'display_name': 'LEGACY_A_LATE', 'id': 2, 'line_ids': [3, 4], 'name': 'LEGACY_A_LATE', 'reference': 'DRAFT-B', 'sequence': 10, 'snapshot_total': 123.0, 'state': 'draft', 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}, {'company_id': [1, 'My Company'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'date_document': '2019-01-01', 'display_name': 'LEGACY_ISSUED', 'id': 3, 'line_ids': [5, 6], 'name': 'LEGACY_ISSUED', 'reference': 'ISSUED/005', 'sequence': 17, 'snapshot_total': 555.0, 'state': 'issued', 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}, {'company_id': [2, 'Synthetic other company N06'], 'create_date': '2026-09-15 22:26:42.511601', 'create_uid': [1, 'System'], 'date_document': '2020-01-01', 'display_name': 'LEGACY_OTHER', 'id': 4, 'line_ids': [7, 8], 'name': 'LEGACY_OTHER', 'reference': 'OTHER/DRAFT', 'sequence': 80, 'snapshot_total': 666.0, 'state': 'draft', 'write_date': '2026-09-15 22:26:42.511601', 'write_uid': [1, 'System']}], 'server_actions': []}
registers = env['lab.register'].browse([1, 2, 3, 4])
before = registers.read()
assert env.company.id == baseline['initial_company_id'] == 1
assert env['ir.module.module'].search([('name', '=', 'lab_register')]).state == 'installed'
assert json.loads(json.dumps(before, default=str)) == baseline['registers']
user = new_test_user(
    env, login='b42_copy_ordinary', groups='base.group_user',
    company_id=1, company_ids=[Command.set([1, 2])],
)
ordinary = registers.with_user(user).with_context(allowed_company_ids=[1, 2])
assert not ordinary.env.su
assert not user.has_group('base.group_system')
assert ordinary.action_repair() is True
assert [(r.sequence, r.snapshot_total) for r in registers[:2]] == [(100, 20), (200, 15)]
assert registers[2:].read() == before[2:]
print('ORDINARY_SUCCESS: uid=%s su=False company=1 allowed=[1,2]; drafts=100/20,200/15; excluded unchanged' % user.id)
snapshot = registers.read()
try:
    with env.cr.savepoint():
        ordinary.browse(4).with_context(allowed_company_ids=[1]).action_repair()
except AccessError as error:
    assert 'lab.register' in str(error)
    print('READ_RULE_EXPECTED_ACCESSERROR: ' + str(error))
else:
    raise AssertionError('Expected AccessError for forbidden company')
assert registers.read() == snapshot
env['ir.rule'].create({
    'name': 'B42 temporary write denial',
    'model_id': env['ir.model']._get_id('lab.register'),
    'domain_force': "[('id', '!=', 2)]",
    'perm_read': False, 'perm_write': True,
    'perm_create': False, 'perm_unlink': False,
})
try:
    with env.cr.savepoint():
        ordinary.action_repair()
except AccessError as error:
    assert 'lab.register' in str(error)
    print('WRITE_RULE_EXPECTED_ACCESSERROR: ' + str(error))
else:
    raise AssertionError('Expected AccessError for forbidden write')
assert registers.read() == snapshot
env.cr.rollback()
env.invalidate_all()
assert registers.read() == before
assert not env['res.users'].search([('login', '=', 'b42_copy_ordinary')])
assert not env['ir.rule'].search([('name', '=', 'B42 temporary write denial')])
print('COPY_RIGHTS_PASS: success, read/write denials, postconditions, rollback and cleanup verified')
