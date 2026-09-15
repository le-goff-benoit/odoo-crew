"""Relire la reprise dans une nouvelle session sans modification."""
import json
records = env['lab.preparation'].search([], order='id')
assert records.ids == [1, 2, 3, 4]
assert records.mapped('prepared_qty') == [7, 0, 2, 88]
assert records.mapped('state') == ['draft', 'draft', 'draft', 'done']
assert records.mapped('manual') == [False, True, True, False]
assert records.mapped('ordered_qty') == [10, 10, 10, 10]
assert records.mapped('delivered_qty') == [3, 0, 3, 4]
print('PERSISTED ' + json.dumps(records.read(), default=str, sort_keys=True))
assert not env['ir.cron'].search([('model_id.model', '=', 'lab.preparation')])
print('PASS: persisted quantities [7, 0, 2, 88]; no permanent cron added')
