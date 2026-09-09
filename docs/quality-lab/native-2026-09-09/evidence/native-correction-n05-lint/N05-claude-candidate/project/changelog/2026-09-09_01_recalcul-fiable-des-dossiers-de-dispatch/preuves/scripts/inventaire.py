D = env['lab.dispatch'].search([])
L = env['lab.dispatch.line'].search([])
print("dossiers:", len(D), "lignes:", len(L))
for s in ('draft', 'done'):
    r = D.filtered(lambda d: d.state == s)
    print(f"  state={s}: {len(r)}")
print("lignes annulees:", len(L.filtered('cancelled')))
print("--- detail")
for d in D.sorted('id'):
    attendu = sum(l.quantity * l.price for l in d.line_ids if not l.cancelled)
    brut = sum(l.quantity * l.price for l in d.line_ids)
    print(f"id={d.id} {d.name!r} state={d.state} snapshot={d.snapshot_total!r} attendu_hors_annul={attendu!r} brut={brut!r} nb_lignes={len(d.line_ids)} annulees={len(d.line_ids.filtered('cancelled'))}")
