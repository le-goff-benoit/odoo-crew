import logging

records = env['lab.rental'].search([], order='id')
expected = {'D03-witness-rental-3': 30, 'D03-witness-rental-4': 40, 'D03-witness-rental-5': 65, 'D03-witness-rental-6': 75, 'D03-witness-loan-4': 40, 'D03-witness-loan-5': 50, 'D03-witness-loan-6': 60}
assert len(records) == len(expected)
assert set(records.mapped('name')) == set(expected)
for record in records:
    assert record.amount_total == expected[record.name], (record.name, record.amount_total)
logging.getLogger(__name__).warning('D03 PERSISTANCE 7/7 : %s', records.read(['name', 'amount_total']))
