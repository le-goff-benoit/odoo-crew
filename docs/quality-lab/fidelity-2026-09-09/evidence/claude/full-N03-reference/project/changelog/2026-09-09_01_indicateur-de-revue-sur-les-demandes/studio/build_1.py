#!/usr/bin/env python3
"""Configuration Studio — indicateur de revue D-22 sur x_lab_request.

Cree, si et seulement si elle manque, la personnalisation suivante :
  x_lab_request.x_studio_needs_review — booleen manuel, stocke, calcule,
  dependant de x_studio_days et x_studio_kind (regle D-22 : revue si la duree
  atteint 7 jours ET que le type est une location).

Tout create/write passe le contexte {"studio": True} : Odoo cree lui-meme
l'identifiant externe sous studio_customization et marque l'enregistrement
comme Studio (web_studio/models/studio_mixin.py). Aucun XML-ID n'est forge a
la main. Le script est idempotent : recherche par cle naturelle
(model + name), creation du manquant, mise a jour des seuls attributs
divergents, puis releve du XML-ID dans created.txt.

Usage : python3 build_1.py [--url URL] [--db DB] [--login L] [--password P]
"""
import argparse
import os
import sys
import xmlrpc.client

MODEL = "x_lab_request"
FIELD = "x_studio_needs_review"

# Regle D-22, ecrite pour safe_eval(mode="exec") : seuls globaux disponibles
# datetime, dateutil, time et self (ir_model.py:39-52). Boucle explicite,
# aucun search, aucun import, aucune ecriture hors du champ calcule.
COMPUTE = (
    "for record in self:\n"
    "    record['%s'] = record['x_studio_days'] >= 7 "
    "and record['x_studio_kind'] == 'rental'\n" % FIELD
)

VALUES = {
    "name": FIELD,
    "field_description": "À revoir",
    "ttype": "boolean",
    "state": "manual",
    "store": True,
    "depends": "x_studio_days,x_studio_kind",
    "compute": COMPUTE,
    # Pose explicitement : l'onchange _onchange_compute (ir_model.py:763-765)
    # ne joue que dans l'editeur Studio, pas sur un create RPC. Sans cette
    # ligne le champ derive resterait editable a l'ecran (cf. H5).
    "readonly": True,
}

CREATED_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "created.txt")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="http://127.0.0.1:60113")
    p.add_argument("--db", default="lab_client")
    p.add_argument("--login", default="admin")
    p.add_argument("--password", default="admin")
    args = p.parse_args()

    common = xmlrpc.client.ServerProxy(args.url + "/xmlrpc/2/common")
    uid = common.authenticate(args.db, args.login, args.password, {})
    if not uid:
        print("ECHEC authentification sur %s / %s" % (args.url, args.db))
        return 1
    models = xmlrpc.client.ServerProxy(args.url + "/xmlrpc/2/object")
    studio_ctx = {"context": {"studio": True}}

    def call(model, method, *pos, **kw):
        return models.execute_kw(args.db, uid, args.password, model, method, list(pos), kw)

    # Le modele doit preexister : on ne le cree pas ici.
    model_ids = call("ir.model", "search", [("model", "=", MODEL)])
    if len(model_ids) != 1:
        print("ECHEC : modele %s introuvable ou en double (%r)" % (MODEL, model_ids))
        return 1
    model_id = model_ids[0]

    # --- cle naturelle : model + name ------------------------------------
    existing = call("ir.model.fields", "search",
                    [("model", "=", MODEL), ("name", "=", FIELD)])
    if len(existing) > 1:
        print("ECHEC : %d champs homonymes %s.%s — anomalie, arret" % (len(existing), MODEL, FIELD))
        return 1

    if existing:
        field_id = existing[0]
        current = call("ir.model.fields", "read", [field_id], fields=list(VALUES))[0]
        diff = {k: v for k, v in VALUES.items() if current.get(k) != v}
        if diff:
            call("ir.model.fields", "write", [field_id], diff, **studio_ctx)
            print("MAJ    ir.model.fields %s (%s) : %s" % (field_id, FIELD, ", ".join(sorted(diff))))
        else:
            print("INCHANGE ir.model.fields %s (%s) : deja conforme" % (field_id, FIELD))
    else:
        vals = dict(VALUES, model_id=model_id, model=MODEL)
        field_id = call("ir.model.fields", "create", vals, **studio_ctx)
        print("CREE   ir.model.fields %s (%s)" % (field_id, FIELD))

    # --- releve du XML-ID cree par Odoo -----------------------------------
    data = call("ir.model.data", "search_read",
                [("model", "=", "ir.model.fields"), ("res_id", "=", field_id)],
                fields=["module", "name"])
    if not data:
        print("ATTENTION : aucun identifiant externe pour ir.model.fields %s ; "
              "le nommer avec odoo_pack.py xmlid sous studio_customization" % field_id)
        return 1
    xmlids = sorted("%s.%s" % (d["module"], d["name"]) for d in data)
    for xid in xmlids:
        print("XML-ID %s" % xid)

    lines = []
    if os.path.exists(CREATED_TXT):
        with open(CREATED_TXT) as fh:
            lines = [l.strip() for l in fh if l.strip()]
    for xid in xmlids:
        if xid not in lines:
            lines.append(xid)
    with open(CREATED_TXT, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("created.txt : %d identifiant(s) externe(s)" % len(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
