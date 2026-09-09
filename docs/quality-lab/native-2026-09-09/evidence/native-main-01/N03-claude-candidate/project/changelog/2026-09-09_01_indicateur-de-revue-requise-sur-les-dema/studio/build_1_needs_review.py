"""Construction Studio — point 1 : indicateur `x_studio_needs_review` (D-22).

Idempotent : cherche par clé naturelle (modèle + nom de champ) et ne crée que
ce qui manque. Rejouable sans produire de doublon.
Tout passe par le contexte `studio=True` : Odoo crée lui-même l'identifiant
externe dans `studio_customization`, marqué `noupdate`
(web_studio/models/studio_mixin.py:20, web_studio/models/ir_model.py:49).

    python3 build_1_needs_review.py

Les champs existants `x_name`, `x_studio_days`, `x_studio_kind` ne sont ni
renommés, ni recréés, ni réécrits : une écriture en contexte `studio`
retoucherait leurs identifiants externes `lab_seed_*`.
"""
import os
import sys

from rpc_common import FIELD, MODEL, connect, studio

# D-22 : revue requise si location ET durée >= 7 jours. Les prêts sont exclus.
# Le code tourne dans safe_eval en mode exec, avec `self` (ir_model.py:47).
COMPUTE = (
    "for record in self:\n"
    "    record['x_studio_needs_review'] = "
    "record['x_studio_kind'] == 'rental' and record['x_studio_days'] >= 7\n"
)
VALEURS = {
    "name": FIELD,
    "field_description": "Revue requise",
    "ttype": "boolean",
    "store": True,
    "readonly": True,
    "compute": COMPUTE,
    "depends": "x_studio_days,x_studio_kind",
}
CREATED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "created.txt")


def releve_xmlid(call, field_id):
    """Relève l'identifiant externe qu'Odoo a créé — on n'en fabrique pas.

    À la création, `ir.model.data` sort avec `studio=True` mais `noupdate=False`
    (web_studio/models/ir_model_data.py:12-17). Studio ne pose `noupdate` qu'au
    `write` suivant : `data.write({})` dans `create_studio_model_data`
    (web_studio/models/ir_model.py:62). On rejoue exactement cet appel pour
    converger vers l'état protégé, celui des champs `lab_seed_*` déjà en base.
    """
    data = call("ir.model.data", "search_read",
                [[("model", "=", "ir.model.fields"), ("res_id", "=", field_id)]],
                {"fields": ["module", "name", "noupdate", "studio"]})
    a_marquer = [d["id"] for d in data if not (d["noupdate"] and d["studio"])]
    if a_marquer:
        call("ir.model.data", "write", [a_marquer, {}], studio())
    return ["%s.%s" % (d["module"], d["name"]) for d in data]


def note_created(xmlids):
    connus = []
    if os.path.exists(CREATED):
        with open(CREATED) as fh:
            connus = [l.strip() for l in fh if l.strip()]
    ajouts = [x for x in xmlids if x not in connus]
    if ajouts:
        with open(CREATED, "a") as fh:
            fh.write("".join(x + "\n" for x in ajouts))
    return ajouts


def main():
    call = connect()

    models = call("ir.model", "search_read", [[("model", "=", MODEL)]], {"fields": ["id"]})
    if not models:
        raise SystemExit("modèle %s absent : il doit préexister (D-22)" % MODEL)
    model_id = models[0]["id"]

    existants = call("ir.model.fields", "search_read",
                     [[("model", "=", MODEL), ("name", "=", FIELD)]],
                     {"fields": list(VALEURS) + ["state"]})
    if len(existants) > 1:
        raise SystemExit("%d champs %s : doublon à corriger à la main"
                         % (len(existants), FIELD))

    if not existants:
        field_id = call("ir.model.fields", "create",
                        [dict(VALEURS, model_id=model_id, model=MODEL)],
                        studio())
        action = "créé"
    else:
        field_id = existants[0]["id"]
        ecarts = {k: v for k, v in VALEURS.items() if existants[0].get(k) != v}
        if ecarts:
            call("ir.model.fields", "write", [[field_id], ecarts], studio())
            action = "aligné (%s)" % ", ".join(sorted(ecarts))
        else:
            action = "déjà conforme"

    xmlids = releve_xmlid(call, field_id)
    ajouts = note_created(xmlids)
    print("champ %s : %s (id %s)" % (FIELD, action, field_id))
    print("identifiant(s) externe(s) : %s" % (", ".join(xmlids) or "aucun"))
    print("created.txt : %d ligne(s) ajoutée(s)" % len(ajouts))
    if len(xmlids) != 1:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
