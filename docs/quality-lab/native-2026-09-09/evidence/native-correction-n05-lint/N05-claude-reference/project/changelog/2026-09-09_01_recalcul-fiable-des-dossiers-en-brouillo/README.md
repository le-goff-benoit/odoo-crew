<!-- release ouverte -->
# Recalcul fiable des dossiers en brouillon

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Corriger action_recalculate (lignes annulées exclues, validés figés) et reprendre les brouillons existants | `/lab_dispatch:TestDispatchRecalculate` (5/5) | VALIDÉ — 5/5 tests ciblés, reprise idempotente prouvée sur la copie |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->
- 09.09.2026 — Le champ figé (et non un champ calculé stocké) est délibéré : un `compute` se
  recalculerait tout seul et violerait D-12 « les validés ne sont pas même recomputés ».
- 09.09.2026 — La reprise compare les totaux à l'exact, sans tolérance à 2 décimales : sinon
  `LEGACY_FRACTION` (20.004) serait resté faux.
- 09.09.2026 — À arbitrer à la clôture : clé `author` absente du manifest (dette antérieure à
  `d6b5c10`, seul point rouge du lint) et emballage de la reprise en script de migration.
