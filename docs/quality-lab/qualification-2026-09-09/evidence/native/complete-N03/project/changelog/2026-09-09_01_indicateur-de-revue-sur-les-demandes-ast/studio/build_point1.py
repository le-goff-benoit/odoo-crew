"""Construction Studio — point 1 : indicateur de revue sur x_lab_request (D-22).

Fait exactement ce que ferait un humain dans Studio : ajouter un champ manuel
calculé et stocké sur un modèle existant, en contexte `studio=True`, ce qui
laisse Odoo créer lui-même l'identifiant externe sous `studio_customization`
(web_studio/models/studio_mixin.py).

Idempotent : cherche d'abord par clé naturelle (modèle + nom du champ) et ne
crée que ce qui manque. Relève ensuite l'identifiant externe créé par Odoo et
l'écrit dans created.txt.

Périmètre strict (D-22) : un seul champ. Aucun droit, aucune vue, aucune
automatisation, aucun champ existant renommé ni recréé.

Usage : python3 build_point1.py
"""

import os
import sys

from lab_rpc import COMPUTE, DEPENDS, FIELD, MODEL, STUDIO, connect

ICI = os.path.dirname(os.path.abspath(__file__))
CREATED = os.path.join(ICI, "created.txt")

DEFINITION = {
    "name": FIELD,
    "field_description": "Revue requise",
    "ttype": "boolean",
    "state": "manual",
    "store": True,
    "readonly": True,
    "depends": DEPENDS,
    "compute": COMPUTE,
}


def main():
    call = connect()

    modeles = call("ir.model", "search_read", [[("model", "=", MODEL)]], {"fields": ["id", "name"]})
    if not modeles:
        raise SystemExit(f"modèle {MODEL} absent de la base : rien à faire ici")
    model_id = modeles[0]["id"]

    # Clé naturelle : modèle + nom du champ. On ne crée que ce qui manque.
    existants = call(
        "ir.model.fields",
        "search_read",
        [[("model", "=", MODEL), ("name", "=", FIELD)]],
        {"fields": ["id", "ttype", "store", "readonly", "depends", "compute"]},
    )
    if existants:
        champ = existants[0]
        field_id = champ["id"]
        ecarts = {
            cle: (champ.get(cle), attendu)
            for cle, attendu in DEFINITION.items()
            if cle in champ and champ.get(cle) != attendu
        }
        if ecarts:
            call("ir.model.fields", "write", [[field_id], {k: v for k, v in DEFINITION.items() if k in ecarts}], STUDIO)
            print(f"champ {FIELD} déjà présent — aligné sur la spec ({', '.join(ecarts)})")
        else:
            print(f"champ {FIELD} déjà présent et conforme — rien à créer")
    else:
        field_id = call("ir.model.fields", "create", [dict(DEFINITION, model_id=model_id, model=MODEL)], STUDIO)
        print(f"champ {FIELD} créé (ir.model.fields id={field_id})")

    # On ne fabrique pas d'identifiant externe : on relève celui qu'Odoo a créé.
    donnees = call(
        "ir.model.data",
        "search_read",
        [[("model", "=", "ir.model.fields"), ("res_id", "=", field_id)]],
        {"fields": ["module", "name"]},
    )
    if not donnees:
        raise SystemExit(
            f"aucun identifiant externe pour {FIELD} : le contexte studio=True n'a pas été appliqué"
        )
    xmlids = sorted(f"{d['module']}.{d['name']}" for d in donnees)

    # created.txt = ce que CETTE release a livré, sans doublon de ligne.
    deja = []
    if os.path.exists(CREATED):
        deja = [ligne.strip() for ligne in open(CREATED, encoding="utf-8") if ligne.strip()]
    lignes = sorted(set(deja) | set(xmlids))
    with open(CREATED, "w", encoding="utf-8") as fichier:
        fichier.write("\n".join(lignes) + "\n")
    print("identifiant(s) externe(s) relevé(s) : " + ", ".join(xmlids))
    return 0


if __name__ == "__main__":
    sys.exit(main())
