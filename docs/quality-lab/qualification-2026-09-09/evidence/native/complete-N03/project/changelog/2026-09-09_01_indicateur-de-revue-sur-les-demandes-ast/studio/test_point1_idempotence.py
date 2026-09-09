"""Scénario RPC rejouable — point 1, idempotence : deux applications sans doublon.

Rejoue, sur la copie du client, la séquence complète de livraison **deux fois** :
script de construction, puis `odoo_pack.py apply`. Compte avant / après par
XML-RPC et exige l'égalité stricte (C11), puis un `diff` sans écart (C12).

Usage : python3 test_point1_idempotence.py
"""

import os
import re
import subprocess
import sys

from lab_rpc import DB, FIELD, MODEL, PASSWORD, URL, connect

ICI = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(ICI, "pack.json")
OUTIL = os.path.expanduser("~/.odoo19-agents/scripts/odoo_pack.py")

echecs = []


def verifie(titre, condition, detail=""):
    print(f"[{'OK ' if condition else 'ROUGE'}] {titre}" + (f" — {detail}" if detail else ""))
    if not condition:
        echecs.append(titre)


def lance(titre, argv):
    print(f"\n$ {' '.join(argv)}")
    fini = subprocess.run(argv, cwd=ICI, capture_output=True, text=True)
    sortie = (fini.stdout + fini.stderr).strip()
    print(sortie)
    verifie(titre, fini.returncode == 0, f"code {fini.returncode}")
    return sortie


def photo(call):
    """Ce qui doit rester strictement identique d'une application à l'autre."""
    return {
        "champs du modèle": call("ir.model.fields", "search_count", [[("model", "=", MODEL)]]),
        "champs nommés needs_review": call(
            "ir.model.fields", "search_count", [[("model", "=", MODEL), ("name", "like", "%needs_review%")]]
        ),
        "XML-ID studio_customization": call(
            "ir.model.data", "search_count", [[("module", "=", "studio_customization")]]
        ),
        "modèles x_lab_request": call("ir.model", "search_count", [[("model", "=", MODEL)]]),
        "valeurs de sélection x_studio_kind": call(
            "ir.model.fields.selection", "search_count", [[("field_id.model", "=", MODEL)]]
        ),
    }


def main():
    call = connect()
    verifie("précondition — le champ existe", bool(call("ir.model.fields", "search_count", [[("model", "=", MODEL), ("name", "=", FIELD)]])))

    reference = photo(call)
    print("\nétat de référence : " + ", ".join(f"{k}={v}" for k, v in reference.items()))

    cible = ["--db", DB, "--url", URL, "--password", PASSWORD]
    for tour in (1, 2):
        print(f"\n───────── application n°{tour} ─────────")
        lance(f"tour {tour} — build_point1.py", [sys.executable, "build_point1.py"])
        lance(f"tour {tour} — odoo_pack.py apply", [sys.executable, OUTIL, "apply", PACK] + cible)
        apres = photo(call)
        for cle, attendu in reference.items():
            verifie(f"tour {tour} — {cle} inchangé", apres[cle] == attendu, f"{attendu} → {apres[cle]}")

    print("\n───────── diff final ─────────")
    sortie = lance("diff — exécution", [sys.executable, OUTIL, "diff", PACK] + cible)
    # « <à créer> / <à modifier> / <inchangés> » : les deux premiers doivent être nuls.
    compteurs = re.search(r"(\d+) / (\d+) / (\d+) à créer / à modifier / inchangés", sortie)
    verifie("diff — ligne de compteurs lisible", compteurs is not None, sortie.splitlines()[-1] if sortie else "")
    if compteurs:
        a_creer, a_modifier, inchanges = (int(g) for g in compteurs.groups())
        verifie(
            "diff — aucun écart entre le pack et la copie",
            a_creer == 0 and a_modifier == 0 and inchanges == 1,
            f"{a_creer} à créer, {a_modifier} à modifier, {inchanges} inchangé(s)",
        )

    # created.txt ne doit pas non plus avoir doublonné
    lignes = [l.strip() for l in open(os.path.join(ICI, "created.txt"), encoding="utf-8") if l.strip()]
    verifie("created.txt sans doublon", len(lignes) == len(set(lignes)) == 1, f"{len(lignes)} ligne(s)")

    if echecs:
        print(f"\nSCÉNARIO IDEMPOTENCE ROUGE — {len(echecs)} vérification(s) en échec")
        return 1
    print("\nSCÉNARIO IDEMPOTENCE VERT — deux applications, aucun doublon")
    return 0


if __name__ == "__main__":
    sys.exit(main())
