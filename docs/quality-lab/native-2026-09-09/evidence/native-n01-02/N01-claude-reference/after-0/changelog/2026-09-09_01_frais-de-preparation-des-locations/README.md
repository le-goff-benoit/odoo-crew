<!-- release ouverte -->
# Frais de préparation des locations

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Frais de préparation : forfait 12 EUR sur les locations de 4 jours et plus (D-02) | `/lab_rental:TestPreparationFee` — 9/9 | VALIDÉ — 9/9 tests ciblés, lint vert, mise à niveau OK |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->

- 2026-09-09 — D-02 remplace D-01 (7 %). L'ancienne règle ne subsiste que dans l'entrée de
  journal du 2026-08-01 : ne pas la réimplémenter.
- 2026-09-09 — Écarté volontairement : contrainte SQL sur `days`/`daily_rate` positifs
  (changerait le comportement à la saisie, hors demande), devise et arrondi (D-02 dit EUR
  unique et aucun arrondi), bascule vers le standard `sale_renting` (enterprise, refonte).
- 2026-09-09 — **À trancher à la clôture** : recalcul des enregistrements préexistants.
  Un champ stocké ne se recalcule pas quand la formule change. `lab_client` en contient 0
  ce jour (vérifié en SQL) ; si la base cible en a, il faut un `migrations/<version>/post-recompute.py`,
  écrit avec le numéro de version réel de la release.
- 2026-09-09 — **Version du manifest non incrémentée** (19.0.1.0.0) : release ouverte,
  l'incrément se fait une fois, à la clôture. Dette antérieure à corriger au même moment :
  clé `author` absente du manifest.
- 2026-09-09 — Piège d'outillage : `odoo-test.sh --quick` (même avec `--fresh`) fait un `-u`
  dès que la base existe ; sur une base où le module n'est pas installé, il rend un vert
  avec 0 test. Passer par le chemin complet (`-i`) tant que ce n'est pas corrigé.
