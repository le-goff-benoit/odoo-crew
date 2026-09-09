Chaîne `/odoo-new` déroulée jusqu'au bout, voie Studio. Rien n'est commité — je ne l'ai pas fait sans votre demande.

# Indicateur de revue sur les demandes Aster (D-22)

**Projet** work · **série** 19.0 · **release** `changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast` (point n°1, **ouverte**) · **modules** aucun

## À décider
1. **`x_lab_request` n'a aucune `ir.model.access` ni aucune vue.** Le champ est correct et prouvé côté serveur, mais **personne ne peut le voir** : tout `create`/`read` sur ce modèle est refusé en XML-RPC, y compris à `admin` (`ir_model.py:33`). D-22 interdisant tout changement de droits, je n'ai créé aucune ACL. Faut-il ouvrir une demande distincte pour les droits et un écran ?
2. **Aucun déploiement.** Le pack n'existe que sur la copie locale `lab_client`.

## Cadrage
Rien à réutiliser dans le standard (modèle 100 % manuel), mais rien à coder non plus. D-22 tranche : seuil **7 inclus**, **prêts exclus** — D-21 (5 jours pour tous) est historique, non appliquée. Le brouillon réclamant un nouveau champ « durée » a été écarté : `x_studio_days` est réutilisé tel quel, comme `x_name` et `x_studio_kind` (ids 3734 / 3736 / 3738 inchangés).

## Réalisation
Un seul objet, créé en contexte `studio=True` — donc indiscernable d'un travail fait dans Studio : `x_lab_request.x_studio_needs_review`, booléen `manual`, `store=True`, `readonly=True`, `depends = x_studio_days,x_studio_kind`, compute en boucle explicite sur `self`. XML-ID relevé et non fabriqué : `studio_customization.revue_requise_demand_0772…`.

Livrables dans `…/studio/` : `build_point1.py` (idempotent), `pack.json`, `created.txt`, trois scénarios rejouables et leurs journaux.

## QA de tâche
| Contrôle | Résultat |
|---|---|
| Lint | **non exécuté, sans objet** — aucun module ; substitut `py_compile` OK. Ruff n'a pas tourné |
| Install / update | sans objet (voie Studio) |
| `odoo_pack.py diff` | 0 à créer / 0 à modifier / 1 inchangé · 0 référence `unresolved` |
| **Deux applications sans doublon** | VERT — 2 × (build + apply), champs 10→10, XML-ID 5→5, `created.txt` 1 ligne |
| Scénario RPC | VERT 25/25 — **rouge avant** construction |
| Scénario ORM | VERT 12/12 — **rouge avant** construction |
| Écran | aucune capture : 0 vue avant comme après |
| Critères d'acceptation | **13/13 couverts** (`qa_point1.md`, contrat `534358c6d6cb`) |

Deux points à ne pas lire comme acquis : le **comportement n'est pas prouvé en XML-RPC** mais par l'ORM superuser (valeurs relues dans la colonne SQL après flush), faute d'ACL — la limite elle-même est vérifiée par le scénario RPC (V6), pas supposée. Et le **rendu visuel n'est pas couvert**, faute de vue.

## Reste à faire
Les deux points « À décider ». Leçon candidate pour `LESSONS.md` : *un modèle manuel sans aucun `ir.model.access` est inaccessible en XML-RPC même à `admin` ; la recette du comportement passe alors par l'ORM superuser, et la limite se prouve dans le scénario.* À promouvoir par `/odoo-feedback` si elle se reproduit.

## Release
1 point, 1 réalisé. La release reste ouverte. Recette complète, captures et livrables client : `/odoo-close`.