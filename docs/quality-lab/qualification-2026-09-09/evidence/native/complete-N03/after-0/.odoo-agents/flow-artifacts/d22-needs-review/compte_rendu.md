# Indicateur de revue sur les demandes Aster (D-22)

**Projet** work (Association Aster) · **série** 19.0 · **release** `changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast` (point n°1) · **modules** aucun — configuration en base

## À décider
1. **`x_lab_request` n'a aucun `ir.model.access` ni aucune vue.** Le champ livré est correct et
   prouvé côté serveur, mais **aucun utilisateur ne peut le voir** : tout `create`/`read` sur ce
   modèle est refusé en XML-RPC, y compris à `admin`. D-22 interdisant tout changement de droits,
   je n'ai créé aucune ACL. Faut-il ouvrir une demande distincte pour les droits (et un écran) ?
2. **Aucun déploiement.** Le pack n'existe que sur la copie locale `lab_client`. Staging et
   production attendent votre décision — et, pour la production, une confirmation explicite.

## Cadrage
Verdict standard : rien à réutiliser (modèle 100 % manuel), mais **rien à coder** non plus — un
champ manuel calculé stocké suffit. Voie **Studio** (0 module custom, Studio déjà en base).
D-22 tranche les deux questions ouvertes : seuil **7 inclus**, **prêts exclus** ; D-21 (5 jours
pour tous) est historique et n'a pas été appliquée. Le brouillon qui demandait un nouveau champ
« durée » a été écarté : `x_studio_days` est réutilisé tel quel.

## Réalisation
`changelog/2026-09-09_01_…/studio/` : `lab_rpc.py` (transport), `build_point1.py` (construction
idempotente), `test_point1_rpc.py`, `test_point1_orm.py`, `test_point1_idempotence.py`,
`pack.json`, `created.txt`, `preuves/*.log`.

Un seul objet créé, en contexte `studio=True` pour qu'il soit indiscernable d'un travail fait
dans Studio : `x_lab_request.x_studio_needs_review`, booléen `manual`, `store=True`,
`readonly=True`, `depends = x_studio_days,x_studio_kind`, compute en boucle explicite sur `self`.
XML-ID relevé, non fabriqué : `studio_customization.revue_requise_demand_0772…`.

## QA de tâche
| Contrôle | Résultat |
|---|---|
| Lint | non exécuté, **sans objet** (aucun module) ; substitut `py_compile` OK sur les 5 scripts |
| Install / update | sans objet (voie Studio) |
| `odoo_pack.py diff` | 0 à créer / 0 à modifier / 1 inchangé ; 0 référence `unresolved` |
| Deux applications sans doublon | VERT — tous compteurs identiques, `created.txt` à 1 ligne |
| Scénario RPC | VERT 25/25 (rouge avant) |
| Scénario ORM | VERT 12/12 (rouge avant) |
| Écran | aucune capture — 0 vue avant comme après |
| Critères d'acceptation | **13/13 couverts** (`qa_point1.md`, contrat `534358c6d6cb`) |

## Reste à faire
- Les deux points « À décider » ci-dessus.
- Leçon candidate pour `LESSONS.md` : *un modèle manuel sans aucun `ir.model.access` est
  inaccessible en XML-RPC même à `admin` ; la recette de comportement doit alors passer par
  l'ORM superuser, et la limite doit être prouvée dans le scénario, pas supposée.* À promouvoir
  par `/odoo-feedback` si elle se reproduit.

## Release
1 point dans la release, 1 réalisé. La release **reste ouverte**. Clôture et recette complète :
`/odoo-close`.
