"""Reprise des dossiers logistiques existants — décision D-12.

Rejoue `action_recalculate` sur les **seuls** dossiers en brouillon, afin de
corriger les `snapshot_total` hérités (lignes annulées incluses à tort). Les
dossiers validés sont laissés strictement intacts : ils ne sont même pas
parcourus. Le script est idempotent — un second passage ne change rien et le
signale par `modifies=0`.

Exécution : /bridge/labctl shell <chemin>/reprise_brouillons.py
"""

Dispatch = env['lab.dispatch']

drafts = Dispatch.search([('state', '=', 'draft')])
done = Dispatch.search([('state', '=', 'done')])

before_drafts = {d.id: d.snapshot_total for d in drafts}
before_done = {d.id: d.snapshot_total for d in done}

drafts.action_recalculate()
env.flush_all()

after_drafts = {d.id: d.snapshot_total for d in drafts}
after_done = {d.id: d.snapshot_total for d in Dispatch.search([('state', '=', 'done')])}

changed = {i: (before_drafts[i], after_drafts[i]) for i in after_drafts if before_drafts[i] != after_drafts[i]}
done_changed = {i: (before_done[i], after_done[i]) for i in after_done if before_done.get(i) != after_done[i]}

print('REPRISE brouillons=%d valides=%d modifies=%d valides_modifies=%d' % (
    len(drafts), len(done), len(changed), len(done_changed)))
for dispatch in drafts.sorted('id'):
    print('  draft  id=%d %-14s %r -> %r' % (
        dispatch.id, dispatch.name, before_drafts[dispatch.id], after_drafts[dispatch.id]))
for dispatch in done.sorted('id'):
    print('  done   id=%d %-14s %r (inchangé: %s)' % (
        dispatch.id, dispatch.name, after_done[dispatch.id],
        before_done[dispatch.id] == after_done[dispatch.id]))

assert not done_changed, 'un dossier validé a été modifié : %r' % (done_changed,)

env.cr.commit()
print('REPRISE committée')
