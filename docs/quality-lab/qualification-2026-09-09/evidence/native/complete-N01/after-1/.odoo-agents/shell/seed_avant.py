"""Jeu de locations existantes sur la copie lab_client, calculé avec la règle d'avant D-02."""
Rental = env['lab.rental']
cas = [
    ('Location 3 jours', 3, 10.0, 'rental'),
    ('Location 4 jours', 4, 10.0, 'rental'),
    ('Location 7 jours', 7, 20.0, 'rental'),
    ('Location 5 jours tarif nul', 5, 0.0, 'rental'),
    ('Location vide', 0, 0.0, 'rental'),
    ('Pret 4 jours', 4, 10.0, 'loan'),
    ('Pret 10 jours', 10, 10.0, 'loan'),
]
existants = Rental.search([])
if existants:
    print('DEJA_PRESENT', len(existants))
else:
    for name, days, rate, kind in cas:
        Rental.create({'name': name, 'days': days, 'daily_rate': rate, 'kind': kind})
    env.cr.commit()
    print('CREES', len(cas))
for r in Rental.search([], order='id'):
    print('AVANT', r.id, r.name, r.days, r.daily_rate, r.kind, r.amount_total)
