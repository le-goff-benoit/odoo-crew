D = env['lab.dispatch']
print("=== État de lab_client après reprise ===")
for r in D.search([], order='id'):
    print(f"id={r.id} {r.name} state={r.state} snapshot={r.snapshot_total!r} attendu={r._get_lines_total()!r}")

print("=== Action sur sélection mixte (rollback, aucune écriture conservée) ===")
avant = {r.id: (r.snapshot_total, r.state, r.write_date) for r in D.search([])}
D.search([]).action_recalculate()
for r in D.search([], order='id'):
    s0, e0, w0 = avant[r.id]
    print(f"id={r.id} {r.name} {e0}: {s0!r} -> {r.snapshot_total!r} "
          f"| état {'inchangé' if r.state == e0 else 'CHANGÉ'} "
          f"| write_date {'inchangée' if r.write_date == w0 else 'modifiée'}")
env.cr.rollback()
print("=== Après rollback ===")
D.invalidate_model()
for r in D.search([], order='id'):
    print(f"id={r.id} {r.name} state={r.state} snapshot={r.snapshot_total!r}")
