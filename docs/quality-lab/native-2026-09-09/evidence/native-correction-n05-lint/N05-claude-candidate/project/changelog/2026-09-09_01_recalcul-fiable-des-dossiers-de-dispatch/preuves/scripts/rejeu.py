repris = env['lab.dispatch']._reprise_snapshot_brouillons()
env.cr.execute("SELECT id, name, state, snapshot_total, write_date FROM lab_dispatch ORDER BY id")
lignes = env.cr.fetchall()
print("REJEU dossiers corriges =", len(repris), "ids =", repris.ids)
for row in lignes:
    print(f"id={row[0]} name={row[1]} state={row[2]} snapshot_total={row[3]!r} write_date={row[4]}")
env.cr.commit()
