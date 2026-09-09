"""Etat de la copie lab_client APRES la mise a niveau D-03, compare a l'etat D-02 d'avant."""
avant = {
    'Location 3 jours': 30.0,
    'Location 4 jours': 52.0,
    'Location 7 jours': 152.0,
    'Location 5 jours tarif nul': 12.0,
    'Location vide': 0.0,
    'Pret 4 jours': 40.0,
    'Pret 10 jours': 100.0,
}
module = env['ir.module.module'].search([('name', '=', 'lab_rental')])
print('VERSION_INSTALLEE', module.latest_version, module.state)
print('%-3s %-28s %3s %7s %8s %8s %8s %7s' % ('id', 'libelle', 'j', 'tarif', 'type', 'D-02', 'D-03', 'ecart'))
for r in env['lab.rental'].search([], order='id'):
    a = avant[r.name]
    print('%-3s %-28s %3d %7.1f %8s %8.1f %8.1f %7.1f' % (
        r.id, r.name, r.days, r.daily_rate, r.kind, a, r.amount_total, r.amount_total - a))
