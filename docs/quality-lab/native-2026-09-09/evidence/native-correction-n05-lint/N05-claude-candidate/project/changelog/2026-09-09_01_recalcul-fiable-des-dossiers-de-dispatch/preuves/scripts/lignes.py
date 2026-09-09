for l in env['lab.dispatch.line'].search([], order='id'):
    print(f"line id={l.id} dispatch={l.dispatch_id.name} qty={l.quantity!r} price={l.price!r} cancelled={l.cancelled}")
f = env['lab.dispatch']._fields['snapshot_total']
print("snapshot_total:", type(f).__name__, "digits=", getattr(f, 'digits', None), "store=", f.store, "compute=", f.compute)
env.cr.execute("SELECT id, name, state, snapshot_total, write_date FROM lab_dispatch ORDER BY id")
print(env.cr.fetchall())
