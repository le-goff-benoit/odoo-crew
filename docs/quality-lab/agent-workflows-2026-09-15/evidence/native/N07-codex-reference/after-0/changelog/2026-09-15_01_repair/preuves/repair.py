"""Reprise N-17 autorisée, uniquement sur la copie synthétique du laboratoire."""
import json
from unittest.mock import patch

Model = env['lab.preparation']
records = Model.search([], order='id')
fields = ['name', 'state', 'ordered_qty', 'delivered_qty', 'prepared_qty',
          'manual', 'parent_id', 'create_date', 'create_uid', 'write_date', 'write_uid']
before = records.read(fields)
print('BEFORE ' + json.dumps(before, default=str, sort_keys=True))
assert records.ids == [1, 2, 3, 4], 'Cohorte différente : réexaminer avant écriture'
assert [r['name'] for r in before] == ['LEGACY_AUTO', 'LEGACY_MANUAL_ZERO',
                                      'LEGACY_MANUAL_PARTIAL', 'LEGACY_DONE']
assert records[0].prepared_qty in (999, 7), 'État automatique inattendu'
assert records[0].state == 'draft' and not records[0].manual
assert records[0].ordered_qty == 10 and records[0].delivered_qty == 3
assert records[1].manual and records[1].prepared_qty == 0
assert records[2].manual and records[2].prepared_qty == 2
assert records[3].state == 'done' and records[3].prepared_qty == 88
Model._cron_prepare()
env.flush_all()
env.invalidate_all()
after = records.read(fields)
assert records.mapped('prepared_qty') == [7, 0, 2, 88]
assert after[1:] == before[1:], 'Une saisie ou un done a été modifié'
for key in fields:
    if key not in ('prepared_qty', 'write_date', 'write_uid'):
        assert after[0][key] == before[0][key], key
assert Model.search([], order='id') == records
with patch.object(type(Model), 'write', autospec=True) as write:
    Model._cron_prepare()
    write.assert_not_called()
env.flush_all()
env.invalidate_all()
assert records.read(fields) == after
print('AFTER ' + json.dumps(after, default=str, sort_keys=True))
print('PASS N-17: automatic draft 999->7 (or already 7); protected rows intact; replay 0 write')
env.cr.commit()
print('COMMITTED lab_client')
