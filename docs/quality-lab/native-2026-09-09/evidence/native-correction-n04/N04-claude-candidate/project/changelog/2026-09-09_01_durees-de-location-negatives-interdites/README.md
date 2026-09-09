<!-- release ouverte -->
# Durees de location negatives interdites

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | lab.rental : contrainte SQL days >= 0 (D-31), zéro autorisé | — | VALIDÉ — 7/7 tests /lab_rental:TestDaysConstraint, contrainte éprouvée sur lab_client |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->
