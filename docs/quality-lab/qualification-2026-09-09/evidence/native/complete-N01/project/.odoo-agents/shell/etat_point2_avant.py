"""Etat de la copie lab_client AVANT la mise a niveau D-03 : elle porte deja les montants D-02."""
module = env['ir.module.module'].search([('name', '=', 'lab_rental')])
print('VERSION_INSTALLEE', module.latest_version, module.state)
print('%-3s %-28s %3s %7s %8s %8s' % ('id', 'libelle', 'j', 'tarif', 'type', 'avant'))
for r in env['lab.rental'].search([], order='id'):
    print('%-3s %-28s %3d %7.1f %8s %8.1f' % (r.id, r.name, r.days, r.daily_rate, r.kind, r.amount_total))
