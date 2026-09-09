env.cr.execute("SELECT id, name, state, snapshot_total, write_date FROM lab_dispatch ORDER BY id")
for r in env.cr.fetchall():
    print(f"dossier id={r[0]} {r[1]} state={r[2]} snapshot={r[3]!r} write_date={r[4]}")
env.cr.execute("SELECT id, dispatch_id, quantity, price, cancelled, write_date FROM lab_dispatch_line ORDER BY id")
for r in env.cr.fetchall():
    print(f"ligne id={r[0]} dispatch={r[1]} qty={r[2]} price={r[3]} cancelled={r[4]} write_date={r[5]}")
m = env['ir.module.module'].search([('name', '=', 'lab_dispatch')])
print("module", m.name, "state=", m.state, "latest_version=", m.latest_version)
d = env['lab.dispatch']
mixte = d.search([])
mixte.action_recalculate()
env.cr.execute("SELECT id, snapshot_total, write_date FROM lab_dispatch ORDER BY id")
print("apres action_recalculate sur TOUTE la selection (mixte):")
for r in env.cr.fetchall():
    print(f"  id={r[0]} snapshot={r[1]!r} write_date={r[2]}")
env.cr.commit()
