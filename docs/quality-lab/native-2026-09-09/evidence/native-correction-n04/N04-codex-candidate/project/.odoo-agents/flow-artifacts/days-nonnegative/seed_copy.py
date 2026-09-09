import json

Rental = env['lab.rental']
assert not Rental.search_count([]), 'La copie initialement vide a changé.'
rental = Rental.create({'name': 'D31-QA-upgrade', 'days': 3, 'daily_rate': 12.5})
env.flush_all()
assert rental.amount_total == 37.5
env.cr.commit()
print(json.dumps({'before_update': rental.read(['name', 'days', 'daily_rate', 'amount_total'])}))
