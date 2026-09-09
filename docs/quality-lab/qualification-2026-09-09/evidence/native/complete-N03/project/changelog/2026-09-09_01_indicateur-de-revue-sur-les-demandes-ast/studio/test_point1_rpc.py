"""Scénario RPC rejouable — point 1, définition du champ x_studio_needs_review.

Rouge avant la configuration, vert après. Traverse le vrai XML-RPC sur la copie
du client. Ne prouve ni le rendu visuel, ni les droits d'un autre utilisateur.

Ce que ce scénario NE peut pas couvrir : le comportement au niveau
enregistrement. `x_lab_request` n'a aucun `ir.model.access` en base et D-22
interdit d'en créer ; tout `create`/`read` de ce modèle est donc refusé en
XML-RPC, y compris à `admin`. Le scénario le vérifie explicitement (V6) pour
que cette limite soit prouvée et non supposée. Le comportement est couvert par
test_point1_orm.py.

Usage : python3 test_point1_rpc.py
"""

import sys

from lab_rpc import COMPUTE, DEPENDS, FIELD, MODEL, connect

ATTENDU_ACCES_REFUSE = "You are not allowed to create"

echecs = []


def verifie(titre, condition, detail=""):
    etat = "OK " if condition else "ROUGE"
    print(f"[{etat}] {titre}" + (f" — {detail}" if detail else ""))
    if not condition:
        echecs.append(titre)


def main():
    call = connect()

    champs = call(
        "ir.model.fields",
        "search_read",
        [[("model", "=", MODEL)]],
        {"fields": ["name", "ttype", "state", "store", "readonly", "depends", "compute", "field_description"]},
    )
    par_nom = {c["name"]: c for c in champs}

    # V1 — le champ existe
    cible = par_nom.get(FIELD)
    verifie("V1 le champ x_studio_needs_review existe", cible is not None)
    if cible is None:
        return conclure()

    # V2 — sa définition est bien celle de la spec (C9)
    verifie("V2 ttype = boolean", cible["ttype"] == "boolean", cible["ttype"])
    verifie("V2 state = manual", cible["state"] == "manual", cible["state"])
    verifie("V2 store = True", cible["store"] is True, str(cible["store"]))
    verifie("V2 readonly = True", cible["readonly"] is True, str(cible["readonly"]))
    verifie("V2 depends = x_studio_days,x_studio_kind", (cible["depends"] or "") == DEPENDS, repr(cible["depends"]))
    verifie("V2 compute conforme", (cible["compute"] or "") == COMPUTE, repr(cible["compute"]))

    # V3 — identifiant externe sous studio_customization (C9)
    xmlids = call(
        "ir.model.data",
        "search_read",
        [[("model", "=", "ir.model.fields"), ("res_id", "=", cible["id"])]],
        {"fields": ["module", "name", "noupdate"]},
    )
    verifie(
        "V3 identifiant externe dans studio_customization",
        len(xmlids) == 1 and xmlids[0]["module"] == "studio_customization",
        ", ".join(f"{x['module']}.{x['name']}" for x in xmlids) or "aucun",
    )

    # V4 — aucun doublon, les champs d'origine sont intacts (C10)
    revue = [c["name"] for c in champs if "needs_review" in c["name"]]
    verifie("V4 un seul champ 'needs_review'", len(revue) == 1, ", ".join(revue))
    seeds = call(
        "ir.model.data",
        "search_read",
        [[("module", "=", "studio_customization"), ("name", "like", "lab_seed_%")]],
        {"fields": ["name", "model", "res_id"]},
    )
    attendus = {"lab_seed_model", "lab_seed_x_name", "lab_seed_x_studio_days", "lab_seed_x_studio_kind"}
    verifie(
        "V4 les XML-ID lab_seed_* d'origine sont intacts",
        {s["name"] for s in seeds} == attendus,
        ", ".join(sorted(s["name"] for s in seeds)),
    )
    par_xmlid = {s["name"]: s for s in seeds}
    for nom in ("x_name", "x_studio_days", "x_studio_kind"):
        verifie(f"V4 {nom} toujours présent et manuel", par_nom.get(nom, {}).get("state") == "manual")
        # Un champ recréé aurait un nouvel id : l'identité id ↔ XML-ID d'origine
        # prouve qu'il a été réutilisé et non reconstruit.
        seed = par_xmlid.get(f"lab_seed_{nom}", {})
        verifie(
            f"V4 lab_seed_{nom} pointe toujours le même ir.model.fields",
            seed.get("model") == "ir.model.fields" and seed.get("res_id") == par_nom.get(nom, {}).get("id"),
            f"XML-ID → {seed.get('res_id')}, champ → {par_nom.get(nom, {}).get('id')}",
        )

    # V5 — rien d'autre n'a été créé sur ce modèle (C13)
    for modele, domaine, libelle in (
        ("ir.model.access", [("model_id.model", "=", MODEL)], "aucune ACL"),
        ("ir.rule", [("model_id.model", "=", MODEL)], "aucune règle d'enregistrement"),
        ("ir.ui.view", [("model", "=", MODEL)], "aucune vue"),
        ("base.automation", [("model_name", "=", MODEL)], "aucune automatisation"),
        ("ir.actions.server", [("model_name", "=", MODEL)], "aucune action serveur"),
        ("ir.cron", [("model_id.model", "=", MODEL)], "aucune action planifiée"),
    ):
        n = call(modele, "search_count", [domaine])
        verifie(f"V5 {libelle} sur {MODEL}", n == 0, f"{n} trouvé(s)")

    # V6 — la limite d'accès est prouvée, pas supposée
    try:
        call(MODEL, "create", [{"x_name": "sonde — recette"}], {"context": {"studio": True}})
        verifie("V6 création refusée faute d'ACL (limite documentée)", False, "la création a réussi : l'ACL a changé")
    except Exception as erreur:  # xmlrpc.client.Fault
        message = str(erreur)
        verifie(
            "V6 création refusée faute d'ACL (limite documentée)",
            ATTENDU_ACCES_REFUSE in message,
            message.splitlines()[0][:120],
        )

    return conclure()


def conclure():
    if echecs:
        print(f"\nSCÉNARIO RPC ROUGE — {len(echecs)} vérification(s) en échec")
        return 1
    print("\nSCÉNARIO RPC VERT — toutes les vérifications passent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
