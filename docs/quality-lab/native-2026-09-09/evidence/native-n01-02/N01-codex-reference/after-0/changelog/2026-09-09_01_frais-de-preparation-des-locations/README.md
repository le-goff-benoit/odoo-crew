<!-- release ouverte -->
# Frais de préparation des locations

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Calcul stocké des frais de préparation D-02 et reprise des essais | /lab_rental:TestPreparation (8/8) | VALIDÉ — TestPreparation 8/8, lint et update/reprise copie OK |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->

- 2026-09-09 : D-02 remplace le taux historique de 7 %. Q1/Q2 déjà tranchées. Aucun écran ni facture. QA renforcée pour le total stocké existant.
- 2026-09-09 : manifest conservé à 19.0.1.0.0 pendant cette release. À la clôture, passer à 19.0.1.0.1 (ou version supérieure couvrant la migration) **avant** la recette, pour déclencher migrations/19.0.1.0.1/post-recompute-amount-total.py. La QA locale invoque explicitement cette migration après update.

- 2026-09-09 : candidat /odoo-feedback — refuser une QA « verte » à zéro test et vérifier que le module est installé avant de choisir -u. Détail et limites dans qa.md.
