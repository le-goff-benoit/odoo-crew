"""Point 1 — indicateur de revue sur les demandes Aster (décision D-22).

Crée sur `x_lab_request` le champ booléen calculé et stocké
`x_studio_needs_review` : vrai si et seulement si la demande est une location
(`x_studio_kind == 'rental'`) d'au moins 7 jours. Les prêts sont exclus, même
au-delà du seuil.

Le script est idempotent : il cherche le champ par sa clé naturelle
(modèle + nom), ne crée que ce qui manque, et ne réécrit une définition que si
elle a divergé. Tout passe par le contexte `studio=True`, donc Odoo crée
lui-même l'identifiant externe sous `studio_customization`.

    python3 build_needs_review.py

Rien n'est touché en dehors de ce champ : `x_name`, `x_studio_days` et
`x_studio_kind` sont utilisés tels quels, ni renommés ni recréés.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lab_rpc import STUDIO, connect  # noqa: E402

MODEL = "x_lab_request"
FIELD = "x_studio_needs_review"

# Le calcul tourne en `safe_eval` (odoo/addons/base/models/ir_model.py:46) :
# pas d'import, pas de curseur, le corps itère sur `self`.
COMPUTE = (
    "for record in self:\n"
    "    record['x_studio_needs_review'] = bool(\n"
    "        (record['x_studio_days'] or 0) >= 7\n"
    "        and record['x_studio_kind'] == 'rental'\n"
    "    )\n"
)
DEPENDS = "x_studio_days,x_studio_kind"

DEFINITION = {
    "ttype": "boolean",
    "field_description": FIELD,
    "store": True,
    "readonly": True,
    "compute": COMPUTE,
    "depends": DEPENDS,
}


def main():
    call = connect()

    model_ids = call("ir.model", "search", [[("model", "=", MODEL)]])
    if not model_ids:
        raise SystemExit(
            f"le modèle {MODEL} est absent de cette base : "
            "il est un prérequis, ce script ne le crée pas"
        )
    model_id = model_ids[0]

    existing = call(
        "ir.model.fields",
        "search_read",
        [[("model", "=", MODEL), ("name", "=", FIELD)]],
        {"fields": ["id", *DEFINITION]},
    )

    if not existing:
        field_id = call(
            "ir.model.fields",
            "create",
            [dict(DEFINITION, name=FIELD, model=MODEL, model_id=model_id)],
            STUDIO,
        )
        print(f"champ créé : {MODEL}.{FIELD} (id {field_id})")
    else:
        field_id = existing[0]["id"]
        drift = {k: v for k, v in DEFINITION.items() if existing[0].get(k) != v}
        if drift:
            call("ir.model.fields", "write", [[field_id], drift], STUDIO)
            print(f"champ réaligné : {MODEL}.{FIELD} → {', '.join(sorted(drift))}")
        else:
            print(f"champ déjà conforme : {MODEL}.{FIELD} (id {field_id}) — rien à faire")

    # On ne fabrique pas l'identifiant externe : on relève celui qu'Odoo a créé.
    data = call(
        "ir.model.data",
        "search_read",
        [[("model", "=", "ir.model.fields"), ("res_id", "=", field_id)]],
        {"fields": ["module", "name", "noupdate"]},
    )
    if not data:
        raise SystemExit(
            f"aucun identifiant externe pour {MODEL}.{FIELD} : "
            "le contexte studio n'a pas été pris en compte"
        )
    xmlid = f"{data[0]['module']}.{data[0]['name']}"

    # Odoo ne marque `noupdate` qu'au premier *write* en contexte studio
    # (web_studio/models/ir_model_data.py) : à la création seule, le champ
    # resterait exposé à une mise à niveau de module. On rejoue donc le chemin
    # que Studio emprunte dès la première retouche du champ, plutôt que
    # d'écrire l'identifiant externe à la main.
    if not data[0]["noupdate"]:
        call("ir.model.fields", "write", [[field_id], {"field_description": FIELD}], STUDIO)
        data = call(
            "ir.model.data",
            "search_read",
            [[("model", "=", "ir.model.fields"), ("res_id", "=", field_id)]],
            {"fields": ["module", "name", "noupdate"]},
        )
        print("identifiant externe passé en noupdate (chemin Studio)")

    print(f"identifiant externe : {xmlid} (noupdate={data[0]['noupdate']})")

    created = os.path.join(os.path.dirname(os.path.abspath(__file__)), "created.txt")
    known = []
    if os.path.exists(created):
        known = [line.strip() for line in open(created, encoding="utf-8") if line.strip()]
    if xmlid not in known:
        known.append(xmlid)
        with open(created, "w", encoding="utf-8") as fh:
            fh.write("\n".join(known) + "\n")
        print(f"ajouté à created.txt : {xmlid}")


if __name__ == "__main__":
    main()
