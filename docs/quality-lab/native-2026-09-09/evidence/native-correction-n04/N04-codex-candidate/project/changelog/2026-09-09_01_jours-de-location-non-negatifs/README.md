<!-- release ouverte -->
# Jours de location non négatifs

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Refuser les jours négatifs par SQL, préserver zéro et le total (D-31) | — | VALIDÉ SOUS RÉSERVE author antérieur — TestRentalDays 4/4 ; update et copie PASS |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->

- 2026-09-09 — D-31 appliquée : SQL days >= 0 ; zéro, tarifs et total conservés. QA de tâche renforcée : 4/4 tests et copie PASS. Réserve : lint global rouge sur author absent avant cette release ; Ruff du diff vert. Détails dans qa.md.
- Version conservée à 19.0.1.0.0, incrément à la clôture. Aucun écran/droit modifié. Sources 19.1 indisponibles dans le laboratoire.
- Commit proposé : `[FIX] lab_rental: reject negative rental days with SQL constraint` (aucun commit effectué).
