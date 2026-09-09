# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-01 : frais de préparation de 7 % pour toutes les locations. Cette décision est historique, remplacée par D-02.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Frais de préparation D-02
**Demande** : appliquer D-02 au total stocké, sans écran ni facturation ; release ouverte.
**Fait** : revue fonctionnelle, compute rental >= 4 jours +12 EUR, prêts exclus, 7 tests métier.
**QA** : VALIDÉ ; lint Ruff/Odoo 19.0 vert, installation/update et 7/7 tests réels, aucun ignoré.
**Copie** : update lab_client, reprise ORM stockée exécutée deux fois (30/40/40 → 30/52/40), entrées préservées ; fixtures nettoyées.
**Appris** : -u seul conserve les anciens totaux ; reprise explicite nécessaire. D-02 prévaut sur D-01, Q1/Q2 déjà tranchées.
**Outillage** : --quick sur une base sans module donnait zéro test ; installation explicite via le pont, sans modifier le dispositif.
**Candidate /odoo-feedback** : refuser la validation à zéro test ; choisir -i/-u selon l'état du module.
**Réserve** : auteur absent du manifest avant intervention, hors périmètre.
**Détail** : changelog/2026-09-09_01_frais-de-preparation-d-02/qa.md ; graphe preparation-d02.
**Reste ouvert** : release, recette complète et incrément de version à la clôture ; aucun déploiement.
