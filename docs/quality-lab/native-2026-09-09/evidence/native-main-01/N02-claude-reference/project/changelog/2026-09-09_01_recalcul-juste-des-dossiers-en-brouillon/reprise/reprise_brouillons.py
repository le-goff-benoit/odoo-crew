"""Reprise idempotente des dossiers en brouillon sur la copie synthétique lab_client.

Contrat D-12 (decisions/2026-09-08.md) : seuls les dossiers ``state = 'draft'`` sont
repris, à partir de leurs lignes non annulées. Les dossiers validés ne sont ni
recalculés ni réécrits. Le script n'écrit que les brouillons qui divergent : rejoué,
il écrit zéro enregistrement.

Usage : /bridge/labctl shell changelog/<release>/reprise/reprise_brouillons.py
"""

from odoo.tools import SQL, float_compare


def _expected(dispatch):
    return sum(line.quantity * line.price for line in dispatch.line_ids if not line.cancelled)


def _write_dates(dispatches):
    if not dispatches:
        return {}
    rows = dispatches.env.execute_query(
        SQL('SELECT id, write_date FROM lab_dispatch WHERE id IN %s', tuple(dispatches.ids))
    )
    return dict(rows)


dispatches = env['lab.dispatch'].search([])
drafts = dispatches.filtered(lambda d: d.state == 'draft')
done = dispatches.filtered(lambda d: d.state == 'done')

print('=== AVANT ===')
print(f'dossiers : {len(dispatches)} · brouillons : {len(drafts)} · validés : {len(done)}')
for dispatch in dispatches:
    print(f'  id={dispatch.id} state={dispatch.state:5} snapshot={dispatch.snapshot_total:.2f} attendu={_expected(dispatch):.2f}')

done_before = _write_dates(done)
done_totals_before = {d.id: d.snapshot_total for d in done}

divergent = drafts.filtered(lambda d: float_compare(d.snapshot_total, _expected(d), precision_digits=2) != 0)
print(f'\nbrouillons divergents : {len(divergent)} / {len(drafts)}')
for dispatch in divergent:
    print(f'  id={dispatch.id} {dispatch.snapshot_total:.2f} -> {_expected(dispatch):.2f}')

divergent.action_recalculate()
env.flush_all()
written = len(divergent)

print('\n=== APRÈS ===')
for dispatch in dispatches:
    print(f'  id={dispatch.id} state={dispatch.state:5} snapshot={dispatch.snapshot_total:.2f} attendu={_expected(dispatch):.2f}')

done_after = _write_dates(done)
frozen = all(
    done_before[d.id] == done_after[d.id] and done_totals_before[d.id] == d.snapshot_total
    for d in done
)
converged = not drafts.filtered(lambda d: float_compare(d.snapshot_total, _expected(d), precision_digits=2) != 0)

print(f'\nenregistrements écrits : {written}')
print(f'validés strictement intacts (total et write_date) : {"OUI" if frozen else "NON"}')
print(f'tous les brouillons convergés : {"OUI" if converged else "NON"}')

if frozen and converged:
    env.cr.commit()
    print('REPRISE ok · commit effectué')
else:
    env.cr.rollback()
    print('REPRISE ko · rollback, rien n\'a été écrit')
