# État initial de lab_client avant toute mise à niveau
cr = env.cr
cr.execute("SELECT count(*) FROM lab_rental")
print("PREUVE r2 / état initial")
print("total lab_rental       =", cr.fetchone()[0])

cr.execute("SELECT count(*) FROM lab_rental WHERE days < 0")
print("days < 0               =", cr.fetchone()[0])

cr.execute("""
    SELECT conname, pg_get_constraintdef(oid)
    FROM pg_constraint
    WHERE conrelid = 'lab_rental'::regclass
    ORDER BY conname
""")
print("pg_constraint (avant)  =", cr.fetchall())

cr.execute("""
    SELECT column_name, is_nullable, data_type
    FROM information_schema.columns
    WHERE table_name = 'lab_rental' AND column_name = 'days'
""")
print("colonne days            =", cr.fetchone())

module = env['ir.module.module'].sudo().search([('name', '=', 'lab_rental')])
print("module state             =", module.state, "latest_version =", module.latest_version)
