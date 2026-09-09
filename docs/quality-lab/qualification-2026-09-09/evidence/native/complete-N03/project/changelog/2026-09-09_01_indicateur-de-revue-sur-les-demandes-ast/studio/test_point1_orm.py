"""Scénario ORM rejouable — point 1, comportement de x_studio_needs_review (D-22).

Rejoué sur la copie du client par `/bridge/labctl shell` (variable `env`
disponible, superuser). Il faut ce transport et non XML-RPC : `x_lab_request`
n'a aucun `ir.model.access` et D-22 interdit d'en créer, donc aucun appel RPC
ne peut créer ni relire un enregistrement de ce modèle (vérifié par
test_point1_rpc.py, V6).

Les valeurs attendues viennent de D-22 (decisions/2026-09-08.md), pas du calcul
à tester. Chaque valeur est relue **dans la colonne SQL** après flush : c'est
ce qui prouve que le champ est réellement stocké, et non recalculé à la volée.

Les données de test sont nommées « — recette » et supprimées à la fin ; le
script ne committe jamais.
"""

MODEL = "x_lab_request"
FIELD = "x_studio_needs_review"

echecs = []


def verifie(titre, obtenu, attendu):
    ok = obtenu == attendu
    print(f"[{'OK ' if ok else 'ROUGE'}] {titre} — attendu {attendu}, obtenu {obtenu}")
    if not ok:
        echecs.append(titre)


def valeur_en_base(record):
    """Relit la colonne SQL, après flush : preuve que le champ est stocké."""
    record.flush_recordset()
    record.env.cr.execute(f'SELECT "{FIELD}" FROM "{MODEL}" WHERE id = %s', (record.id,))
    return record.env.cr.fetchone()[0]


Demande = env[MODEL].sudo()
crees = env[MODEL].sudo().browse()

# Précondition : sans le champ, le scénario est rouge d'emblée et ne touche à rien.
if FIELD not in Demande._fields:
    print(f"[ROUGE] précondition — le champ {FIELD} n'existe pas sur {MODEL}")
    print("\nSCÉNARIO ORM ROUGE — 1 vérification(s) en échec")
    raise SystemExit(1)

try:
    # C1 à C6 — la table de vérité de D-22, une demande par ligne
    cas = [
        ("C1 7 jours, location → revue requise", 7, "rental", True),
        ("C2 30 jours, location → revue requise", 30, "rental", True),
        ("C3 6 jours, location → pas de revue", 6, "rental", False),
        ("C4 7 jours, prêt → pas de revue", 7, "loan", False),
        ("C5 30 jours, prêt → pas de revue", 30, "loan", False),
        ("C6 0 jour, type vide → pas de revue", 0, False, False),
    ]
    for titre, jours, nature, attendu in cas:
        demande = Demande.create({
            "x_name": f"{titre} — recette",
            "x_studio_days": jours,
            "x_studio_kind": nature,
        })
        crees |= demande
        verifie(titre, valeur_en_base(demande), attendu)

    # C7 — le franchissement du seuil recalcule le champ stocké, dans les deux sens
    bascule = Demande.create({
        "x_name": "C7 bascule de seuil — recette",
        "x_studio_days": 6,
        "x_studio_kind": "rental",
    })
    crees |= bascule
    verifie("C7 état initial à 6 jours", valeur_en_base(bascule), False)
    bascule.write({"x_studio_days": 7})
    verifie("C7 recalcul après 6 → 7 jours", valeur_en_base(bascule), True)
    bascule.write({"x_studio_days": 6})
    verifie("C7 recalcul après 7 → 6 jours", valeur_en_base(bascule), False)

    # C8 — le changement de nature recalcule aussi
    nature = Demande.create({
        "x_name": "C8 bascule de nature — recette",
        "x_studio_days": 30,
        "x_studio_kind": "rental",
    })
    crees |= nature
    verifie("C8 état initial en location", valeur_en_base(nature), True)
    nature.write({"x_studio_kind": "loan"})
    verifie("C8 recalcul après location → prêt", valeur_en_base(nature), False)

    # Le champ est en lecture seule : une écriture directe ne doit pas survivre
    # au recalcul (un champ calculé stocké sans inverse ignore la valeur donnée).
    nature.invalidate_recordset()
    verifie("C8 valeur relue après invalidation du cache", nature[FIELD], False)

finally:
    crees.unlink()
    env.cr.execute(f'SELECT count(*) FROM "{MODEL}"')
    print(f"nettoyage : {env.cr.fetchone()[0]} enregistrement(s) restant(s) sur {MODEL}")
    env.cr.rollback()

if echecs:
    print(f"\nSCÉNARIO ORM ROUGE — {len(echecs)} vérification(s) en échec")
else:
    print("\nSCÉNARIO ORM VERT — toutes les vérifications passent")
