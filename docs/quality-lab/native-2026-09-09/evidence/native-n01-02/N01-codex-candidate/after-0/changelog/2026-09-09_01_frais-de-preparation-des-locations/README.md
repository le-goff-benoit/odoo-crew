<!-- release ouverte -->
# Frais de préparation des locations

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Appliquer D-02 aux totaux stockés des locations, tests métier et reprise locale | — | VALIDÉ — TestPreparationFee 8/8 ; lint, installation, update et reprise idempotente sur copie OK |

## Notes de travail

- 09.09.2026 : D-02 appliquée : +12 EUR HT seulement aux locations d'au moins 4 jours ; Q1/Q2 déjà décidées, D-01 écartée. Aucun changement d'écran ni facturation.
- 09.09.2026 : reprise ORM explicite dans `recompute_totals.py`, exécutée deux fois sur la copie ; preuve de persistance et nettoyage dans `qa.md`. À rejouer après une future mise à jour sur le périmètre autorisé.
- 09.09.2026 : auteur manquant du manifest complété pour passer le lint ; version 19.0.1.0.0 conservée jusqu'à clôture. Règle métier et dépendances inchangées hors D-02.
- 09.09.2026 : QA VALIDÉE, 8/8 tests. Commit proposé : `[IMP] lab_rental: appliquer le forfait de préparation D-02`. Release laissée ouverte, aucun commit effectué.

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->
