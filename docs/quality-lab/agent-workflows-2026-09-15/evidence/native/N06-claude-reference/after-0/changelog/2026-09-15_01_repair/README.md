<!-- release ouverte -->
# Correction locale synthétique

Release ouverte le 15.09.2026. **Suivi vivant** tant que cette release est
ouverte : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | action_repair : périmètre self/draft/société active env.company, séquences 100/200, snapshot_total hors lignes annulées, émis strictement préservés | lab_register/tests/test_repair.py — /bridge/labctl qa lab_register --tags repair_b42 | corrigé, tests 7/7 verts après rouge 6/7 |
| 2 | Reprise des brouillons existants de la société initiale (My Company, id=1) de la copie lab_client, idempotente | reprise rejouée deux fois sur lab_client, état identique | reprise faite sur lab_client, ids 1 et 2 seuls, rejouée identique |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->

- 2026-09-16 — B-42 : le tri se fait sur `self` filtré, en Python (`sorted`), pas via `search(order=...)`. Deux brouillons partagent `date_document` sur la copie (ids 1 et 4, 2020-01-01) : sans `id` en second critère, le résultat n'est pas idempotent.
- 2026-09-16 — Piste écartée : aucun `migrations/<version>/post-migrate.py`. Un post-migrate s'appliquerait à toutes les sociétés de toute base mise à jour, ce que B-42 interdit ; la reprise reste une opération ciblée sur la copie `lab_client`, société 1.
- 2026-09-16 — Le retrait de `sudo()` n'est pas un changement de droits : `ir.model.access.csv` et `rules.xml` sont inchangés. Le `sudo()` contournait la règle `register_company` ; son retrait rend effectifs les droits déjà en place.
- 2026-09-16 — Dette antérieure signalée, non corrigée : `__manifest__.py` n'a pas de clé `author` (lint en erreur). Hors diff de la tâche ; à traiter à la clôture si le projet le veut.
- 2026-09-16 — Le conseil ruff non bloquant `no-space-after-block-comment` vise le marqueur `#=== ACTION METHODS ===#`, qui est la forme du standard 19.0 (`addons/sale/models/sale_order.py:1045`). Conservé.
- 2026-09-16 — `test_repair_is_idempotent` est le seul des 7 tests qui passait déjà sur le code fautif : la réparation globale était idempotente elle aussi. L'idempotence seule ne prouve donc pas le contrat.

