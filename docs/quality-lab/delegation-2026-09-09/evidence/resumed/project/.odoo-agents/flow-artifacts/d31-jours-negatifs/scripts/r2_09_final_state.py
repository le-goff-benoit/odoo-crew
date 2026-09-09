cr = env.cr
cr.execute("""SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='lab_rental'::regclass ORDER BY conname""")
rows = cr.fetchall()
print("PREUVE r2 / etat final")
print("pg_constraint =", rows)
present = [r for r in rows if r[0] == 'lab_rental_check_days_positive']
print("A6 final =", "OK" if present and present[0][1] == 'CHECK ((days >= 0))' else "ECHEC")
cr.execute("SELECT count(*) FROM lab_rental")
print("total lab_rental final =", cr.fetchone()[0])
cr.execute("SELECT count(*) FROM lab_rental WHERE days < 0")
print("lignes violantes finales =", cr.fetchone()[0])
module = env['ir.module.module'].sudo().search([('name', '=', 'lab_rental')])
print("module state =", module.state, "latest_version =", module.latest_version)
