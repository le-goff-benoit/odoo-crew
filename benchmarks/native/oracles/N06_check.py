import json
from odoo.exceptions import AccessError
from odoo import Command
model = env['lab.register']
early = model.search([('name', '=', 'LEGACY_A_EARLY')])
late = model.search([('name', '=', 'LEGACY_A_LATE')])
issued = model.search([('name', '=', 'LEGACY_ISSUED')])
other = model.search([('name', '=', 'LEGACY_OTHER')])
checks = {
    'legacy_drafts_repaired': len(early) == len(late) == 1 and early.sequence == 100 and late.sequence == 200 and early.snapshot_total == 20 and late.snapshot_total == 15,
    'emitted_reference_frozen': len(issued) == 1 and (issued.state, issued.sequence, issued.snapshot_total, issued.reference) == ('issued', 17, 555, 'ISSUED/005'),
    'other_company_untouched': len(other) == 1 and (other.sequence, other.snapshot_total, other.reference) == (80, 666, 'OTHER/DRAFT'),
}
operator = env['res.users'].search([('login', '=', 'n06_operator')])
restricted = env['res.users'].search([('login', '=', 'n06_restricted')])
company = early.company_id
ordinary = model.with_user(operator).with_context(allowed_company_ids=[company.id, other.company_id.id])
new = ordinary.create([
    {'name': 'Oracle late', 'date_document': '2030-02-02', 'company_id': company.id, 'sequence': 7, 'line_ids': [Command.create({'quantity': 4, 'price': 8}), Command.create({'quantity': 9, 'price': 9, 'cancelled': True})]},
    {'name': 'Oracle early', 'date_document': '2030-02-01', 'company_id': company.id, 'sequence': 9, 'line_ids': [Command.create({'quantity': 3, 'price': 2})]},
])
try:
    selected = ordinary.browse(new.ids + issued.ids + other.ids)
    selected.action_repair()
    checks['ordinary_user_mixed_selection'] = (new[0].sequence, new[1].sequence, new[0].snapshot_total, new[1].snapshot_total) == (200, 100, 32, 6)
    checks['scope_remains_local'] = (issued.sequence, issued.snapshot_total, issued.reference, other.sequence, other.snapshot_total) == (17, 555, 'ISSUED/005', 80, 666)
    before = selected.read(['state', 'sequence', 'snapshot_total', 'reference'])
    selected.action_repair()
    checks['idempotent'] = before == selected.read(['state', 'sequence', 'snapshot_total', 'reference'])
except Exception:
    checks['ordinary_user_mixed_selection'] = checks['scope_remains_local'] = checks['idempotent'] = False
try:
    other.with_user(restricted).with_context(allowed_company_ids=[company.id]).read(['sequence'])
    checks['company_rule_still_enforced'] = False
except AccessError:
    checks['company_rule_still_enforced'] = True
print('LAB_ORACLE ' + json.dumps(checks))
env.cr.rollback()
