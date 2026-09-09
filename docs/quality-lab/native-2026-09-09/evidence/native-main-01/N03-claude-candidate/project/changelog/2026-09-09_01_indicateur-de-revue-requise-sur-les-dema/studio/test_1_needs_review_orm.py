"""Scénario ORM — point 1 : table de vérité D-22 sur les enregistrements.

Rejouable : `/bridge/labctl shell changelog/<release>/studio/test_1_needs_review_orm.py`
(ou `odoo-stack.sh odoo-shell lab_client`). `env` est fourni par le shell Odoo.

Pourquoi pas en XML-RPC : `x_lab_request` n'a aucun `ir.model.access`
(ir_model.py:2134-2167), et D-22 interdit de toucher aux droits. On passe donc
en superutilisateur (`sudo()`), qui est le seul accès possible aujourd'hui.
Les valeurs sont relues **après invalidation du cache**, donc côté serveur.

Rouge avant la construction (le champ n'existe pas), vert après.
"""

FIELD = "x_studio_needs_review"
MODEL = "x_lab_request"
MARQUE = "— recette"

CASES = [
    ("location 7 jours — seuil inclus", "rental", 7, True, "C1"),
    ("location 6 jours — sous le seuil", "rental", 6, False, "C2"),
    ("location 30 jours", "rental", 30, True, "C3"),
    ("prêt 7 jours — exclu", "loan", 7, False, "C4"),
    ("prêt 30 jours — exclu", "loan", 30, False, "C4"),
    ("sans type", False, 10, False, "C5"),
    ("location 0 jour", "rental", 0, False, "C5"),
    ("location -3 jours", "rental", -3, False, "C5"),
]

results = []


def check(critere, libelle, ok, detail=""):
    results.append((critere, libelle, ok, detail))
    print("%s %-4s %s%s" % ("OK  " if ok else "ÉCHEC", critere, libelle,
                            (" — " + detail) if detail else ""))


M = env[MODEL].sudo()

if FIELD not in M._fields:
    print("ÉCHEC C1-C9 le champ %s n'existe pas sur %s" % (FIELD, MODEL))
    print("\nRECETTE ROUGE — le champ n'existe pas encore.")
else:
    # C8 : le champ est réellement une colonne de la table.
    env.cr.execute(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name = %s AND column_name = %s", (MODEL, FIELD))
    check("C8", "colonne %s présente en base" % FIELD, bool(env.cr.fetchone()))

    # C9 : les enregistrements créés AVANT l'ajout du champ portent la valeur.
    avant = M.search([("x_name", "like", "reprise")])
    if avant:
        attendus = {
            r.id: (r.x_studio_kind == "rental" and r.x_studio_days >= 7)
            for r in avant
        }
        M.invalidate_recordset([FIELD])
        ok = all(r[FIELD] == attendus[r.id] for r in avant)
        check("C9", "reprise des %d enregistrement(s) antérieur(s)" % len(avant),
              ok, ", ".join("%s=%r" % (r.x_name, r[FIELD]) for r in avant))
    else:
        check("C9", "aucun enregistrement antérieur à reprendre", False,
              "jouer d'abord reprise_avant_1_needs_review.py")

    crees = M.browse()
    try:
        for libelle, kind, days, attendu, critere in CASES:
            rec = M.create({"x_name": "%s %s" % (libelle, MARQUE),
                            "x_studio_kind": kind, "x_studio_days": days})
            crees |= rec
            rec.invalidate_recordset([FIELD])
            check(critere, "%s → %s" % (libelle, attendu),
                  rec[FIELD] == attendu, "lu %r" % rec[FIELD])

        # C6 : la dépendance sur le type déclenche le recalcul.
        rec = M.create({"x_name": "bascule type %s" % MARQUE,
                        "x_studio_kind": "loan", "x_studio_days": 10})
        crees |= rec
        check("C6", "prêt 10 j avant bascule → faux", rec[FIELD] is False)
        rec.x_studio_kind = "rental"
        rec.invalidate_recordset([FIELD])
        check("C6", "prêt 10 j passé en location → vrai", rec[FIELD] is True)

        # C7 : la dépendance sur la durée déclenche le recalcul.
        rec = M.create({"x_name": "bascule durée %s" % MARQUE,
                        "x_studio_kind": "rental", "x_studio_days": 10})
        crees |= rec
        check("C7", "location 10 j avant bascule → vrai", rec[FIELD] is True)
        rec.x_studio_days = 3
        rec.invalidate_recordset([FIELD])
        check("C7", "location 10 j ramenée à 3 j → faux", rec[FIELD] is False)

        # C8 : la valeur est cherchable côté serveur, donc bien stockée.
        vrais = M.search([("id", "in", crees.ids), (FIELD, "=", True)])
        check("C8", "recherche serveur sur l'indicateur", len(vrais) == 3,
              "%d enregistrement(s) à vrai" % len(vrais))
    finally:
        # Nettoyage : la recette ne laisse rien derrière elle.
        (crees | M.search([("x_name", "like", MARQUE)])
              | M.search([("x_name", "like", "reprise")])).unlink()
        env.cr.commit()
        reste = M.search_count([("x_name", "like", MARQUE)])
        check("—", "nettoyage des données de recette", reste == 0,
              "%d restant(s)" % reste)

    echecs = [r for r in results if not r[2]]
    print("\nRECETTE %s — %d contrôle(s), %d échec(s)"
          % ("VERTE" if not echecs else "ROUGE", len(results), len(echecs)))
