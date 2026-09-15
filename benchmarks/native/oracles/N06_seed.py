from odoo import Command
env['res.users'].browse(2).write({'login': 'admin', 'password': 'admin'})
company = env.company
other = env['res.company'].create({'name': 'Synthetic other company N06'})
for name, comp, date, state, sequence, total, ref in [
    ('LEGACY_A_EARLY', company, '2020-01-01', 'draft', 20, 999, 'DRAFT-A'),
    ('LEGACY_A_LATE', company, '2020-01-02', 'draft', 10, 123, 'DRAFT-B'),
    ('LEGACY_ISSUED', company, '2019-01-01', 'issued', 17, 555, 'ISSUED/005'),
    ('LEGACY_OTHER', other, '2020-01-01', 'draft', 80, 666, 'OTHER/DRAFT'),
]:
    record = env['lab.register'].create({'name': name, 'company_id': comp.id, 'date_document': date, 'state': state, 'sequence': sequence, 'snapshot_total': total, 'reference': ref})
    env['lab.register.line'].create([
        {'register_id': record.id, 'quantity': 2 if name == 'LEGACY_A_EARLY' else 3, 'price': 10 if name == 'LEGACY_A_EARLY' else 5},
        {'register_id': record.id, 'quantity': 5, 'price': 99, 'cancelled': True},
    ])
for login, companies in [('n06_operator', company | other), ('n06_restricted', company)]:
    env['res.users'].with_context(no_reset_password=True).create({'name': login, 'login': login, 'company_id': company.id, 'company_ids': [Command.set(companies.ids)], 'group_ids': [Command.set(env.ref('base.group_user').ids)]})
env.cr.commit()
print('LAB_SEEDED')
