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

## 2026-09-09 — Frais de préparation révisés (D-03, remplace D-02)
**Demande** : D-03 (Alice Martin, `decisions/2026-09-09.md`) — 15 EUR à partir de **5 jours inclus**
au lieu de 12 EUR à partir de 4, dans la **même release**, déjà porteuse de D-02 réalisée et validée.
**Fait** : constantes du modèle à 15.0 / 5 ; manifest en **19.0.1.2.0** et
`migrations/19.0.1.2.0/post-migrate.py` (le dossier 19.0.1.1.0 n'aurait pas été rejoué sur une base
déjà à jour) ; 12 tests réécrits sur D-03, dont deux de non-régression sur D-01 et D-02. Point 1 de la
release marqué **PÉRIMÉ** dans README et `qa.md`, ses preuves conservées intactes.
**Verdict** : VALIDÉ — lint 0, 12/12 tests ciblés (install et update), 14/14 critères, reprise prouvée
sur `lab_client` **depuis l'état D-02** : 4 j 52.0 → 40.0, 7 j 152.0 → 155.0, 5 j tarif nul 12.0 → 15.0.
**Appris** :
- Une décision qui en remplace une autre **dans la même release** ne se rejoue pas : la QA précédente
  n'est pas « à refaire », elle est **fausse**, ses oracles contredisent la nouvelle règle. Il faut la
  marquer périmée là où on la lit (README, `qa.md`) sans effacer ses preuves.
- La reprise part de l'état **déjà migré**, pas de l'état d'origine : ici les montants **baissent**
  (52.0 → 40.0). Un `add_to_compute` le fait, un script « qui ajoute le forfait » ne l'aurait pas fait.
- Un second `-u` ne rejoue pas un post-migrate à version inchangée : il prouve l'absence de dérive,
  **pas** l'idempotence de la reprise, qui se mesure en rappelant son corps.
**Reste ouvert** : confirmer `author` du manifest ; le paramétrage seuil/montant reste hors périmètre
mais est à reproposer (3ᵉ écriture de la règle en 2 jours) ; clôture et recette complète (`/odoo-close`).
