import logging

Rental = env['lab.rental']
assert not Rental.search_count([]), "Inventaire changé : préserver les données existantes"
cases = [('rental', 3, 30), ('rental', 4, 52), ('rental', 5, 62), ('rental', 6, 72), ('loan', 4, 40), ('loan', 5, 50), ('loan', 6, 60)]
records = Rental.create([{'name': f'D03-witness-{kind}-{days}', 'kind': kind, 'days': days, 'daily_rate': 10} for kind, days, total in cases])
records.flush_recordset()
records.invalidate_recordset()
assert records.mapped('amount_total') == [total for kind, days, total in cases]
logging.getLogger(__name__).warning('D03 AVANT : %s', records.read(['name', 'days', 'daily_rate', 'kind', 'amount_total']))
env.cr.commit()
