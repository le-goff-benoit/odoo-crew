# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-01 : frais de préparation de 7 % pour toutes les locations. Cette décision est historique, remplacée par D-02.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Frais de préparation des locations (D-02)
**Demande** : appliquer D-02 sur `lab_rental` — total calculé et stocké, sans écran ni facturation.
**Fait** : `_compute_amount_total` délègue à `_preparation_fee()` (12 EUR fixes si `kind = rental`
et `days >= 4`) ; 10 tests métier ; reprise `migrations/19.0.1.1.0/post-migrate.py` ; manifest en
19.0.1.1.0. Release `2026-09-09_01`, point 1, **restée ouverte**.
**Verdict** : VALIDÉ — lint 0 erreur, 10/10 tests ciblés (install et update), 12/12 critères reçus,
reprise prouvée sur `lab_client` (3 lignes sur 7, +12.0 exactement, idempotente).
**Appris** :
- Une mise à niveau ne recalcule **pas** un champ stocké dont seul le corps du compute a changé :
  constaté sur `lab_client` (une location de 4 jours restait à 40.0). Tout changement de règle sur
  `amount_total` exige un script de reprise, sinon c'est vert en test et faux chez le client.
- Le dossier de migration porte la version cible : la montée de version ne peut pas attendre la clôture.
- D-01 (7 %) est morte mais vit encore au journal du 2026-08-01 ; un test de non-régression interdit
  désormais tout forfait proportionnel.
**Reste ouvert** : confirmer `author` du manifest ; clôture et recette complète (`/odoo-close`) ;
hors périmètre assumé — `Monetary`, contrainte de positivité, paramétrage du seuil.
