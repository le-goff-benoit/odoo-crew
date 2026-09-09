[4/4 journal] entrée écrite · PROJECT.md : D-22 réalisée + 3 pièges ajoutés · flow TERMINÉ

---

# Indicateur de revue sur les demandes Aster

**Projet** work (Association Aster) · **série** 19.0 (origine : défaut) · **release** `changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast` (point n°1) · **voie** Studio, aucun module

## Cadrage

Verdict standard : **ça n'existe pas** — `x_lab_request` est un modèle manuel du client, un champ calculé stocké est la bonne forme. D-22 appliquée telle quelle (seuil **7 inclus**, `loan` **exclu**) ; D-21 (5 jours, tous types), encore présente au journal, écartée explicitement. Le brouillon qui demandait un nouveau champ durée est écarté : `x_studio_days` existe.

Deux hypothèses posées, D-22 étant muette : **genre vide ⇒ pas de revue**, **durée nulle ou négative ⇒ pas de revue**. Hors périmètre : vues, menus, automatisations, droits, déploiement.

## Réalisation

Un seul objet créé, en contexte `{"studio": True}` sur la copie `lab_client` :

- `x_lab_request.x_studio_needs_review` — booléen, **stocké**, calculé, lecture seule, `state=manual`, `depends = x_studio_days,x_studio_kind`
- calcul (safe_eval) : `(record['x_studio_days'] or 0) >= 7 and record['x_studio_kind'] == 'rental'`
- XML-ID relevé, pas fabriqué : `studio_customization.revue_requise_demand_2e8e5590-…`, dans `created.txt`

Livrables dans `changelog/<release>/studio/` : `build_01_needs_review.py` (idempotent, `--dry-run`), `test_01_needs_review.py` (scénario RPC rejouable), `pack.json`, `created.txt`, `preuves/` (9 sorties réelles), `README.md`. Les champs `x_name`, `x_studio_days`, `x_studio_kind` sont réutilisés tels quels — mêmes ids, mêmes XML-ID `lab_seed_*`.

## QA de tâche

| Contrôle | Résultat |
|---|---|
| `odoo_pack.py diff` sur la copie | 0 à créer / 0 à modifier / 1 inchangé |
| Pack sans `unresolved` | 0 ; `model_id` → `studio_customization.lab_seed_model` |
| **Deux applications du build** | CRÉÉ puis INCHANGÉ — 1 champ, 1 XML-ID, **aucun doublon** |
| Scénarios RPC rejoués par le testeur | **9/9 vert**, sortie 0 |
| Discrimination du scénario | ROUGE 0/1 avant, VERT 9/9 après |
| Écran | sans objet — 0 `ir.ui.view` sur le modèle, avant comme après |
| Critères d'acceptation | **10/10 `covered`**, réception `pass` par `qa-report` |

## Reste à faire

- **Contrôle non exécuté, dit tel quel** : pas de lint Ruff. Le point ne livre aucun module ; `labctl lint` n'accepte qu'un module et Ruff n'est pas installé hors image QA. Seul `py_compile` est passé (OK) — ce n'est pas un lint.
- **Rien n'est déployé** : le pack est prêt pour `diff` puis `apply` en staging/production, sous décision humaine. Conforme à la demande.
- L'indicateur n'est visible nulle part (aucune vue sur ce modèle) : l'exposer est une tâche à cadrer.
- Anomalie corrigée en cours de route : mon helper RPC empaquetait un niveau de liste en trop (`read`/`unlink` en `unhashable type: 'list'`). Corrigé, puis **toute la séquence rejouée depuis une copie remise à zéro** — les preuves conservées sont celles de la version corrigée. Leçon candidate pour `/odoo-feedback` : sur ce parc, `create` en XML-RPC renvoie une liste.

## Release

1 point, 1 réalisé. **Release ouverte.** Clôture, recette complète et livrables : `/odoo-close`. Rien n'est commité — dis-moi si tu veux le commit.