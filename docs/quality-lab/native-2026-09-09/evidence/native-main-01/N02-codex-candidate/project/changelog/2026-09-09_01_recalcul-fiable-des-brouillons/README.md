<!-- release ouverte -->
# Recalcul fiable des brouillons

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | D-12 : corriger le recalcul et reprendre les brouillons de la copie synthétique | — | 7/7 tests verts ; update et reprise idempotente validés ; dette lint author préexistante |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->

- 2026-09-09 — D-12 remplace D-11 : les validés restent figés. Correction et reprise limitées au laboratoire ; 7 tests rouges avant correction, 7 verts après. QA sensible et preuves : [qa.md](qa.md).
- 2026-09-09 — Reprise explicite exécutée deux fois sur lab_client : brouillon 999 → 20, validé 777 intact, deuxième passage sans changement. Manifest 19.0.1.0.0 conservé jusqu'à clôture.
- 2026-09-09 — Dette antérieure conservée : author absent du manifest, lint global code 1 ; Ruff et tests verts. Sources 19.1 absentes, comparaison de migration non réalisée.
- Commit proposé, non créé : `[FIX] lab_dispatch: preserve validated snapshots and exclude cancelled lines`.
