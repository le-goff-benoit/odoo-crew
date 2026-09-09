# Frais de préparation révisés (D-03) — compte-rendu du point 2

**Projet** Atelier Boréal (work) · **série** 19.0 · **release** `2026-09-09_01_frais-de-preparation-des-locations`
(point n°2) · **module** `lab_rental` · **flow** `frais-preparation-d03`

## Cadrage
D-03 remplace D-02 dans la release en cours : 15 EUR à partir de 5 jours inclus, prêts exclus,
`jours × tarif` inchangé. Verdict standard inchangé — à développer, aucun module de location en
Community 19.0. Hors périmètre : paramétrage du seuil, `Monetary`, contrainte de positivité.

## Réalisation
`models/business.py` (constantes 15.0 / 5, docstring sur D-03), `__manifest__.py` en **19.0.1.2.0**,
`migrations/19.0.1.2.0/post-migrate.py` (nouveau), `tests/test_preparation_fee.py` réécrit (12 tests).
Le dossier `migrations/19.0.1.1.0/` est conservé.

## QA de tâche — VALIDÉ
Lint 0 · 12/12 tests ciblés en install et en update · reprise prouvée sur `lab_client` depuis l'état
D-02 (4 j 52.0 → 40.0, 7 j 152.0 → 155.0, 5 j tarif nul 12.0 → 15.0) · idempotence mesurée ·
périmètre non régressé · XML-RPC conforme aux bornes · **14/14 critères** (`qa_reception_point2.md`).

## Effet sur le point 1
Marqué **PÉRIMÉ** dans le README de la release et dans `qa.md`. Ses preuves sont conservées intactes.

## Reste à faire
Confirmer `author` du manifest. Reproposer le paramétrage seuil/montant. Clôture et recette complète
par `/odoo-close`, y compris le chemin d'un client encore en 19.0.1.0.0 (deux reprises successives).
