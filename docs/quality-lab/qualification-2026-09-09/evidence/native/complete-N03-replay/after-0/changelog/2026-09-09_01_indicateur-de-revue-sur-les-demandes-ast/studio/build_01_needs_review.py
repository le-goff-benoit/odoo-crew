#!/usr/bin/env python3
"""Point 1 — [studio] Indicateur booléen stocké x_studio_needs_review sur x_lab_request.

Décision D-22 (decisions/2026-09-08.md) : revue requise si la demande est une
LOCATION (`x_studio_kind == 'rental'`) ET dure AU MOINS 7 jours (seuil inclus).
Les prêts (`loan`) sont exclus quelle que soit la durée.

Ce script fait exactement ce que ferait Odoo Studio : tout `create` / `write`
passe le contexte {"studio": True}, donc Odoo crée lui-même l'identifiant externe
sous `studio_customization`. Il est IDEMPOTENT : la clé naturelle est
(modèle, nom du champ) ; une deuxième exécution ne crée pas de doublon et se
contente d'aligner la définition si elle a dérivé.

Usage :
    python3 build_01_needs_review.py [--dry-run]
Cible par variables d'environnement (défauts = copie locale du banc) :
    ODOO_URL (http://127.0.0.1:46503) · ODOO_DB (lab_client)
    ODOO_LOGIN (admin) · ODOO_PASSWORD (admin)
"""

import os
import sys
import xmlrpc.client

URL = os.environ.get("ODOO_URL", "http://127.0.0.1:46503")
DB = os.environ.get("ODOO_DB", "lab_client")
LOGIN = os.environ.get("ODOO_LOGIN", "admin")
PASSWORD = os.environ.get("ODOO_PASSWORD", "admin")

MODEL = "x_lab_request"
FIELD = "x_studio_needs_review"
LABEL = "Revue requise"

# Le code tourne dans safe_eval (mode exec) sur `self` : pas d'import, pas d'env.cr.
COMPUTE = (
    "for record in self:\n"
    "    record['%s'] = (record['x_studio_days'] or 0) >= 7 "
    "and record['x_studio_kind'] == 'rental'\n" % FIELD
)
DEPENDS = "x_studio_days,x_studio_kind"

DEFINITION = {
    "ttype": "boolean",
    "field_description": LABEL,
    "store": True,
    "readonly": True,
    "compute": COMPUTE,
    "depends": DEPENDS,
    "state": "manual",
}

STUDIO_CTX = {"context": {"studio": True}}


class Rpc:
    def __init__(self):
        common = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common")
        self.uid = common.authenticate(DB, LOGIN, PASSWORD, {})
        if not self.uid:
            raise SystemExit("authentification refusée sur %s / %s" % (URL, DB))
        self.models = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")

    def __call__(self, model, method, args=None, kwargs=None):
        """args = liste des arguments positionnels de la méthode ORM, dans l'ordre.

        Pour une méthode qui porte sur des enregistrements, le premier est la
        liste d'ids : execute_kw ne l'empaquette pas une seconde fois.
        """
        return self.models.execute_kw(
            DB, self.uid, PASSWORD, model, method, args or [], kwargs or {})


def main():
    dry_run = "--dry-run" in sys.argv
    rpc = Rpc()

    model_ids = rpc("ir.model", "search", [[["model", "=", MODEL]]])
    if not model_ids:
        raise SystemExit(
            "le modèle %s est absent de %s : ce point réutilise l'existant, il ne le crée pas" % (MODEL, DB)
        )
    model_id = model_ids[0]

    # Les champs existants sont réutilisés tels quels : on vérifie leur présence,
    # on ne les renomme pas et on ne les recrée pas (D-22 + journal 2026-08-01).
    existing = rpc(
        "ir.model.fields", "search_read",
        [[["model", "=", MODEL], ["name", "in", ["x_name", "x_studio_days", "x_studio_kind"]]]],
        {"fields": ["name"]},
    )
    missing = {"x_name", "x_studio_days", "x_studio_kind"} - {f["name"] for f in existing}
    if missing:
        raise SystemExit("champs existants attendus introuvables : %s" % ", ".join(sorted(missing)))

    # Clé naturelle : (modèle, nom du champ).
    found = rpc(
        "ir.model.fields", "search_read",
        [[["model", "=", MODEL], ["name", "=", FIELD]]],
        {"fields": ["id", "name"] + list(DEFINITION)},
    )
    if len(found) > 1:
        raise SystemExit("doublon détecté : %s existe %d fois sur %s" % (FIELD, len(found), MODEL))

    if not found:
        if dry_run:
            print("À CRÉER  %s.%s" % (MODEL, FIELD))
            return
        created_id = rpc(
            "ir.model.fields", "create",
            [dict(DEFINITION, name=FIELD, model=MODEL, model_id=model_id)],
            STUDIO_CTX,
        )
        # `create` renvoie un entier ou une liste d'un élément selon la passerelle.
        field_id = created_id[0] if isinstance(created_id, list) else created_id
        action = "CRÉÉ"
    else:
        field_id = found[0]["id"]
        drift = {k: v for k, v in DEFINITION.items() if found[0].get(k) != v}
        if drift and not dry_run:
            rpc("ir.model.fields", "write", [[field_id], drift], STUDIO_CTX)
            action = "ALIGNÉ (%s)" % ", ".join(sorted(drift))
        elif drift:
            print("À ALIGNER %s.%s : %s" % (MODEL, FIELD, ", ".join(sorted(drift))))
            return
        else:
            action = "INCHANGÉ"

    # On ne fabrique pas l'identifiant externe : on relève celui qu'Odoo a créé.
    data = rpc(
        "ir.model.data", "search_read",
        [[["model", "=", "ir.model.fields"], ["res_id", "=", field_id]]],
        {"fields": ["complete_name", "module"]},
    )
    xmlids = [d["complete_name"] for d in data]
    print("%-9s %s.%s (id=%s)" % (action, MODEL, FIELD, field_id))
    print("XML-ID    %s" % (", ".join(xmlids) or "AUCUN — anomalie, le contexte studio n'a pas pris"))

    # created.txt : ce que CETTE release a livré, distinct du Studio historique.
    created = os.path.join(os.path.dirname(os.path.abspath(__file__)), "created.txt")
    known = []
    if os.path.exists(created):
        known = [line.strip() for line in open(created) if line.strip()]
    for xmlid in xmlids:
        if xmlid not in known:
            known.append(xmlid)
    with open(created, "w") as fh:
        fh.write("\n".join(known) + "\n")


if __name__ == "__main__":
    main()
