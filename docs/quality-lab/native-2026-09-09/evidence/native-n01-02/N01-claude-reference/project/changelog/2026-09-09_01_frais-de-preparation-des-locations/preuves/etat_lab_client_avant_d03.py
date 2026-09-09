# Lecture seule : état des enregistrements de lab.rental sur la copie lab_client.
env.cr.execute("SELECT count(*) FROM lab_rental")
print("lignes lab_rental :", env.cr.fetchone()[0])
env.cr.execute("SELECT id, name, kind, days, daily_rate, amount_total FROM lab_rental ORDER BY id")
for row in env.cr.fetchall():
    print("SQL", row)
