<!-- release ouverte -->
# Recalcul fiable des brouillons

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Corriger le recalcul et reprendre les brouillons synthétiques (D-12) | — | VALIDÉ — 6/6 tests, QA sensible et reprise idempotente sur lab_client |

## Notes de travail

- 09.09.2026 — D-12 appliquée, voie module_high_risk ; reprise explicitement limitée à lab_client, sans hook de migration automatique. Version 19.0.1.0.0 conservée jusqu'à clôture.
- 09.09.2026 — Six tests rouges puis verts ; le premier passage QA à zéro test a été rejeté. Installation explicite nécessaire avant --quick dans ce laboratoire.
- 09.09.2026 — Reprise commitée : brouillon 999 → 20, validé 777 intact ; deuxième exécution sans écriture, relecture indépendante confirmée. Voir qa.md et preuves/.
- Commit proposé, non exécuté : `[FIX] lab_dispatch: preserve validated totals and exclude cancelled lines`.

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->
