"""QA locale du vrai pack : diff, deux apply, scénarios, identité et nettoyage.

python3 test_pack_d22.py [--recreate-added-field]
L'option retire uniquement le champ de CE pack sur le laboratoire afin de
prouver le chemin de création ; elle n'est nécessaire que pour la QA initiale.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from rpc_local import call, scenario, MODEL, FIELD, CTX, DB, URL

HERE = Path(__file__).resolve().parent
TOOL = Path.home() / '.odoo19-agents/scripts/odoo_pack.py'


def run(name, command, expected=0):
    result = subprocess.run(command, capture_output=True, text=True)
    (HERE / 'proofs' / name).write_text(result.stdout + result.stderr + f'\nEXIT_CODE={result.returncode}\n')
    print(name, 'exit', result.returncode)
    assert result.returncode == expected, result.stdout + result.stderr
    return result.stdout


def pack_command(verb):
    return [sys.executable, str(TOOL), verb, str(HERE / 'pack.json'), '--db', DB, '--url', URL]


def snapshot():
    return {
        'fields': call('ir.model.fields', 'search_read', [('model', '=', MODEL)],
                       fields=['name', 'ttype', 'store', 'compute', 'depends']),
        'xmlids': call('ir.model.data', 'search_read', [('module', '=', 'studio_customization')],
                       fields=['module', 'name', 'model', 'res_id', 'studio', 'noupdate']),
        'views': call('ir.ui.view', 'search_read', [('model', '=', MODEL)], fields=['name', 'arch_db']),
        'access': call('ir.model.access', 'search_read', [('model_id.model', '=', MODEL)],
                      fields=['name', 'group_id', 'perm_read', 'perm_write', 'perm_create', 'perm_unlink']),
        'actions': call('ir.actions.server', 'search_read', [], fields=['name', 'code']),
        'automations': call('base.automation', 'search_read', [], fields=['name']),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recreate-added-field', action='store_true')
    args = parser.parse_args()
    pack = json.loads((HERE / 'pack.json').read_text())
    assert len(pack['records']) == 1 and 'unresolved' not in json.dumps(pack)
    entry = pack['records'][0]
    assert entry['model'] == 'ir.model.fields' and entry['values']['name'] == FIELD
    before = snapshot()
    (HERE / 'proofs/before-pack.json').write_text(json.dumps(before, ensure_ascii=False, indent=2)+'\n')
    run('diff-before.log', pack_command('diff'))
    if args.recreate_added_field:
        module, name = entry['xml_id'].split('.', 1)
        refs = call('ir.model.data', 'search_read', [('module', '=', module), ('name', '=', name)], fields=['model', 'res_id'])
        assert len(refs) == 1 and refs[0]['model'] == 'ir.model.fields'
        fields = call('ir.model.fields', 'search', [('model', '=', MODEL), ('name', '=', FIELD)])
        assert fields == [refs[0]['res_id']]
        call('ir.model.fields', 'unlink', fields, context=CTX)
        run('diff-missing.log', pack_command('diff'))
    first = None
    for number in (1, 2):
        run(f'apply-{number}.log', pack_command('apply'))
        run(f'diff-{number}.log', pack_command('diff'))
        run(f'scenarios-{number}.log', [sys.executable, str(HERE / 'test_d22.py')])
        current = snapshot()
        assert len([f for f in current['fields'] if f['name'] == FIELD]) == 1
        assert len([r for r in current['xmlids'] if r['model'] == 'ir.model.fields'
                    and r['name'] == entry['xml_id'].split('.', 1)[1]]) == 1
        if first is None:
            first = current
        else:
            assert current == first, 'Deuxième application ou scénario non idempotent'
        for key in ('views', 'access', 'actions', 'automations'):
            assert current[key] == before[key], f'{key} modifié'
        old_fields = [f for f in before['fields'] if f['name'] != FIELD]
        assert [f for f in current['fields'] if f['name'] != FIELD] == old_fields
        old_refs = [r for r in before['xmlids'] if r['module']+'.'+r['name'] != entry['xml_id']]
        assert [r for r in current['xmlids'] if r['module']+'.'+r['name'] != entry['xml_id']] == old_refs
    (HERE / 'proofs/after-pack.json').write_text(json.dumps(current, ensure_ascii=False, indent=2)+'\n')
    print('PASS : deux applications, scénarios verts, identités stables, aucun doublon, sources/vues/droits/actions conservés.')


if __name__ == '__main__':
    main()
