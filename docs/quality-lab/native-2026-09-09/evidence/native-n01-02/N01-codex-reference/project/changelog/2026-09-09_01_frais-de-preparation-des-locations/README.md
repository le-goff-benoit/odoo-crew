<!-- release ouverte -->
# Frais de préparation des locations

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Calcul stocké des frais de préparation D-03 (remplace D-02) et reprise des essais | /lab_rental:TestPreparation (D-03, 8/8) | VALIDÉ EN LOCAL D-03 — 8/8, lint, update et double reprise copie OK ; clôture à faire |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->

- 2026-09-09 : D-02 remplace le taux historique de 7 %. Q1/Q2 déjà tranchées. Aucun écran ni facture. QA renforcée pour le total stocké existant.
- 2026-09-09 : manifest conservé à 19.0.1.0.0 pendant cette release. À la clôture, passer à 19.0.1.0.1 (ou version supérieure couvrant la migration) **avant** la recette, pour déclencher migrations/19.0.1.0.1/post-recompute-amount-total.py. La QA locale invoque explicitement cette migration après update.

- 2026-09-09 : candidat /odoo-feedback — refuser une QA « verte » à zéro test et vérifier que le module est installé avant de choisir -u. Détail et limites dans qa.md.

- 2026-09-09 : Alice Martin acte D-03, 15 EUR dès 5 jours inclus, prêts exclus ; D-02 remplacée. Reprise du point 1 et nouvelle QA renforcée ; historique conservé dans qa.md et preuves/, nouvelles preuves dans preuves/d03/.

- 2026-09-09 : D-03 VALIDÉE EN LOCAL après reprise 1 (critère write_date rectifié conformément au standard) ; 8/8 tests, lint et update/reprise copie verts, 8 essais nettoyés. Historique D-02 intact. À la clôture, valider le déclenchement automatique de la migration avec le calcul D-03.
