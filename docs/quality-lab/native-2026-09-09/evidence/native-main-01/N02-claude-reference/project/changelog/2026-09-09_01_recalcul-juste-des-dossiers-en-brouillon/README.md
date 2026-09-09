<!-- release ouverte -->
# Recalcul juste des dossiers en brouillon

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Corriger action_recalculate (lignes annulées exclues, validés figés) et reprendre les brouillons existants sur la copie | — | VERT — 7/7 tests ciblés, reprise idempotente prouvée sur lab_client |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->

- 2026-09-09 — D-12 (`decisions/2026-09-08.md`) remplace D-11 du `JOURNAL.md` : on ne recalcule que
  les brouillons, les validés restent figés sans être réécrits. Ancienne piste « reconstruire les
  validés » définitivement écartée.
- 2026-09-09 — `labctl qa … --quick` peut rendre un faux vert (0 test collecté quand le module n'est
  pas installé sur la base QA) : lire le compte de tests, pas le verdict. Chemin complet utilisé.
- 2026-09-09 — Reprise des données jouée sur la copie synthétique `lab_client` uniquement ; le script
  `reprise/reprise_brouillons.py` est rejouable et n'écrit que les brouillons divergents.
