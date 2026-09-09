import logging

Rental = env['lab.rental']
names = [f'D03-witness-{kind}-{days}' for kind, days in [('rental', 3), ('rental', 4), ('rental', 5), ('rental', 6), ('loan', 4), ('loan', 5), ('loan', 6)]]
records = Rental.search([('name', 'in', names)])
assert len(records) == 7
records.unlink()
assert Rental.search_count([]) == 0
logging.getLogger(__name__).warning('D03 NETTOYAGE : 7 témoins supprimés, copie vide comme initialement')
env.cr.commit()
