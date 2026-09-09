records = env['lab.rental'].search([], order='id')
print("id | name | kind | days | rate | amount_total")
for r in records:
    print(f"{r.id} | {r.name} | {r.kind} | {r.days} | {r.daily_rate} | {r.amount_total}")
print("total_general =", sum(records.mapped('amount_total')))
print("nb =", len(records))
# Ce que D-03 changerait (simulation pure, aucune écriture)
delta = 0.0
touches = []
for r in records:
    old = 12.0 if (r.kind == 'rental' and r.days >= 4) else 0.0
    new = 15.0 if (r.kind == 'rental' and r.days >= 5) else 0.0
    if old != new:
        touches.append((r.id, r.name, r.days, old, new, new - old))
        delta += new - old
print("attendu: enregistrements impactes =", len(touches), "delta =", delta)
for t in touches:
    print("  ", t)
print("version installee du module:", env['ir.module.module'].search([('name','=','lab_rental')]).latest_version)
