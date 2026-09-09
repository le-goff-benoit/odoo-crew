"""Reprise D-12 explicite, réservée au shell Odoo de la copie synthétique."""
import json

from odoo import fields


def snapshot(records):
    """Lire les valeurs persistées des dossiers et de leurs lignes."""
    env.flush_all()
    env.invalidate_all()
    return {
        'dispatches': records.read(['name', 'state', 'snapshot_total', 'write_date']),
        'lines': records.line_ids.sorted('id').read([
            'dispatch_id', 'quantity', 'price', 'cancelled', 'write_date',
        ]),
    }


if env.cr.dbname != 'lab_client':
    raise RuntimeError('Reprise autorisée uniquement sur lab_client synthétique')

records = env['lab.dispatch'].search([], order='id')
before = snapshot(records)
drafts = records.filtered(lambda record: record.state == 'draft')
expected = {
    record.id: sum(line.quantity * line.price for line in record.line_ids if not line.cancelled)
    for record in drafts
}
drafts.action_recalculate()
after = snapshot(records)
assert before['lines'] == after['lines'], 'Les lignes doivent rester identiques'
assert len(before['dispatches']) == len(after['dispatches'])
changed_ids = []
for old, new in zip(before['dispatches'], after['dispatches']):
    assert (old['id'], old['name'], old['state']) == (new['id'], new['name'], new['state'])
    if old['state'] != 'draft':
        assert old == new, 'Un dossier validé ne doit pas être écrit'
    else:
        assert new['snapshot_total'] == expected[new['id']]
        if old['snapshot_total'] == new['snapshot_total']:
            assert old == new, 'Un brouillon déjà correct ne doit pas être écrit'
        else:
            changed_ids.append(new['id'])

env.cr.commit()
persisted = snapshot(records)
assert persisted == after
print('D12_RESULT=' + json.dumps({
    'database': env.cr.dbname,
    'executed_at': str(fields.Datetime.now()),
    'draft_ids': drafts.ids,
    'changed_ids': changed_ids,
    'before': before,
    'after': persisted,
    'committed': True,
}, default=str, sort_keys=True))
