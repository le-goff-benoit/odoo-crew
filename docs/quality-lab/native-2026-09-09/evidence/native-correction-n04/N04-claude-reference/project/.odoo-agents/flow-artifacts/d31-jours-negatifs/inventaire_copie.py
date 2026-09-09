env.cr.execute("SELECT count(*) FROM lab_rental")
print("SQL total:", env.cr.fetchall())
env.cr.execute("SELECT id, name, days, daily_rate, kind, amount_total FROM lab_rental ORDER BY id")
for row in env.cr.fetchall():
    print(row)
env.cr.execute("SELECT count(*) FROM lab_rental WHERE days < 0")
print("SQL negatifs:", env.cr.fetchall())
env.cr.execute("""SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint
                  WHERE conrelid = 'lab_rental'::regclass""")
print("contraintes:", env.cr.fetchall())
print("uid shell:", env.uid, env.user.login)
