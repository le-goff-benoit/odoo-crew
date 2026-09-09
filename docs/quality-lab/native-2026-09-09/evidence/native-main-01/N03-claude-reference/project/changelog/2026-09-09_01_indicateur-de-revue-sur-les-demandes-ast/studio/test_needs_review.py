"""Recette du point 1 — indicateur de revue sur les demandes Aster (D-22).

Scénario XML-RPC rejouable sur la copie locale. Il crée ses propres demandes
(suffixées « — recette »), relit les valeurs **côté serveur** après écriture, et
nettoie tout derrière lui.

Particularité assumée, et signalée dans la revue (contradiction C1) :
`x_lab_request` ne porte **aucun droit d'accès**, si bien que personne — pas
même l'administrateur — ne peut créer ou lire une demande par RPC. Le scénario
pose donc un droit d'accès **temporaire**, hors contexte `studio` (il n'a donc
pas d'identifiant externe et n'entre pas dans le pack), et le retire en fin de
parcours. Le dernier contrôle vérifie qu'il ne reste rien.

    python3 test_needs_review.py

Sortie : une ligne par contrôle, puis un verdict. Code de retour non nul si un
contrôle échoue.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import xmlrpc.client  # noqa: E402

from lab_rpc import connect  # noqa: E402

MODEL = "x_lab_request"
FIELD = "x_studio_needs_review"
MARK = " — recette"
ACCESS_NAME = "x_lab_request accès temporaire de recette"

failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"  {'OK  ' if ok else 'ÉCHEC'} {label} — attendu {expected!r}, obtenu {got!r}")
    if not ok:
        failures.append(label)


def clear_caches(call):
    """Vide les caches de droits du serveur.

    Sans cela, un droit d'accès qui vient d'être créé n'est pas vu par le
    processus qui sert nos appels : `_get_allowed_models` est mis en cache par
    utilisateur et par opération (odoo/addons/base/models/ir_model.py:2133), et
    l'invalidation automatique ne nous atteint pas ici. Constaté sur cette
    copie : `create` restait refusé pendant huit requêtes consécutives alors
    que `read` passait, et redevenait autorisé aussitôt après cet appel.

    La méthode ne renvoie rien, et XML-RPC refuse de sérialiser `None` : la
    faute correspondante est attendue, pas masquée.
    """
    try:
        call("ir.model.access", "call_cache_clearing_methods", [])
    except xmlrpc.client.Fault as exc:
        if "cannot marshal None" not in str(exc):
            raise


def open_access(call):
    """Droit d'accès global temporaire, sans contexte studio : c'est un moyen de
    recette, pas un livrable (il n'a donc pas d'identifiant externe)."""
    found = call("ir.model.access", "search", [[("name", "=", ACCESS_NAME)]])
    if not found:
        model_id = call("ir.model", "search", [[("model", "=", MODEL)]])[0]
        found = [call("ir.model.access", "create", [{
            "name": ACCESS_NAME,
            "model_id": model_id,
            "group_id": False,
            "perm_read": True,
            "perm_write": True,
            "perm_create": True,
            "perm_unlink": True,
        }])]
    clear_caches(call)
    return found[0]


def close_access(call, access_id):
    call("ir.model.access", "unlink", [[access_id]])
    clear_caches(call)


def review(call, record_id):
    """Relit la valeur telle que le serveur l'a stockée."""
    return call(MODEL, "read", [[record_id], [FIELD]])[0][FIELD]


def make(call, name, days, kind):
    return call(MODEL, "create", [{
        "x_name": name + MARK,
        "x_studio_days": days,
        "x_studio_kind": kind,
    }])


def main():
    call = connect()

    print("A1 — définition du champ")
    fields = call(
        "ir.model.fields",
        "search_read",
        [[("model", "=", MODEL), ("name", "=", FIELD)]],
        {"fields": ["ttype", "state", "store", "compute", "depends"]},
    )
    check("un seul champ, sans doublon", len(fields), 1)
    if not fields:
        print("\nVERDICT : ROUGE — le champ n'existe pas, rien d'autre n'est testable")
        return 1
    definition = fields[0]
    check("type", definition["ttype"], "boolean")
    check("champ manuel", definition["state"], "manual")
    check("stocké", definition["store"], True)
    check("calculé (code non vide)", bool(definition["compute"]), True)
    check("dépendances", definition["depends"], "x_studio_days,x_studio_kind")

    access_id = open_access(call)
    created = []
    try:
        print("A2 — location de 7 jours : le seuil inclut 7")
        rid = make(call, "Location 7 jours", 7, "rental")
        created.append(rid)
        check("rental / 7 j", review(call, rid), True)

        print("A3 — location de 6 jours : sous le seuil")
        rid = make(call, "Location 6 jours", 6, "rental")
        created.append(rid)
        check("rental / 6 j", review(call, rid), False)

        print("A4 — prêts : exclus quelle que soit la durée")
        rid = make(call, "Prêt 7 jours", 7, "loan")
        created.append(rid)
        check("loan / 7 j", review(call, rid), False)
        rid = make(call, "Prêt 30 jours", 30, "loan")
        created.append(rid)
        check("loan / 30 j", review(call, rid), False)

        print("A5 — recalcul sur modification de la durée")
        rid = make(call, "Location qui s'allonge", 6, "rental")
        created.append(rid)
        check("avant : rental / 6 j", review(call, rid), False)
        call(MODEL, "write", [[rid], {"x_studio_days": 7}])
        check("après : rental / 7 j", review(call, rid), True)

        print("A6 — recalcul sur modification du type")
        rid = make(call, "Prêt requalifié en location", 10, "rental")
        created.append(rid)
        call(MODEL, "write", [[rid], {"x_studio_kind": "loan"}])
        check("avant : loan / 10 j", review(call, rid), False)
        call(MODEL, "write", [[rid], {"x_studio_kind": "rental"}])
        check("après : rental / 10 j", review(call, rid), True)

        print("Bord — type non renseigné")
        rid = make(call, "Sans type", 30, False)
        created.append(rid)
        check("type vide / 30 j", review(call, rid), False)
        print("A9 — les demandes de recette sont retirées")
        call(MODEL, "unlink", [created])
        created = []
        check(
            "aucune demande de recette restante",
            call(MODEL, "search_count", [[("x_name", "like", MARK)]]),
            0,
        )
    finally:
        if created:
            call(MODEL, "unlink", [created])
        close_access(call, access_id)

    print("A9 — la copie retrouve ses droits d'origine")
    check(
        "aucun droit d'accès sur le modèle",
        call("ir.model.access", "search_count", [[("model_id.model", "=", MODEL)]]),
        0,
    )
    check(
        "aucune règle d'enregistrement sur le modèle",
        call("ir.rule", "search_count", [[("model_id.model", "=", MODEL)]]),
        0,
    )

    if failures:
        print(f"\nVERDICT : ROUGE — {len(failures)} contrôle(s) en échec : {', '.join(failures)}")
        return 1
    print("\nVERDICT : VERT — tous les contrôles passent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
