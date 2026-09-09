"""Scénarios RPC D-22 ; données isolées et ACL temporaire nettoyées même en échec."""

from uuid import uuid4
import json

from rpc_lab import FIELD, MODEL, Lab


def main():
    lab = Lab()
    meta = lab.rows('ir.model.fields', [('model', '=', MODEL), ('name', '=', FIELD)],
                    ['ttype', 'store', 'compute', 'depends', 'readonly'])
    assert len(meta) == 1, 'D-22 absent : x_studio_needs_review attendu'
    assert meta[0]['ttype'] == 'boolean' and meta[0]['store'] and meta[0]['compute']
    assert meta[0]['readonly']
    assert set(meta[0]['depends'].split(',')) == {'x_studio_days', 'x_studio_kind'}
    checks = []
    prefix = 'D-22 — recette ' + uuid4().hex
    with lab.recipe_access():
        try:
            def create(values):
                return lab.call(MODEL, 'create', {'x_name': prefix, **values})

            def expect(rid, value, label):
                actual = lab.call(MODEL, 'read', [rid], fields=[FIELD])[0][FIELD]
                assert actual is value, (label, actual, value)
                checks.append(label)

            for days in (5, 6, 7, 8):
                for kind, expected in [('rental', days in (7, 8)), ('loan', False), (False, False)]:
                    rid = create({'x_studio_days': days, 'x_studio_kind': kind})
                    expect(rid, expected, f'creation {days} {kind}: {expected}')
            expect(create({}), False, 'valeurs absentes')
            expect(create({'x_studio_kind': 'rental'}), False, 'durée absente en location')
            rid = create({'x_studio_days': 6, 'x_studio_kind': 'rental'})
            for values, expected, label in [
                ({'x_studio_days': 7}, True, 'durée 6 → 7'),
                ({'x_studio_days': 6}, False, 'durée 7 → 6'),
                ({'x_studio_days': 8}, True, 'durée 6 → 8'),
                ({'x_studio_kind': 'loan'}, False, 'location → prêt'),
                ({'x_studio_kind': 'rental'}, True, 'prêt → location'),
                ({'x_studio_kind': False}, False, 'type effacé'),
                ({'x_studio_kind': 'rental'}, True, 'type rétabli'),
                ({'x_studio_days': 0}, False, 'durée à zéro'),
            ]:
                lab.call(MODEL, 'write', [rid], values)
                expect(rid, expected, label)
            batch = lab.call(MODEL, 'create', [
                {'x_name': prefix, 'x_studio_days': 7, 'x_studio_kind': 'loan'},
                {'x_name': prefix, 'x_studio_days': 8, 'x_studio_kind': 'rental'},
            ])
            for values, expected, label in [
                ({'x_studio_kind': 'rental'}, True, 'lot locations'),
                ({'x_studio_days': 6}, False, 'lot six jours'),
                ({'x_studio_days': 7}, True, 'lot sept jours'),
                ({'x_studio_kind': 'loan'}, False, 'lot prêts'),
            ]:
                lab.call(MODEL, 'write', batch, values)
                for item in batch:
                    expect(item, expected, f'{label} #{item}')
            source = create({'x_studio_days': 8, 'x_studio_kind': 'rental'})
            duplicate = lab.call(MODEL, 'copy', [source], {'x_name': prefix, 'x_studio_kind': 'loan'})
            if isinstance(duplicate, list):
                duplicate = duplicate[0]
            expect(source, True, 'original location')
            expect(duplicate, False, 'copie en prêt recalculée')
            rows = lab.rows(MODEL, [('x_name', '=', prefix)], [FIELD])
            selected = lab.call(MODEL, 'search', [('x_name', '=', prefix), (FIELD, '=', True)])
            assert set(selected) == {row['id'] for row in rows if row[FIELD]}
            checks.append('filtre serveur sur booléen stocké')
        finally:
            leftovers = lab.call(MODEL, 'search', [('x_name', '=', prefix)])
            if leftovers:
                lab.call(MODEL, 'unlink', leftovers)
            assert not lab.call(MODEL, 'search_count', [('x_name', '=', prefix)])
    print(json.dumps({'verdict': 'PASS', 'checks': len(checks), 'scenarios': checks,
                      'cleanup': 'données et ACL supprimées'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
