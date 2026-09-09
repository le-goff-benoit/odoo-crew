<!-- release ouverte -->
# Recalcul fiable des dossiers brouillons

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Corriger action_recalculate (lignes annulées exclues, validés figés) et reprendre les brouillons existants | — | VALIDÉ — 5/5 tests, reprise idempotente prouvée sur la copie |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->
- 2026-09-09 — Version du manifest incrémentée dès maintenant (19.0.1.0.1) : sans incrément, la migration
  de reprise ne se déclenche pas. À la clôture, ne pas ré-incrémenter.
- 2026-09-09 — Lint rouge sur `author` manquant dans le manifest : dette antérieure au commit 799eff1,
  volontairement non reprise. À arbitrer avant la clôture.
- 2026-09-09 — `ruff` indisponible dans l'environnement : étape 1/3 du lint ignorée, pas passée.
- 2026-09-09 — D-11 (journal du 2026-08-01, « recalculer tous les dossiers ») est obsolète : D-12 fait foi.
