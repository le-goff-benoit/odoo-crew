<!-- release ouverte -->
# Interdiction des durees negatives de location

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Contrainte SQL days >= 0 sur lab.rental (D-31), zéro autorisé, total inchangé | `labctl qa lab_rental --quick --tags /lab_rental:TestLabRentalDaysConstraint` | VERT AVEC RESERVE — 6/6 tests cibles + suite complete, A1-A9 satisfaits, A7 risque n1 confirme et documente |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->

- 2026-09-09 — Chaîne reprise après interruption des voies QA : revue et code repris tels quels,
  toutes les preuves d'exécution rejouées sur les bases reconstituées (`lab_client`, `lab_qa`).
- 2026-09-09 — **A7 / risque n°1 confirmé sur la copie** : un `-u` sur une base portant une ligne
  `days < 0` se termine sans erreur **sans poser la contrainte**. Avant toute mise à niveau réelle :
  compter les lignes violantes, les traiter, puis vérifier `pg_constraint`. L'arbitrage
  « mise à 0 ou suppression » n'est pas tranché par D-31 → Luc Roy.
- 2026-09-09 — Dette antérieure : `lab_rental/__manifest__.py` sans clé `author`, le lint sort en
  échec pour ce seul motif. Hors périmètre de la tâche, à arbitrer à la clôture.
- 2026-09-09 — `git diff` contre `.base` (`9cf40f33…`) impossible dans cette copie : objet git
  absent. Le diff de la tâche a été délimité par recoupement documentaire.
- 2026-09-09 — Reste pour `/odoo-close` : vérifier à l'écran que le message français est bien celui
  remonté en RPC/UI (partie non traversée d'A8) ; incrémenter la version du manifest.
