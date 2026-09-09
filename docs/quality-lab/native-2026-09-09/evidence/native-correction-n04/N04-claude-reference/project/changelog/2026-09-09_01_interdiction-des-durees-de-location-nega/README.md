<!-- release ouverte -->
# Interdiction des durees de location negatives

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Interdire les durees negatives sur lab.rental par contrainte SQL (D-31) | lab_rental:TestRentalDaysConstraint | VALIDÉ — 6/6 tests ciblés, contrainte vérifiée dans pg_constraint sur la copie |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->
- 2026-09-09 — D-31 tranche les deux seules questions ouvertes (zéro valide, contrainte SQL) : aucune question bloquante posée.
- 2026-09-09 — QA renforcée retenue (données existantes) : validation immédiate sur la copie `lab_client`, sans attendre la clôture.
- 2026-09-09 — Écarté volontairement : borne sur `daily_rate` (non arbitrée par D-31) et `required=True` sur `days` (élargirait le périmètre).
- 2026-09-09 — Non corrigé faute de mandat : clé `author` absente de `__manifest__.py`, seule cause de l'échec du lint. À arbitrer avant la clôture.
- 2026-09-09 — Version du manifest laissée à `19.0.1.0.0` : l'incrément se fait à la clôture de la release.
