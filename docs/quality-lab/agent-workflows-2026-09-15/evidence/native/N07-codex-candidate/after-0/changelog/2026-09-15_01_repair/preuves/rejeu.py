"""Vérifier dans un nouveau shell la persistance et le rejeu N-17."""
import json

assert env.cr.dbname == 'lab_client', env.cr.dbname
model = env['lab.preparation']
records = model.search([])
assert records.ids == [1, 2, 3, 4], records.ids
assert records.mapped('prepared_qty') == [7, 0, 2, 88]
assert records.mapped('manual') == [False, True, True, False]
assert records.mapped('state') == ['draft', 'draft', 'draft', 'done']
before = records.read()
model._cron_prepare()
env.flush_all()
env.invalidate_all()
after = records.read()
assert model.search([]).ids == records.ids
assert before == after, (before, after)
env.cr.commit()
print('REJEU_N17=' + json.dumps(after, default=str, ensure_ascii=False))
print('PERSISTANCE_ET_REJEU_OK : 4 lignes, 0 changement de champ, write_date inclus')
