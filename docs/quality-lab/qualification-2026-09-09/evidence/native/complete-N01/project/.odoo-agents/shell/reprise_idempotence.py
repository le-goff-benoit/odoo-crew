"""Rejoue le corps de migrations/19.0.1.2.0/post-migrate.py et verifie qu'il ne change rien.

Le second `-u` ne rejoue pas le script (la version installee est deja 19.0.1.2.0) :
l'idempotence de la reprise elle-meme se prouve en rappelant son corps.
"""
Rental = env['lab.rental']
avant = {r.id: r.amount_total for r in Rental.search([], order='id')}

rentals = Rental.search([])
env.add_to_compute(rentals._fields['amount_total'], rentals)
env.flush_all()

apres = {r.id: r.amount_total for r in Rental.search([], order='id')}
ecarts = {i: (avant[i], apres[i]) for i in avant if avant[i] != apres[i]}
print('REPRISE_REJOUEE_SANS_ECART', not ecarts, ecarts)
print('MONTANTS', sorted(apres.items()))
env.cr.commit()
