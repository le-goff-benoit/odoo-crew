import json
from psycopg2.errors import CheckViolation
from odoo.tools import SQL, mute_logger

Rental = env['lab.rental']
env.cr.execute(SQL("""
    SELECT conname, convalidated, pg_get_constraintdef(oid)
    FROM pg_constraint
    WHERE conrelid = 'lab_rental'::regclass AND conname = 'lab_rental_days_nonnegative'
"""))
constraint = env.cr.fetchone()
assert constraint and constraint[1] and constraint[2] == 'CHECK ((days >= 0))', constraint
print('SQL_CONSTRAINT', constraint)
rental = Rental.search([('name', '=', 'D-31 QA existing rental')])
assert len(rental) == 1
fields = ['name', 'days', 'daily_rate', 'kind', 'amount_total']
before = rental.read(fields)
assert before[0]['days'] == 2 and before[0]['daily_rate'] == 12.5 and before[0]['amount_total'] == 25
print('AFTER_UPDATE', json.dumps(before))
for kind in ('rental', 'loan'):
    try:
        with env.cr.savepoint(), mute_logger('odoo.sql_db'):
            Rental.create({'name': 'D-31 rejected create', 'kind': kind, 'days': -1})
            env.flush_all()
    except CheckViolation as error:
        assert error.diag.constraint_name == 'lab_rental_days_nonnegative'
    else:
        raise AssertionError('Negative create accepted')
assert not Rental.search_count([('name', '=', 'D-31 rejected create')])
print('NEGATIVE_CREATE_REJECTED_AND_ABSENT: OK')
try:
    with env.cr.savepoint(), mute_logger('odoo.sql_db'):
        rental.write({'days': -1, 'daily_rate': 99, 'name': 'Rejected write'})
        env.flush_all()
except CheckViolation as error:
    assert error.diag.constraint_name == 'lab_rental_days_nonnegative'
else:
    raise AssertionError('Negative write accepted')
rental.invalidate_recordset()
assert rental.read(fields) == before
print('REJECTED_WRITE_PRESERVES_RENTAL', json.dumps(rental.read(fields)))
rental.write({'days': 3})
env.flush_all()
rental.invalidate_recordset()
assert rental.amount_total == 37.5
rental.write({'days': 0})
env.flush_all()
rental.invalidate_recordset()
assert rental.amount_total == 0
zeros = Rental.create([
    {'name': 'D-31 QA zero', 'days': 0, 'daily_rate': 12.5},
    {'name': 'D-31 QA default zero', 'kind': 'loan', 'daily_rate': 12.5},
])
env.flush_all()
zeros.invalidate_recordset()
assert all(record.days == 0 and record.amount_total == 0 for record in zeros)
print('VALID_EDIT_ZERO_AND_DEFAULT: OK')
(zeros | rental).unlink()
env.cr.commit()
assert Rental.search_count([]) == 0
print('CLIENT_QA_OK: constraint verified, existing rental preserved, rejected writes rolled back, witnesses cleaned')
