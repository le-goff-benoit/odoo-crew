import json

from psycopg2.errors import CheckViolation

from odoo.tools import mute_logger

Rental = env['lab.rental']
rental = Rental.search([('name', '=', 'D31-QA-upgrade')])
assert len(rental) == 1
assert (rental.days, rental.daily_rate, rental.amount_total) == (3, 12.5, 37.5)
env.cr.execute("""
    SELECT conname, pg_get_constraintdef(oid), convalidated
      FROM pg_constraint
     WHERE conrelid = 'lab_rental'::regclass AND conname = 'lab_rental_days_nonnegative'
""")
constraint = env.cr.fetchone()
assert constraint and constraint[2] and constraint[1] == 'CHECK ((days >= 0))', constraint

for operation in ('create', 'write'):
    try:
        with mute_logger('odoo.sql_db'), env.cr.savepoint():
            if operation == 'create':
                Rental.create({'name': 'D31-QA-invalid', 'days': -1, 'daily_rate': 12.5})
            else:
                rental.write({'days': -1, 'daily_rate': 99})
            env.flush_all()
    except CheckViolation as error:
        assert error.diag.constraint_name == 'lab_rental_days_nonnegative'
    else:
        raise AssertionError(f'{operation} négatif accepté')
    rental.invalidate_recordset()
    assert (rental.days, rental.daily_rate, rental.amount_total) == (3, 12.5, 37.5)
    assert Rental.search_count([]) == 1

zero = Rental.create({'name': 'D31-QA-zero', 'days': 0, 'daily_rate': 12.5})
env.flush_all()
zero.invalidate_recordset()
assert (zero.days, zero.amount_total) == (0, 0)
for values, expected in (({'days': 0}, 0), ({'days': 4}, 50),
                         ({'daily_rate': -5}, -20), ({'daily_rate': 0}, 0)):
    rental.write(values)
    env.flush_all()
    rental.invalidate_recordset()
    assert rental.amount_total == expected

(rental | zero).unlink()
env.flush_all()
assert Rental.search_count([]) == 0
env.cr.commit()
print(json.dumps({'verdict': 'PASS', 'constraint': constraint, 'preserved_after_update': True,
                  'create_and_write_rejected': True, 'preserved_after_rejection': True,
                  'zero_and_total': True, 'remaining_rentals': 0}, ensure_ascii=False))
