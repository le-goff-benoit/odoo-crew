"""Reprise des totaux figés des dossiers en brouillon (D-12).

À exécuter dans un shell Odoo sur la copie synthétique :

    /bridge/labctl shell changelog/<release>/reprise/reprise_brouillons.py

Règle appliquée : pour les seuls dossiers `state == 'draft'`, `snapshot_total`
devient la somme `quantity * price` des lignes non annulées. Les dossiers
validés sont lus pour le rapport, jamais écrits. La comparaison est faite sur
l'égalité exacte du flottant, sans tolérance monétaire : un écart de 0,004 est
un écart à corriger.

Le script est idempotent : il n'écrit que les enregistrements réellement
divergents, donc une seconde exécution ne modifie rien.
"""

drafts = env['lab.dispatch'].search([('state', '=', 'draft')], order='id')
frozen = env['lab.dispatch'].search([('state', '!=', 'draft')], order='id')

print("=== Reprise des brouillons — lab.dispatch ===")
print(f"brouillons examinés : {len(drafts)} · dossiers figés ignorés : {len(frozen)}")

modified = env['lab.dispatch']
for dispatch in drafts:
    expected = dispatch._get_lines_total()
    current = dispatch.snapshot_total
    if current == expected:
        print(f"  = id={dispatch.id} {dispatch.name}: {current!r} déjà conforme")
        continue
    dispatch.snapshot_total = expected
    modified |= dispatch
    print(f"  ~ id={dispatch.id} {dispatch.name}: {current!r} -> {expected!r}")

for dispatch in frozen:
    print(f"  · id={dispatch.id} {dispatch.name} ({dispatch.state}): {dispatch.snapshot_total!r} inchangé (figé)")

print(f"REPRISE modifiés={len(modified)} inchangés={len(drafts) - len(modified)} figés={len(frozen)}")
env.cr.commit()
