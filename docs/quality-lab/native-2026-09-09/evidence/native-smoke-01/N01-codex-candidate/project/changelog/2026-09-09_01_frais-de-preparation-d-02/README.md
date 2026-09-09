<!-- release ouverte -->
# Frais de préparation D-02

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Total stocké avec frais D-02, tests métier et reprise sur copie | /lab_rental:TestPreparationFees | à faire |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->

- 2026-09-09 — D-02 appliquée : forfait 12 EUR à partir de 4 jours inclus pour les locations, prêts exclus ; Q1/Q2 déjà tranchées. Aucun écran ni flux de facturation modifié.
- 2026-09-09 — Total stocké existant : reprise explicite dans `scripts/recompute_totals.py`, validée et rejouée sur lab_client. L'update seul conserve les anciens totaux (preuve QA). Intégrer la reprise au protocole de livraison à la clôture.
- 2026-09-09 — QA après une reprise des assertions SQL : lint vert, 10/10 tests à l'installation puis à l'update, copie validée et témoins nettoyés. Détail : `qa.md`, preuves dans `preuves/`.
- 2026-09-09 — `author` ajouté au manifest pour satisfaire le lint ; version maintenue à 19.0.1.0.0 jusqu'à clôture. Aucun commit créé. Proposition : `[IMP] lab_rental: appliquer les frais de préparation D-02`.
