"""Créer uniquement le champ D-22, avec XML-ID automatique Studio ; rejouable."""
from pathlib import Path
import json
from rpc_local import call, CTX, MODEL, FIELD

COMPUTE = "for record in self:\n    record['x_studio_needs_review'] = record['x_studio_days'] >= 7 and record['x_studio_kind'] == 'rental'"


def main():
    model_ids = call('ir.model', 'search', [('model', '=', MODEL)])
    assert len(model_ids) == 1
    sources = call('ir.model.fields', 'search_read', [
        ('model', '=', MODEL), ('name', 'in', ['x_name', 'x_studio_days', 'x_studio_kind'])
    ], fields=['name', 'ttype'])
    assert {r['name']: r['ttype'] for r in sources} == {
        'x_name': 'char', 'x_studio_days': 'integer', 'x_studio_kind': 'selection'}
    values = {'name': FIELD, 'model_id': model_ids[0], 'field_description': 'Revue requise',
              'ttype': 'boolean', 'state': 'manual', 'store': True, 'readonly': True,
              'copied': False, 'depends': 'x_studio_days,x_studio_kind', 'compute': COMPUTE}
    rows = call('ir.model.fields', 'search_read', [('model', '=', MODEL), ('name', '=', FIELD)],
                fields=list(values))
    assert len(rows) <= 1, 'Champ en doublon'
    if rows:
        row = rows[0]
        actual = {k: row[k][0] if k == 'model_id' else row[k] for k in values}
        assert actual == values, 'Champ existant différent : ne pas écraser une autre configuration'
        field_id = row['id']
        status = 'inchangé'
    else:
        field_id = call('ir.model.fields', 'create', values, context=CTX)
        status = 'créé'
    refs = call('ir.model.data', 'search_read', [
        ('model', '=', 'ir.model.fields'), ('res_id', '=', field_id),
        ('module', '=', 'studio_customization')], fields=['module', 'name', 'studio', 'noupdate'])
    # En 19.0, create marque studio ; seul write force noupdate.
    assert len(refs) == 1 and refs[0]['studio']
    xmlid = refs[0]['module'] + '.' + refs[0]['name']
    Path(__file__).with_name('created.txt').write_text(xmlid + '\n')
    print(json.dumps({'champ': FIELD, 'statut': status, 'xmlid': xmlid}, ensure_ascii=False))


if __name__ == '__main__':
    main()
