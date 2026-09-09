<!-- release ouverte -->
# Interdiction des durees negatives de location

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Contrainte SQL days >= 0 sur lab.rental (D-31), zéro autorisé, total inchangé | — | VALIDÉ SOUS RÉSERVE — 6/6 tests, A1-A7 verts, A8 partiel (RPC/UI à la clôture) |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->
