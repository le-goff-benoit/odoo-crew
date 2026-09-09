<!-- release ouverte -->
# Recalcul juste des dossiers et reprise des brouillons

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Corriger action_recalculate (lignes annulées exclues, validés figés) et reprendre les brouillons existants | — | VERT — 7/7 tests ciblés, reprise idempotente prouvée sur lab_client, 7/7 critères |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->

- **2026-09-09** — Version du manifest incrémentée dès cette tâche (`19.0.1.0.0` → `19.0.1.0.1`) : c'est l'incrément qui déclenche le script de migration, donc la reprise. La release ne porte que ce point.
- **2026-09-09** — Piste écartée : transformer `snapshot_total` en champ calculé stocké. Un compute se recalculerait aussi pour les dossiers validés, ce que D-12 interdit. Consigné dans `PROJECT.md` pour qu'une prochaine intervention ne le « corrige » pas à tort.
- **2026-09-09** — Piste écartée : tolérance d'arrondi dans la reprise. Elle aurait laissé `LEGACY_FRACTION` à 20.004. Comparaison stricte retenue.
- **2026-09-09** — À arbitrer à la clôture : clé `author` absente du manifest (dette antérieure au commit `799eff1`) et `ruff` non installé (une voie de lint non jouée).
