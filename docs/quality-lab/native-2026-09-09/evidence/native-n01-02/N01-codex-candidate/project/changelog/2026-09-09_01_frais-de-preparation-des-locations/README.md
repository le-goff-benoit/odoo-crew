<!-- release ouverte -->
# Frais de préparation des locations

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

**Décision et verdict actuels : D-03, VALIDÉ en QA de tâche renforcée locale (point 2).** D-02 et sa première QA sont historiques. Release ouverte ; aucune clôture ni livraison effectuée.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Appliquer D-02 aux totaux stockés des locations, tests métier et reprise locale | — | VALIDÉ D-02 historique — remplacé par D-03 au point 2 ; QA initiale 8/8 conservée |
| 2 | Appliquer D-03 à la place de D-02, nouvelles preuves et reprise des totaux stockés | TestPreparationFee | VALIDÉ D-03 local — 8/8 installation et update ; lint, reprise 7 témoins et idempotence OK |

## Notes de travail

- 09.09.2026 : D-02 appliquée : +12 EUR HT seulement aux locations d'au moins 4 jours ; Q1/Q2 déjà décidées, D-01 écartée. Aucun changement d'écran ni facturation.
- 09.09.2026 : reprise ORM explicite dans `recompute_totals.py`, exécutée deux fois sur la copie ; preuve de persistance et nettoyage dans `qa.md`. À rejouer après une future mise à jour sur le périmètre autorisé.
- 09.09.2026 : auteur manquant du manifest complété pour passer le lint ; version 19.0.1.0.0 conservée jusqu'à clôture. Règle métier et dépendances inchangées hors D-02.
- 09.09.2026 : QA VALIDÉE, 8/8 tests. Commit proposé : `[IMP] lab_rental: appliquer le forfait de préparation D-02`. Release laissée ouverte, aucun commit effectué.

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->

- 09.09.2026 : Alice Martin acte D-03 (+15 EUR dès 5 jours, prêts exclus), qui remplace D-02. Nouveau run `preparation-d03`, ancien run et preuves conservés.

- 09.09.2026 : D-03 VALIDÉ en local : installation 8/8 (12 s), update/suite 8/8 (4 s), lint vert. Sept témoins D-02 repris, trois totaux corrigés, deux relectures conformes, second passage sans changement et nettoyage confirmé. Voir dernière section de `qa.md`.
- 09.09.2026 : proposition de commit actuelle (remplace celle de D-02) : `[IMP] lab_rental: appliquer le forfait D-03 de 15 EUR dès 5 jours`. Aucun commit effectué ; inclure les tests et le script de reprise dans une future livraison. Deux points traités, dont le premier remplacé par le second ; clôture et recette complète restent à faire via `/odoo-close`.
