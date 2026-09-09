import json
from psycopg2.errors import CheckViolation
checks = {}
model = env['lab.rental']
try:
    with env.cr.savepoint():
        record = model.create({'name': 'zéro', 'days': 0, 'daily_rate': 10})
        record.flush_recordset()
        checks['zero_allowed'] = record.days == 0 and record.amount_total == 0
except CheckViolation:
    checks['zero_allowed'] = False
try:
    with env.cr.savepoint():
        model.create({'name': 'invalide', 'days': -1}).flush_recordset()
    checks['negative_create'] = False
except CheckViolation:
    checks['negative_create'] = True
record = model.create({'name': 'valide', 'days': 3, 'daily_rate': 10})
record.flush_recordset()
try:
    with env.cr.savepoint():
        record.write({'days': -1})
        record.flush_recordset()
    checks['negative_write'] = False
except CheckViolation:
    checks['negative_write'] = True
record.invalidate_recordset()
checks['valid_record_preserved'] = record.days == 3 and record.amount_total == 30
print('LAB_ORACLE ' + json.dumps(checks))
env.cr.rollback()
