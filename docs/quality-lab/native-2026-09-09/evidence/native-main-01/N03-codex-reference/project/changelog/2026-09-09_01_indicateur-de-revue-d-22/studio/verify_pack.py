"""QA du pack sur LAB.md : deux applications, diff et scénarios RPC.

--from-absent supprime uniquement l'indicateur livré sur cette copie vide,
pour prouver une première création réelle. Option réservée au laboratoire.
"""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from rpc_lab import DB, FIELD, MODEL, URL, Lab

ROOT = Path(__file__).resolve().parent
PACK_TOOL = Path.home() / '.odoo19-agents/scripts/odoo_pack.py'
PROOFS = ROOT / 'proofs'


def command(args, name, expected=None):
    result = subprocess.run(args, capture_output=True, text=True)
    (PROOFS / name).write_text(result.stdout + result.stderr, encoding='utf-8')
    assert result.returncode == 0, f'{name}: voir la preuve'
    if expected:
        assert expected in result.stdout, (name, result.stdout)
    return result.stdout


def pack_command(operation, name, expected):
    return command([sys.executable, str(PACK_TOOL), operation, str(ROOT / 'pack.json'),
                    '--db', DB, '--url', URL], name, expected)


def invariant_snapshot(lab):
    return {
        'model': lab.rows('ir.model', [('model', '=', MODEL)], ['model', 'name', 'state']),
        'fields': lab.rows('ir.model.fields', [('model', '=', MODEL), ('name', '!=', FIELD)],
                           ['name', 'ttype', 'state', 'store', 'compute', 'depends',
                            'model_id', 'readonly', 'field_description']),
        'seed_xmlids': lab.rows('ir.model.data', [('module', '=', 'studio_customization'),
                                                 ('name', '=like', 'lab_seed_%')],
                                ['module', 'name', 'model', 'res_id', 'studio', 'noupdate']),
        'access': lab.rows('ir.model.access', [('model_id.model', '=', MODEL)],
                           ['name', 'group_id', 'perm_read', 'perm_write', 'perm_create', 'perm_unlink']),
        'rules': lab.rows('ir.rule', [('model_id.model', '=', MODEL)], ['name', 'domain_force', 'groups']),
        'views': lab.rows('ir.ui.view', [('model', '=', MODEL)], ['name', 'arch_db', 'write_date']),
        'actions': lab.rows('ir.actions.server', [('model_id.model', '=', MODEL)], ['name', 'write_date']),
        'automations': lab.rows('base.automation', [('model_id.model', '=', MODEL)], ['name', 'write_date']),
    }


def field_identity(lab):
    fields = lab.rows('ir.model.fields', [('model', '=', MODEL), ('name', '=', FIELD)], ['name'])
    assert len(fields) == 1
    ids = lab.xmlids('ir.model.fields', fields[0]['id'])
    assert len(ids) == 1 and ids[0]['studio'] and ids[0]['noupdate']
    return {'field': fields[0], 'xmlid': ids[0]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--from-absent', action='store_true')
    args = parser.parse_args()
    PROOFS.mkdir(exist_ok=True)
    lab = Lab()
    pack = json.loads((ROOT / 'pack.json').read_text())
    assert len(pack['records']) == 1 and 'unresolved' not in json.dumps(pack)
    record = pack['records'][0]
    assert record['model'] == 'ir.model.fields' and record['values']['name'] == FIELD
    assert record['values']['model_id'] == {'ref': 'studio_customization.lab_seed_model'}
    before = invariant_snapshot(lab)
    initial = json.loads((PROOFS / 'inventory-before.json').read_text())
    assert sorted(before['fields'], key=lambda r: r['id']) == sorted(initial['fields'], key=lambda r: r['id'])
    assert sorted(before['seed_xmlids'], key=lambda r: r['id']) == sorted(initial['xmlids'], key=lambda r: r['id'])
    assert before['access'] == initial['access'] == []
    (PROOFS / 'invariants-before.json').write_text(json.dumps(before, indent=2, ensure_ascii=False) + '\n')

    if args.from_absent:
        # LAB.md autorise cette préparation réversible ; aucune ligne métier
        # ne doit exister et le champ doit être exactement celui de ce pack.
        with lab.recipe_access():
            assert lab.call(MODEL, 'search_count', []) == 0
        identity = field_identity(lab)
        assert identity['xmlid']['module'] + '.' + identity['xmlid']['name'] == record['xml_id']
        lab.call('ir.model.fields', 'unlink', [identity['field']['id']])
        assert not lab.call('ir.model.fields', 'search_count', [('model', '=', MODEL), ('name', '=', FIELD)])
        assert not lab.call('ir.model.data', 'search_count', [('id', '=', identity['xmlid']['id'])])
        (PROOFS / 'reset-local.json').write_text(json.dumps({'removed_delivered_field': identity,
                                                           'business_records': 0}, indent=2) + '\n')
        pack_command('diff', 'diff-before-apply1.log', '1 / 0 / 0')
        expected_first = '1 / 0 / 0'
    else:
        pack_command('diff', 'diff-before-apply1.log', '0 / 0 / 1')
        expected_first = '0 / 0 / 1'

    identities = []
    for number in (1, 2):
        pack_command('apply', f'apply{number}.log', expected_first if number == 1 else '0 / 0 / 1')
        identities.append(field_identity(lab))
        pack_command('diff', f'diff-after-apply{number}.log', '0 / 0 / 1')
        command([sys.executable, str(ROOT / 'test_d22.py')], f'scenarios-apply{number}.json', '"PASS"')
    assert identities[0] == identities[1], 'Identifiants stables après la seconde application'
    command([sys.executable, str(ROOT / 'build_d22.py')], 'build-idempotence.log', '"unchanged"')
    assert identities[1] == field_identity(lab)
    after = invariant_snapshot(lab)
    assert before == after, 'Modèle, champs existants, vues et sécurité inchangés'
    with lab.recipe_access():
        assert lab.call(MODEL, 'search_count', []) == 0
    assert invariant_snapshot(lab) == before
    studio_ids = lab.rows('ir.model.data', [('module', '=', 'studio_customization')],
                          ['module', 'name', 'model', 'res_id', 'studio', 'noupdate'])
    assert len(studio_ids) == len(initial['xmlids']) + 1
    assert not lab.call('ir.model.access', 'check', MODEL, 'create', False)
    result = {'verdict': 'PASS', 'from_absent': args.from_absent, 'applications': 2,
              'identities': identities, 'invariants_unchanged': True,
              'business_records_final': 0, 'studio_xmlids_final': len(studio_ids),
              'new_fields': 1, 'persistent_acl_added': 0, 'scenario_checks_per_run': 33}
    (PROOFS / 'pack-qa.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
