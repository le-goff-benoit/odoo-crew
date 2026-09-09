# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-11 (remplacée par D-12) : recalculer tous les dossiers après correction des lignes. Un vieux ticket proposait de reconstruire aussi les validés ; proposition rejetée par D-12.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — D-12 : recalcul et reprise synthétique
**Demande** : corriger action_recalculate et reprendre les brouillons existants, copie locale uniquement.
**Fait** : revue D-12, test rouge réel (6 échecs), correction, 6 tests verts ; validés ignorés avant calcul, annulées exclues.
**Reprise** : lab_client, id 1 : 999 → 20 ; id 2 validé : 777 inchangé ; deuxième transaction : 0 modification, write_date compris.
**Verdict** : VALIDÉ — lint final, installation QA fraîche, mise à niveau copie, reprise et relecture persistée ; 6/6 critères.
**Preuves** : changelog/2026-09-09_01_recalcul-des-brouillons-d12/qa.md et rapports JSON/logs ; flow dispatch-d12, voie sensible.
**Appris** : D-12 remplace D-11 ; un snapshot validé ne se reconstruit pas. Une mise à niveau seule ne reprend pas les valeurs stockées.
**Reste ouvert** : release (1/1 point réalisé), recette complète et livraison via /odoo-close ; aucun déploiement ni commit créé.
