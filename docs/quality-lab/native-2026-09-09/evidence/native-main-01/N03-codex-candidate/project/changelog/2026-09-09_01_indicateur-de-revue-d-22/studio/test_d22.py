"""Scénario RPC : python3 test_d22.py ; valeurs relues côté serveur, nettoyage."""
import json
from rpc_local import call, scenario, MODEL, FIELD


def main():
    fields = call('ir.model.fields', 'search_read', [('model', '=', MODEL), ('name', '=', FIELD)],
                  fields=['ttype', 'store', 'depends', 'readonly'])
    assert len(fields) == 1, 'D-22 absent ou en doublon'
    field = fields[0]
    assert field['ttype'] == 'boolean' and field['store'] and field['readonly']
    assert set(field['depends'].split(',')) == {'x_studio_days', 'x_studio_kind'}
    result = scenario('''
created = requests.browse([])
try:
    cases = [(5, 'rental'), (6, 'rental'), (7, 'rental'), (8, 'rental'),
             (6, 'loan'), (7, 'loan'), (8, 'loan'), (0, 'rental'), (7, False)]
    created = requests.create([{'x_name': 'D-22 — recette', 'x_studio_days': days,
                                'x_studio_kind': kind} for days, kind in cases])
    initial = created.read(['x_studio_days', 'x_studio_kind', 'x_studio_needs_review'])
    probe = created[1]
    stages = []
    for values in [{'x_studio_days': 7}, {'x_studio_days': 6}, {'x_studio_days': 8},
                   {'x_studio_kind': 'loan'}, {'x_studio_kind': 'rental'},
                   {'x_studio_kind': False}]:
        probe.write(values)
        stages.append(probe.read(['x_studio_needs_review'])[0]['x_studio_needs_review'])
    created.write({'x_studio_days': 7, 'x_studio_kind': 'rental'})
    batch_true = created.read(['x_studio_needs_review'])
    selected = requests.search_count([('id', 'in', created.ids), ('x_studio_needs_review', '=', True)])
    created.write({'x_studio_kind': 'loan'})
    batch_false = created.read(['x_studio_needs_review'])
    selected_false = requests.search_count([('id', 'in', created.ids), ('x_studio_needs_review', '=', False)])
    action = {'type': 'ir.actions.client', 'tag': 'd22_test', 'params': {
        'initial': initial, 'stages': stages, 'batch_true': batch_true,
        'batch_false': batch_false, 'selected': selected, 'selected_false': selected_false}}
finally:
    created.unlink()
''')
    assert [r[FIELD] for r in result['initial']] == [False, False, True, True, False, False, False, False, False]
    assert result['stages'] == [True, False, True, False, True, False]
    assert all(r[FIELD] is True for r in result['batch_true'])
    assert all(r[FIELD] is False for r in result['batch_false'])
    assert result['selected'] == result['selected_false'] == 9
    remaining = scenario("action = {'type': 'ir.actions.client', 'tag': 'd22_test', 'params': requests.search_count([('x_name', '=', 'D-22 — recette')])}")
    assert remaining == 0, 'Données de recette non nettoyées'
    print(json.dumps({'verdict': 'PASS', 'creation_cases': 9, 'dependency_transitions': 6,
                      'batch_checks': 2, 'stored_searches': 2, 'cleanup': True,
                      'server_values': result}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
