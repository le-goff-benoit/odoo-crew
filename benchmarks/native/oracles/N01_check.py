import json
checks = {}
model = env['lab.rental']
for days, kind, expected in [(4, 'rental', 40), (5, 'rental', 65), (6, 'rental', 75), (7, 'loan', 70), (0, 'rental', 0)]:
    record = model.create({'name': 'oracle', 'days': days, 'daily_rate': 10, 'kind': kind})
    checks[f'{days}_{kind}'] = record.amount_total == expected
record.write({'days': 5, 'kind': 'rental', 'daily_rate': 20})
checks['dependencies'] = record.amount_total == 115
checks['stored'] = model._fields['amount_total'].store
print('LAB_ORACLE ' + json.dumps(checks))
env.cr.rollback()
