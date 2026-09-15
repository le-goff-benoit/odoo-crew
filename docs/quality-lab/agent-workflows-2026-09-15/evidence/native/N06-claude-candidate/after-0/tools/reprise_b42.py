"""Reprise B-42 sur lab_client : brouillons existants de la société initiale (id 1).

Exécutée sous n06_operator — utilisateur ordinaire (base.group_user, non admin)
ayant accès à DEUX sociétés, société active = My Company (id 1). La sélection
transmise est volontairement mixte : brouillons société 1, référence émise,
brouillon société 2. Rejouable : le second passage ne doit rien changer.
"""
FIELDS = ['name', 'company_id', 'state', 'date_document', 'sequence', 'snapshot_total', 'reference']

operator = env['res.users'].sudo().search([('login', '=', 'n06_operator')])
print('utilisateur :', operator.login, '| admin:', operator._is_admin(), '| sociétés:', operator.company_ids.mapped('name'))

user_env = env(user=operator, context=dict(env.context, allowed_company_ids=[1, 2]))
print('société active (env.company) :', user_env.company.id, user_env.company.name)
print('sociétés autorisées (env.companies) :', user_env.companies.ids)

Register = user_env['lab.register']
selection = Register.search([], order='id')           # tout ce que l'utilisateur voit
print('sélection mixte transmise :', selection.ids)


def snapshot(records):
    return {
        r.id: {f: (r[f].id if f == 'company_id' else r[f]) for f in FIELDS} | {'write_date': str(r.write_date)}
        for r in records
    }


before = snapshot(selection)
selection.action_repair()
selection.invalidate_recordset()
after = snapshot(selection)

print('\n--- résultat ---')
for rid in sorted(before):
    changed = {k: (before[rid][k], after[rid][k]) for k in before[rid] if before[rid][k] != after[rid][k]}
    print(f"id={rid} {before[rid]['name']} co={before[rid]['company_id']} state={before[rid]['state']} "
          f"seq={before[rid]['sequence']}->{after[rid]['sequence']} "
          f"snap={before[rid]['snapshot_total']}->{after[rid]['snapshot_total']} "
          f"ref={after[rid]['reference']!r} | champs modifiés: {sorted(changed) or 'AUCUN'}")

env.cr.commit()
print('\ncommit effectué sur lab_client')
