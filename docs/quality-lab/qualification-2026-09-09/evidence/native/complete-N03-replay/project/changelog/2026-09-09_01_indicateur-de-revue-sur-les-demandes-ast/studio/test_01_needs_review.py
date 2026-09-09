#!/usr/bin/env python3
"""Scénario de recette — point 1 : x_studio_needs_review sur x_lab_request (D-22).

Rejouable : crée ses propres données « — recette », vérifie les valeurs relues
DEPUIS LE SERVEUR (jamais la valeur envoyée), puis nettoie systématiquement.
Rouge avant la configuration, vert après. Sortie 0 = tout vert, 1 = au moins un
critère rouge.

Usage : python3 test_01_needs_review.py
Cible : mêmes variables d'environnement que build_01_needs_review.py.
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
TAG = "— recette"

results = []


def check(criterion, label, ok, detail=""):
    results.append((criterion, label, ok, detail))
    print("%-4s %-5s %s%s" % (criterion, "VERT" if ok else "ROUGE", label, (" · " + detail) if detail else ""))


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
    rpc = Rpc()
    created_ids = []

    # ---- C1 : définition du champ -------------------------------------------------
    defs = rpc("ir.model.fields", "search_read",
               [[["model", "=", MODEL], ["name", "=", FIELD]]],
               {"fields": ["id", "ttype", "store", "readonly", "compute", "depends", "state"]})
    if not defs:
        check("C1", "le champ %s existe sur %s" % (FIELD, MODEL), False, "champ absent")
        summary()
        return
    d = defs[0]
    check("C1", "booléen stocké calculé, readonly, manual, depends sur les deux champs",
          d["ttype"] == "boolean" and d["store"] and d["readonly"] and bool(d["compute"])
          and d["state"] == "manual"
          and sorted(p.strip() for p in (d["depends"] or "").split(",")) == ["x_studio_days", "x_studio_kind"],
          "ttype=%s store=%s readonly=%s depends=%s state=%s" % (
              d["ttype"], d["store"], d["readonly"], d["depends"], d["state"]))

    def make(name, kind, days):
        vals = {"x_name": "%s %s" % (name, TAG), "x_studio_days": days}
        if kind:
            vals["x_studio_kind"] = kind
        rid = rpc(MODEL, "create", [vals])
        # `create` renvoie un entier ou une liste d'un élément selon la passerelle.
        rid = rid[0] if isinstance(rid, list) else rid
        created_ids.append(rid)
        return rid

    def read_flag(rid):
        return rpc(MODEL, "read", [[rid]], {"fields": [FIELD]})[0][FIELD]

    try:
        # ---- C2 : location à 7 jours = seuil inclus --------------------------------
        r7 = make("Location 7j", "rental", 7)
        check("C2", "location de 7 jours (seuil inclus) → True", read_flag(r7) is True)

        # ---- C3 : 6 jours non, 30 jours oui ----------------------------------------
        r6 = make("Location 6j", "rental", 6)
        r30 = make("Location 30j", "rental", 30)
        check("C3", "location de 6 jours → False et de 30 jours → True",
              read_flag(r6) is False and read_flag(r30) is True)

        # ---- C4 : les prêts sont exclus quelle que soit la durée --------------------
        l7 = make("Pret 7j", "loan", 7)
        l30 = make("Pret 30j", "loan", 30)
        check("C4", "prêt de 7 et de 30 jours → False",
              read_flag(l7) is False and read_flag(l30) is False)

        # ---- C5 : valeurs vides ou négatives ---------------------------------------
        empty = make("Sans genre 10j", None, 10)
        zero = make("Location 0j", "rental", 0)
        neg = make("Location -3j", "rental", -3)
        check("C5", "genre vide, durée nulle ou négative → False, sans erreur",
              read_flag(empty) is False and read_flag(zero) is False and read_flag(neg) is False)

        # ---- C6 : recalcul au fil des modifications --------------------------------
        moving = make("Location evolutive", "rental", 6)
        before = read_flag(moving)
        rpc(MODEL, "write", [[moving], {"x_studio_days": 7}])
        after_days = read_flag(moving)
        rpc(MODEL, "write", [[moving], {"x_studio_kind": "loan"}])
        after_kind = read_flag(moving)
        check("C6", "6j→7j bascule à True, puis rental→loan revient à False",
              before is False and after_days is True and after_kind is False,
              "%s → %s → %s" % (before, after_days, after_kind))

        # ---- C7 : les champs existants sont intacts, aucun doublon ------------------
        seeds = rpc("ir.model.data", "search_read",
                    [[["module", "=", "studio_customization"], ["name", "like", "lab_seed_"]]],
                    {"fields": ["complete_name", "res_id"]})
        seed_map = {s["complete_name"]: s["res_id"] for s in seeds}
        legacy = rpc("ir.model.fields", "search_read",
                     [[["model", "=", MODEL], ["name", "in", ["x_name", "x_studio_days", "x_studio_kind"]]]],
                     {"fields": ["id", "name"]})
        expected = {
            "studio_customization.lab_seed_x_name": "x_name",
            "studio_customization.lab_seed_x_studio_days": "x_studio_days",
            "studio_customization.lab_seed_x_studio_kind": "x_studio_kind",
        }
        by_id = {f["id"]: f["name"] for f in legacy}
        intact = len(legacy) == 3 and all(
            by_id.get(seed_map.get(xid)) == fname for xid, fname in expected.items())
        check("C7", "x_name / x_studio_days / x_studio_kind inchangés, aucun doublon",
              intact, "%d champ(s) d'origine, %d XML-ID lab_seed_*" % (len(legacy), len(seed_map)))

        # ---- C8 : un seul champ, un seul XML-ID pour l'indicateur -------------------
        dup = rpc("ir.model.fields", "search_count", [[["model", "=", MODEL], ["name", "=", FIELD]]])
        xmlids = rpc("ir.model.data", "search_count",
                     [[["model", "=", "ir.model.fields"], ["res_id", "=", defs[0]["id"]]]])
        check("C8", "exactement un champ %s et un identifiant externe" % FIELD,
              dup == 1 and xmlids == 1, "champs=%d xmlids=%d" % (dup, xmlids))

    finally:
        # On nettoie sur la clé naturelle : robuste même si le scénario s'est arrêté en route.
        leftovers = rpc(MODEL, "search", [[["x_name", "like", TAG]]])
        if leftovers:
            rpc(MODEL, "unlink", [leftovers])
        rest = rpc(MODEL, "search_count", [[["x_name", "like", TAG]]])
        check("nett", "données de recette supprimées", rest == 0, "%d reste(nt)" % rest)

    summary()


def summary():
    red = [r for r in results if not r[2]]
    print("\nRECETTE studio point 1 : %d/%d vert(s)%s" % (
        len(results) - len(red), len(results),
        "" if not red else " · ROUGE : " + ", ".join(r[0] for r in red)))
    sys.exit(1 if red else 0)


if __name__ == "__main__":
    main()
