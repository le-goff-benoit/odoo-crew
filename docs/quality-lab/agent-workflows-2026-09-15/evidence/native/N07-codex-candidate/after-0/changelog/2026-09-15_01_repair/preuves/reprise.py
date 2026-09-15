"""Reprise autorisée N-17 sur la seule copie synthétique lab_client."""
import json

assert env.cr.dbname == 'lab_client', env.cr.dbname
model = env['lab.preparation']
records = model.search([])
before = records.read()
assert records.ids == [1, 2, 3, 4], records.ids
expected = {
    1: ('LEGACY_AUTO', 'draft', False, 10, 3, 7),
    2: ('LEGACY_MANUAL_ZERO', 'draft', True, 10, 0, 0),
    3: ('LEGACY_MANUAL_PARTIAL', 'draft', True, 10, 3, 2),
    4: ('LEGACY_DONE', 'done', False, 10, 4, 88),
}
print('AVANT_N17=' + json.dumps(before, default=str, ensure_ascii=False))
model._cron_prepare()
env.flush_all()
env.invalidate_all()
after = records.read()
assert model.search([]).ids == records.ids
changed = []
for previous, current in zip(before, after):
    identifier = current['id']
    values = tuple(current[key] for key in (
        'name', 'state', 'manual', 'ordered_qty', 'delivered_qty', 'prepared_qty',
    ))
    assert values == expected[identifier], (identifier, values)
    if identifier != 1:
        assert current == previous, (previous, current)
    else:
        for key in previous.keys() - {'prepared_qty', 'write_date', 'write_uid'}:
            assert current[key] == previous[key], key
    if previous['prepared_qty'] != current['prepared_qty']:
        changed.append(identifier)
print('APRES_N17=' + json.dumps(after, default=str, ensure_ascii=False))
print('LIGNES_MODIFIEES_N17=' + repr(changed))
env.cr.commit()
print('REPRISE_N17_COMMIT_OK')
