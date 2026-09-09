#!/usr/bin/env python3
"""Scenario RPC — indicateur de revue D-22 sur x_lab_request (release 2026-09-09_01).

Rejouable et autonome : cree ses propres demandes « — recette », relit chaque
valeur cote serveur, nettoie derriere lui. Sort en code 1 au premier ecart.

Couverture (criteres §8 de revue_fonctionnelle.md) :
  - definition du champ (unicite, ttype, state, store, depends) ;
  - table de verite D-22 (§7) : rental 6/7/8+, loan 7/30, jours et type absents ;
  - recalcul a l'ecriture de chacune des deux sources ;
  - stockage reel, prouve par un search sur domaine.

Usage : python3 test_1.py [--url URL] [--db DB] [--login L] [--password P]
"""
import argparse
import sys
import xmlrpc.client

MARK = "— recette needs_review"
FIELD = "x_studio_needs_review"
MODEL = "x_lab_request"

failures = []
checks = 0


def check(label, expected, got):
    global checks
    checks += 1
    if expected == got:
        print("  OK   %-58s = %r" % (label, got))
    else:
        print("  ECHEC %-57s attendu %r, obtenu %r" % (label, expected, got))
        failures.append("%s : attendu %r, obtenu %r" % (label, expected, got))


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

    def call(model, method, *pos, **kw):
        return models.execute_kw(args.db, uid, args.password, model, method, list(pos), kw)

    created = []
    try:
        # --- 1. definition du champ -----------------------------------------
        print("[1] Definition du champ %s" % FIELD)
        defs = call("ir.model.fields", "search_read",
                    [("model", "=", MODEL), ("name", "=", FIELD)],
                    fields=["id", "ttype", "state", "store", "depends", "readonly"])
        check("nombre d'enregistrements ir.model.fields", 1, len(defs))
        if not defs:
            raise AssertionError("le champ %s n'existe pas sur %s" % (FIELD, MODEL))
        d = defs[0]
        check("ttype", "boolean", d["ttype"])
        check("state", "manual", d["state"])
        check("store", True, d["store"])
        check("depends (les deux sources, et rien d'autre)",
              ["x_studio_days", "x_studio_kind"],
              sorted((d["depends"] or "").replace(" ", "").split(",")))

        # --- 2. table de verite D-22 ----------------------------------------
        print("[2] Table de verite D-22 a la creation")
        cases = [
            ("rental 6 jours", {"x_studio_kind": "rental", "x_studio_days": 6}, False),
            ("rental 7 jours (seuil inclus)", {"x_studio_kind": "rental", "x_studio_days": 7}, True),
            ("rental 12 jours", {"x_studio_kind": "rental", "x_studio_days": 12}, True),
            ("loan 7 jours", {"x_studio_kind": "loan", "x_studio_days": 7}, False),
            ("loan 30 jours", {"x_studio_kind": "loan", "x_studio_days": 30}, False),
            ("rental sans jours renseignes", {"x_studio_kind": "rental"}, False),
            ("type non renseigne, 30 jours", {"x_studio_days": 30}, False),
            ("ni type ni jours", {}, False),
        ]
        ids_true = []
        for label, vals, expected in cases:
            vals = dict(vals, x_name="%s %s" % (label, MARK))
            rid = call(MODEL, "create", vals)
            created.append(rid)
            got = call(MODEL, "read", [rid], fields=[FIELD])[0][FIELD]
            check("creation : " + label, expected, got)
            if expected:
                ids_true.append(rid)

        # --- 3. recalcul a l'ecriture ---------------------------------------
        print("[3] Recalcul a l'ecriture des sources")
        r1 = call(MODEL, "create", {"x_name": "recalcul jours %s" % MARK,
                                    "x_studio_kind": "rental", "x_studio_days": 6})
        created.append(r1)
        check("avant ecriture (rental 6)", False, call(MODEL, "read", [r1], fields=[FIELD])[0][FIELD])
        call(MODEL, "write", [r1], {"x_studio_days": 9})
        check("apres x_studio_days = 9", True, call(MODEL, "read", [r1], fields=[FIELD])[0][FIELD])
        ids_true.append(r1)

        r2 = call(MODEL, "create", {"x_name": "recalcul type %s" % MARK,
                                    "x_studio_kind": "rental", "x_studio_days": 9})
        created.append(r2)
        check("avant ecriture (rental 9)", True, call(MODEL, "read", [r2], fields=[FIELD])[0][FIELD])
        call(MODEL, "write", [r2], {"x_studio_kind": "loan"})
        check("apres x_studio_kind = loan", False, call(MODEL, "read", [r2], fields=[FIELD])[0][FIELD])

        r3 = call(MODEL, "create", {"x_name": "recalcul type inverse %s" % MARK,
                                    "x_studio_kind": "loan", "x_studio_days": 9})
        created.append(r3)
        check("avant ecriture (loan 9)", False, call(MODEL, "read", [r3], fields=[FIELD])[0][FIELD])
        call(MODEL, "write", [r3], {"x_studio_kind": "rental"})
        check("apres x_studio_kind = rental", True, call(MODEL, "read", [r3], fields=[FIELD])[0][FIELD])
        ids_true.append(r3)

        # --- 4. stockage reel, prouve par un search sur domaine -------------
        print("[4] Stockage : recherche sur domaine")
        found = call(MODEL, "search", [(FIELD, "=", True), ("id", "in", created)])
        check("search [(needs_review,=,True)] sur le jeu d'essai",
              sorted(ids_true), sorted(found))
        found_false = call(MODEL, "search", [(FIELD, "=", False), ("id", "in", created)])
        check("search [(needs_review,=,False)] : complement exact",
              sorted(set(created) - set(ids_true)), sorted(found_false))

    except xmlrpc.client.Fault as exc:
        print("  ECHEC Fault RPC : %s" % (exc.faultString or "").strip().splitlines()[-1:])
        failures.append("Fault RPC : %s" % exc.faultString)
    except AssertionError as exc:
        failures.append(str(exc))
    finally:
        if created:
            try:
                call(MODEL, "unlink", created)
                reste = call(MODEL, "search_count", [("x_name", "like", MARK)])
                print("[nettoyage] %d enregistrement(s) supprime(s), reste %d"
                      % (len(created), reste))
                if reste:
                    failures.append("nettoyage incomplet : %d enregistrement(s) « recette » restant(s)" % reste)
            except xmlrpc.client.Fault as exc:
                failures.append("nettoyage impossible : %s" % exc.faultString)

    print("")
    if failures:
        print("SCENARIO ROUGE — %d controle(s) en echec sur %d" % (len(failures), checks))
        for f in failures:
            print("  - %s" % f)
        return 1
    print("SCENARIO VERT — %d controles passes" % checks)
    return 0


if __name__ == "__main__":
    sys.exit(main())
