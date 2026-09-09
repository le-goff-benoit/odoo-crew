"""Postconditions sur la copie lab_client apres la mise a niveau."""
attendu = {
    'Location 3 jours': 30.0,
    'Location 4 jours': 52.0,
    'Location 7 jours': 152.0,
    'Location 5 jours tarif nul': 12.0,
    'Location vide': 0.0,
    'Pret 4 jours': 40.0,
    'Pret 10 jours': 100.0,
}
ecarts = []
for r in env['lab.rental'].search([], order='id'):
    if r.amount_total != attendu[r.name]:
        ecarts.append((r.name, attendu[r.name], r.amount_total))
print('STABLE_APRES_2E_UPDATE', not ecarts, ecarts)

module = env['ir.module.module'].search([('name', '=', 'lab_rental')])
print('VERSION_INSTALLEE', module.latest_version, module.state)

vues = env['ir.ui.view'].search_count([('model', '=', 'lab.rental')])
actions = env['ir.actions.act_window'].search_count([('res_model', '=', 'lab.rental')])
menus = env['ir.ui.menu'].search_count([('action', 'like', 'lab.rental')])
acces = env['ir.model.access'].search([('model_id.model', '=', 'lab.rental')])
regles = env['ir.rule'].search_count([('model_id.model', '=', 'lab.rental')])
autos = env['base.automation'].search_count([]) if 'base.automation' in env else 'module absent'
print('VUES', vues, 'ACTIONS', actions, 'MENUS', menus, 'REGLES', regles, 'AUTOMATISATIONS', autos)
print('ACCES', [(a.name, a.group_id.name, a.perm_read, a.perm_write, a.perm_create, a.perm_unlink) for a in acces])

champs = env['ir.model.fields'].search([('model', '=', 'lab.rental')]).mapped('name')
print('CHAMPS', sorted(n for n in champs if not n.startswith(('create_', 'write_', '__'))))
