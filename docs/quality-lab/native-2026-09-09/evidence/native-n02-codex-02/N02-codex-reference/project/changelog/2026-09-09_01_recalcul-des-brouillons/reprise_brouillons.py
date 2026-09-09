"""Reprise D-12 explicite sur la seule copie synthétique lab_client.

Exécution : /bridge/labctl shell /work/changelog/2026-09-09_01_recalcul-des-brouillons/reprise_brouillons.py
Le commit n'intervient qu'après les assertions. Rejouer la même commande.
"""

import json

from odoo.fields import Domain


def snapshot(env):
    """Relire les données persistées et leurs métadonnées après flush."""
    env.flush_all()
    env.invalidate_all()
    return {
        'dispatches': env['lab.dispatch'].search(Domain.TRUE, order='id').read(
            ['name', 'state', 'snapshot_total', 'write_date', 'write_uid'],
        ),
        'lines': env['lab.dispatch.line'].search(Domain.TRUE, order='id').read(
            ['dispatch_id', 'quantity', 'price', 'cancelled', 'write_date', 'write_uid'],
        ),
    }


def repair(env):
    """Corriger les brouillons et prouver la conservation de tout le reste."""
    assert env.cr.dbname == 'lab_client', 'Copie synthétique uniquement'
    before = snapshot(env)
    drafts = env['lab.dispatch'].search(Domain('state', '=', 'draft'))
    expected = {
        record['id']: sum(
            line['quantity'] * line['price']
            for line in before['lines']
            if line['dispatch_id'][0] == record['id'] and not line['cancelled']
        )
        for record in before['dispatches'] if record['state'] == 'draft'
    }
    assert set(drafts.ids) == set(expected)
    drafts.action_recalculate()
    after = snapshot(env)
    assert before['lines'] == after['lines'], 'Les lignes doivent rester inchangées'
    assert len(before['dispatches']) == len(after['dispatches'])
    changed_ids = []
    for old, new in zip(before['dispatches'], after['dispatches'], strict=True):
        assert old['id'] == new['id']
        if old['state'] != 'draft':
            assert old == new, 'Dossier validé modifié'
        else:
            assert new['snapshot_total'] == expected[old['id']]
            assert all(old[key] == new[key] for key in ('id', 'name', 'state'))
            if old['snapshot_total'] == new['snapshot_total']:
                assert old == new, 'Une reprise sans écart doit rester sans écriture'
            else:
                changed_ids.append(old['id'])
    env.cr.commit()
    persisted = snapshot(env)
    assert persisted == after, 'État persistant différent après commit'
    print('REPAIR_JSON=' + json.dumps({  # ruff: ignore[print] - preuve du shell capturée par le pont
        'database': env.cr.dbname,
        'draft_count': len(drafts),
        'validated_count': sum(row['state'] == 'done' for row in before['dispatches']),
        'changed_count': len(changed_ids),
        'changed_ids': changed_ids,
        'before': before,
        'after': persisted,
    }, default=str, sort_keys=True))


repair(env)
