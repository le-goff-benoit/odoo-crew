Reg = env['lab.register']
print("companies:", [(c.id, c.name) for c in env['res.company'].search([])])
print("env.company:", env.company.id, env.company.name)
recs = Reg.sudo().search([], order='company_id,date_document,id')
print("total registers:", len(recs))
for r in recs:
    print(f"  id={r.id} co={r.company_id.id}/{r.company_id.name} state={r.state} date={r.date_document} seq={r.sequence} snap={r.snapshot_total} ref={r.reference!r} name={r.name!r}")
    for l in r.line_ids:
        print(f"      line id={l.id} qty={l.quantity} price={l.price} cancelled={l.cancelled}")
print("users:", [(u.id, u.login, u.company_id.name, [c.name for c in u.company_ids]) for u in env['res.users'].sudo().search([])])
