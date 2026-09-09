<!-- release ouverte -->
# Frais de préparation D-02

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Calcul stocké des frais de préparation D-02 | — | VALIDÉ — TestPreparationFee 7/7 ; update et reprise copie OK |

## Notes de travail

- 2026-09-09 : D-02 remplace D-01 ; seuil inclusif 4 jours, 12 EUR HT fixes, prêts exclus. Q1/Q2 déjà décidées, aucun arbitrage restant.
- 2026-09-09 : total stocké existant repris par script ORM idempotent sur lab_client après update, preuves dans qa.md. Trois fixtures préparées avant update puis nettoyées.
- 2026-09-09 : installation et update explicites nécessaires pour obtenir les 7 tests réels ; les tentatives rapides à zéro test ont été écartées.
- 2026-09-09 : version 19.0.1.0.0 conservée ; incrément et reprise à intégrer à la clôture. Aucun écran ni droit changé, aucune facturation.
- Commit proposé, non exécuté : `[IMP] lab_rental: appliquer les frais de préparation D-02`.

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->
