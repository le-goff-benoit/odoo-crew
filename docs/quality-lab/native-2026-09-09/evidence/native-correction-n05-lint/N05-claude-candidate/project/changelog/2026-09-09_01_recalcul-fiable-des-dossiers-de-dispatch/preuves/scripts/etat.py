env.cr.execute("SELECT id, name, state, snapshot_total, write_date FROM lab_dispatch ORDER BY id")
for row in env.cr.fetchall():
    print(f"id={row[0]} name={row[1]} state={row[2]} snapshot_total={row[3]!r} write_date={row[4]}")
