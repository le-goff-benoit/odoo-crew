`[4/4 journal]` entrée écrite · `PROJECT.md` : 1 décision + 2 pièges ajoutés · release laissée ouverte

---

# Indicateur de revue requise sur les demandes (D-22)

**Projet** Association Aster (`/work`) · **série** 19.0 (défaut) · **release** `changelog/2026-09-09_01_indicateur-de-revue-requise-sur-les-dema` (point n°1) · **modules** aucun — configuration en base

## À décider

1. **`x_lab_request` n'a aucun `ir.model.access` ni `ir.rule`.** Sans ACL, tout accès hors superutilisateur est refusé (`odoo/addons/base/models/ir_model.py:2134-2167`) : **aucun utilisateur réel ne voit l'indicateur aujourd'hui**. D-22 interdisant de toucher aux droits, je n'ai rien fait — mais c'est un préalable à toute mise en service.
2. **Aucun écran ne porte le champ** (le modèle n'a aucune vue). Conforme à la demande, à prévoir ensuite.
3. **Déploiement non fait** (hors périmètre) : le pack est prêt pour `diff` puis `apply` sur staging.

## Cadrage

Verdict : rien de standard à réutiliser sur un modèle manuel, mais le besoin est entièrement couvert par un **champ manuel calculé stocké** — aucun module justifié. D-22 (7 jours inclus, prêts exclus) l'emporte sur D-21 (5 jours, tous types) qui traînait dans le journal. Hors périmètre : droits, écran, automatisation, déploiement.

## Réalisation

Un seul objet créé, en contexte `studio=True`, identifiant externe déposé par Odoo lui-même : `studio_customization.revue_requise_demand_924627ca…` (`ir.model.fields`, booléen, `store=True`, `readonly`, `depends = x_studio_days,x_studio_kind`). Les trois champs existants sont lus, jamais réécrits — leurs `lab_seed_*` sont intacts.

Livrés dans `studio/` : `pack.json` (le livrable), `created.txt`, `build_1_needs_review.py` (idempotent), `rpc_common.py`, `test_1_needs_review.py` (XML-RPC), `test_1_needs_review_orm.py`, `reprise_avant_1_needs_review.py`.

Deux scénarios plutôt qu'un : la table de vérité au niveau enregistrement est inaccessible en XML-RPC faute d'ACL. Le scénario RPC **constate** cette limite à l'exécution et jouera la table de vérité automatiquement si une ACL est ajoutée un jour.

## QA de tâche

| Contrôle | Résultat |
|---|---|
| Compilation des 5 scripts (pas de module → pas de lint de module) | OK |
| Scénarios rouges **avant** configuration | ROUGE, motif attendu |
| Build rejoué 3× | 1 création puis « déjà conforme », 0 doublon |
| Pack appliqué 2× depuis un état sans le champ | 1 créé, puis 0/0/1 inchangé |
| `odoo_pack.py diff` | 0 / 0 / 1 — aucun écart, aucune référence `unresolved` |
| Relevé final en base | 1 champ, 1 identifiant externe, `noupdate` et `studio` à vrai |
| Scénario XML-RPC | **VERT 12/12** |
| Scénario ORM (table de vérité D-22, reprise incluse) | **VERT 16/16** |

**Critères d'acceptation : 13/13**, dont 12/13 au premier passage. Une reprise : C10 était rouge — l'identifiant externe sortait en `noupdate=False`. Vérification dans les sources plutôt que dans le souvenir : Studio ne pose `noupdate` qu'au `write` suivant (`web_studio/models/ir_model_data.py:19-25`, appelé par `ir_model.py:62`). Le script rejoue exactement cet appel de Studio. Données de recette nettoyées, `lab_client` ne garde que le champ livré.

## Reste à faire

Les trois points « À décider ». **Leçon candidate pour `/odoo-feedback`** : la doc de rôle Studio résume « marqué `studio` et `noupdate` » — vrai seulement après une écriture, pas à la création ; un contrôle écrit sur ce résumé part rouge à tort.

## Release

1 point, 1 réalisé. Rien n'est commité (aucune demande en ce sens). Clôture et recette complète : `/odoo-close`.