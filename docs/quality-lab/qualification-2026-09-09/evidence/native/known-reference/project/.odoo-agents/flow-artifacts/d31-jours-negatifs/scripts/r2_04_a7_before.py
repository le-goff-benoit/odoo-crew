cr = env.cr
# Retirer temporairement la contrainte pour simuler une base héritée sans la règle D-31,
# comme si la donnée avait été insérée avant l'existence de la contrainte.
cr.execute("ALTER TABLE lab_rental DROP CONSTRAINT lab_rental_check_days_positive")
cr.execute("INSERT INTO lab_rental (name, days, daily_rate, kind, amount_total, create_uid, write_uid, create_date, write_date) "
           "VALUES ('A7 violante', -3, 10.0, 'rental', -30.0, %s, %s, now(), now())", (env.uid, env.uid))
env.cr.commit()
cr.execute("SELECT count(*) FROM lab_rental WHERE days < 0")
print("PREUVE r2 / A7 avant update")
print("lignes violantes en base =", cr.fetchone()[0])
cr.execute("""SELECT conname FROM pg_constraint WHERE conrelid='lab_rental'::regclass""")
print("contraintes restantes    =", cr.fetchall())
