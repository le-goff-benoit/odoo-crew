<!-- release ouverte -->
# Recalcul des brouillons D12

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | D-12 : recalcul des brouillons et reprise locale idempotente | — | VALIDÉ — 6/6 tests ; reprise 1 puis 0 modification ; validé intact |

## Notes de travail

- 09.09.2026 : D-12 remplace D-11 ; correction module et reprise explicite des seuls brouillons sur lab_client autorisées. Validés définitivement ignorés par l'action.
- 09.09.2026 : test rouge réel puis 6/6 tests verts ; lint final vert ; reprise 1 puis 0 modification, validé 777 intact. Détail et limites dans qa.md.
- 09.09.2026 : author synthétique ajouté pour lever le lint ; version conservée à 19.0.1.0.0. Release ouverte, aucun déploiement ni commit.

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->
