"""Créer ou mettre à jour le seul indicateur D-22 sur la copie du laboratoire."""

from pathlib import Path
import json

from rpc_lab import FIELD, MODEL, Lab

COMPUTE = (
    'for record in self:\n'
    "    record['x_studio_needs_review'] = record['x_studio_days'] >= 7 "
    "and record['x_studio_kind'] == 'rental'\n"
)


def main():
    lab = Lab()
    model_id = lab.model_id()
    expected = {'x_name': 'char', 'x_studio_days': 'integer', 'x_studio_kind': 'selection'}
    existing = lab.rows('ir.model.fields', [('model', '=', MODEL), ('name', 'in', list(expected))],
                        ['name', 'ttype'])
    assert {row['name']: row['ttype'] for row in existing} == expected
    values = {
        'name': FIELD, 'model_id': model_id, 'ttype': 'boolean',
        'field_description': 'Revue requise', 'store': True, 'readonly': True,
        'compute': COMPUTE, 'depends': 'x_studio_days,x_studio_kind',
        'copied': False,
    }
    rows = lab.rows('ir.model.fields', [('model', '=', MODEL), ('name', '=', FIELD)], list(values))
    assert len(rows) <= 1
    if rows:
        rid = rows[0]['id']
        changes = {key: value for key, value in values.items()
                   if (rows[0][key][0] if key == 'model_id' else rows[0][key]) != value}
        if changes:
            lab.call('ir.model.fields', 'write', [rid], changes)
        operation = 'updated' if changes else 'unchanged'
    else:
        rid = lab.call('ir.model.fields', 'create', values)
        operation = 'created'
    ids = lab.xmlids('ir.model.fields', rid)
    assert len(ids) == 1 and ids[0]['module'] == 'studio_customization'
    # En 19.0, create marque studio ; write protège aussi par noupdate.
    # Conserver le nom natif généré, sans créer ni renommer d'XML-ID.
    if not ids[0]['noupdate']:
        lab.call('ir.model.data', 'write', [ids[0]['id']], {'noupdate': True})
        ids = lab.xmlids('ir.model.fields', rid)
    assert ids[0]['studio'] and ids[0]['noupdate']
    xmlid = ids[0]['module'] + '.' + ids[0]['name']
    Path(__file__).with_name('created.txt').write_text(xmlid + '\n', encoding='utf-8')
    print(json.dumps({'operation': operation, 'field_id': rid, 'xml_id': xmlid}, ensure_ascii=False))


if __name__ == '__main__':
    main()
