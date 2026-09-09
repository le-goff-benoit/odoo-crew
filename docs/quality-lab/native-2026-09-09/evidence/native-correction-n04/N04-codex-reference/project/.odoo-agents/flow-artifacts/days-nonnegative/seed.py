import json
rental = env['lab.rental'].create({'name': 'D-31 QA existing rental', 'days': 2, 'daily_rate': 12.5})
env.flush_all()
print('BEFORE_UPDATE', json.dumps(rental.read(['name', 'days', 'daily_rate', 'kind', 'amount_total'])))
env.cr.commit()
