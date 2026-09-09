cr = env.cr
cr.execute("""
    SELECT conname, pg_get_constraintdef(oid)
    FROM pg_constraint
    WHERE conrelid = 'lab_rental'::regclass
    ORDER BY conname
""")
rows = cr.fetchall()
print("PREUVE r2 / A6 après update")
print("pg_constraint (après update) =", rows)
found = [r for r in rows if r[0] == 'lab_rental_check_days_positive']
print("A6 =", "OK" if found and found[0][1] == 'CHECK ((days >= 0))' else "ECHEC", found)
