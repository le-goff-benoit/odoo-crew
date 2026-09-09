"""Scénario RPC — point 1 : indicateur `x_studio_needs_review` (D-22).

Rejouable : `python3 test_1_needs_review.py` (copie `lab_client`).
Rouge avant la construction, vert après.

Ce scénario couvre ce qui est atteignable en XML-RPC : la configuration
elle-même (C10, C11, C12) et, si les droits le permettent un jour, la table de
vérité de D-22. `x_lab_request` n'a aujourd'hui aucun `ir.model.access`
(ir_model.py:2134-2167 : hors superutilisateur, pas d'ACL = pas d'accès), et
D-22 interdit de toucher aux droits : la table de vérité au niveau
enregistrement est donc jouée par `test_1_needs_review_orm.py`. Ce scénario le
constate au lieu de le supposer.
"""
import sys

from rpc_common import FIELD, MODEL, SEED_FIELDS, connect

EXPECTED_COMPUTE_TERMS = ("x_studio_kind", "rental", "x_studio_days", ">= 7")
CASES = [
    # (libellé, type, jours, indicateur attendu, critère)
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


def main():
    call = connect()

    # --- La configuration livrée -------------------------------------------
    fields = call("ir.model.fields", "search_read",
                  [[("model", "=", MODEL), ("name", "=", FIELD)]],
                  {"fields": ["name", "ttype", "store", "compute", "depends",
                              "readonly", "state", "field_description"]})
    check("C12", "un seul %s sur %s" % (FIELD, MODEL), len(fields) == 1,
          "%d trouvé(s)" % len(fields))
    if not fields:
        print("\nRECETTE ROUGE — le champ n'existe pas encore.")
        return 1

    f = fields[0]
    check("C10", "type booléen", f["ttype"] == "boolean", f["ttype"])
    check("C8", "champ stocké", f["store"] is True, "store=%r" % f["store"])
    check("C10", "dépendances déclarées",
          f["depends"] == "x_studio_days,x_studio_kind", repr(f["depends"]))
    check("C10", "champ manuel en lecture seule",
          f["state"] == "manual" and f["readonly"] is True,
          "state=%s readonly=%r" % (f["state"], f["readonly"]))
    compute = f["compute"] or ""
    check("C10", "code du calcul conforme à D-22",
          all(t in compute for t in EXPECTED_COMPUTE_TERMS),
          repr(compute))

    # --- L'identifiant externe, créé par Odoo en contexte studio ------------
    data = call("ir.model.data", "search_read",
                [[("model", "=", "ir.model.fields"), ("res_id", "=", f["id"])]],
                {"fields": ["module", "name", "noupdate"]})
    check("C12", "un seul identifiant externe pour le champ", len(data) == 1,
          "%d trouvé(s)" % len(data))
    if data:
        d = data[0]
        check("C10", "identifiant externe dans studio_customization, noupdate",
              d["module"] == "studio_customization" and d["noupdate"] is True,
              "%s.%s noupdate=%r" % (d["module"], d["name"], d["noupdate"]))
        check("C10", "nommé par Odoo (suffixe uuid), pas à la main",
              not d["name"].startswith("lab_seed_") and len(d["name"].split("_")) >= 2,
              d["name"])

    # --- Les champs existants, intacts --------------------------------------
    for name in SEED_FIELDS:
        seed = call("ir.model.fields", "search_read",
                    [[("model", "=", MODEL), ("name", "=", name)]],
                    {"fields": ["name", "ttype", "compute", "store"]})
        ok = len(seed) == 1 and not seed[0]["compute"]
        detail = "%d trouvé(s)" % len(seed)
        if len(seed) == 1:
            xid = call("ir.model.data", "search_read",
                       [[("model", "=", "ir.model.fields"), ("res_id", "=", seed[0]["id"])]],
                       {"fields": ["module", "name"]})
            ok = ok and len(xid) == 1 and xid[0]["name"] == "lab_seed_%s" % name
            detail = ", ".join("%s.%s" % (x["module"], x["name"]) for x in xid) or "aucun"
        check("C11", "champ existant %s inchangé" % name, ok, detail)

    # --- Table de vérité D-22, si les droits la rendent atteignable ---------
    try:
        call(MODEL, "search_count", [[]])
        joignable = True
    except Exception as exc:  # AccessError attendue tant qu'aucune ACL n'existe
        joignable = False
        print("\nINFO  table de vérité D-22 non jouable en RPC : %s"
              % str(exc).splitlines()[0])
        print("INFO  → jouée en ORM superutilisateur par test_1_needs_review_orm.py")

    if joignable:
        created = []
        try:
            for libelle, kind, days, attendu, critere in CASES:
                rid = call(MODEL, "create", [{
                    "x_name": "%s — recette" % libelle,
                    "x_studio_kind": kind,
                    "x_studio_days": days,
                }])
                created.append(rid)
                got = call(MODEL, "read", [[rid], [FIELD]])[0][FIELD]
                check(critere, "%s → %s" % (libelle, attendu), got == attendu,
                      "lu %r" % got)
            # C6 / C7 : le recalcul suit les deux dépendances
            rid = call(MODEL, "create", [{"x_name": "bascule type — recette",
                                          "x_studio_kind": "loan",
                                          "x_studio_days": 10}])
            created.append(rid)
            call(MODEL, "write", [[rid], {"x_studio_kind": "rental"}])
            check("C6", "prêt 10 j passé en location → vrai",
                  call(MODEL, "read", [[rid], [FIELD]])[0][FIELD] is True)
            rid = call(MODEL, "create", [{"x_name": "bascule durée — recette",
                                          "x_studio_kind": "rental",
                                          "x_studio_days": 10}])
            created.append(rid)
            call(MODEL, "write", [[rid], {"x_studio_days": 3}])
            check("C7", "location 10 j ramenée à 3 j → faux",
                  call(MODEL, "read", [[rid], [FIELD]])[0][FIELD] is False)
            trouve = call(MODEL, "search", [[("id", "in", created), (FIELD, "=", True)]])
            check("C8", "recherche serveur sur l'indicateur stocké",
                  len(trouve) == 3, "%d enregistrement(s) à vrai" % len(trouve))
        finally:
            if created:
                call(MODEL, "unlink", [created])

    echecs = [r for r in results if not r[2]]
    print("\nRECETTE %s — %d contrôle(s), %d échec(s)"
          % ("VERTE" if not echecs else "ROUGE", len(results), len(echecs)))
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
