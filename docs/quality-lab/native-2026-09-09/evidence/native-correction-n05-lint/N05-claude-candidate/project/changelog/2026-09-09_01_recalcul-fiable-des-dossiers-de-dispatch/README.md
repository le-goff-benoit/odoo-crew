<!-- release ouverte -->
# Recalcul fiable des dossiers de dispatch

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | action_recalculate : exclure les lignes annulées, figer les dossiers validés, reprendre les brouillons existants | lab_dispatch:TestRecalculate + TestReprise | VERT — 7/7 tests ciblés, reprise idempotente prouvée sur lab_client |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->

- 2026-09-09 — D-11 (journal 2026-08-01) est **écartée** par D-12 : un dossier validé n'est
  ni recalculé, ni réécrit, ni repassé en brouillon. Tracé dans `PROJECT.md`.
- 2026-09-09 — La version du manifest est déjà passée à `19.0.1.0.1` : c'est elle qui
  déclenche `migrations/19.0.1.0.1/post-migrate.py`. **Ne pas la réincrémenter à la clôture.**
- 2026-09-09 — Dette antérieure à trancher avant clôture : clé `author` absente de
  `__manifest__.py` (depuis HEAD) ; elle fait échouer le bloc « contrôles Odoo » du lint.
- 2026-09-09 — Aucun écran ne change (le module n'a pas de vue) : rien à capturer à la clôture.
