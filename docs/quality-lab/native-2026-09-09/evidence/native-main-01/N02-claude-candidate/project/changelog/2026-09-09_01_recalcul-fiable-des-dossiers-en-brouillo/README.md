<!-- release ouverte -->
# Recalcul fiable des dossiers en brouillon

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | action_recalculate : exclure les lignes annulées, figer les dossiers validés, reprendre les brouillons existants | tests ciblés lab_dispatch + reprise sur lab_client | VALIDÉ — 6/6 tests ciblés, reprise idempotente prouvée sur lab_client |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->
