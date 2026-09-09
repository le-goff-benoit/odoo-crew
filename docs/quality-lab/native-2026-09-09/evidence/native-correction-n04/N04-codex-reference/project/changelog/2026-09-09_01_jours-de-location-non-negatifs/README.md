<!-- release ouverte -->
# Jours de location non négatifs

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | D-31 — Refuser les jours négatifs par contrainte SQL, zéro et total conservés | — | VALIDÉ SOUS RÉSERVE author préexistant — TestRentalDays 4/4, update et copie OK |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->

- 2026-09-09 — D-31 : SQL Odoo 19.0, zéro inclus, calcul inchangé ; revue arbitrée, aucun écran/droit touché. Copie initialement vide : témoin ajouté avant update, vérifié puis nettoyé.
- 2026-09-09 — 4/4 tests verts, update copie et CHECK validés. Ruff vert ; réserve : lint global rouge sur author absent avant la release, preuve sur référence Git dans qa.md.
- 2026-09-09 — Version conservée à 19.0.1.0.0 ; release ouverte, aucun livrable client produit. Commit proposé (non créé) : `[FIX] lab_rental: reject negative rental days with SQL constraint`.
