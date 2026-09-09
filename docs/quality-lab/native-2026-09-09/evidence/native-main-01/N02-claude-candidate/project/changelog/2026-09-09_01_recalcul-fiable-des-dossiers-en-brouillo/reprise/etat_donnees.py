D = env['lab.dispatch'].search([])
print('dossiers:', len(D))
for s in ('draft', 'done'):
    r = D.filtered(lambda d: d.state == s)
    print(' ', s, len(r))
print('id | name | state | snapshot | attendu_actif | total_toutes_lignes | nb_lignes | nb_annulees')
for d in D.sorted('id'):
    act = sum(l.quantity * l.price for l in d.line_ids if not l.cancelled)
    tot = sum(l.quantity * l.price for l in d.line_ids)
    print(f'{d.id} | {d.name} | {d.state} | {d.snapshot_total!r} | {act!r} | {tot!r} | {len(d.line_ids)} | {len(d.line_ids.filtered("cancelled"))}')
