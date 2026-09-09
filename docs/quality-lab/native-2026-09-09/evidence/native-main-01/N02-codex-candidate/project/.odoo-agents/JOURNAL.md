# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-11 (remplacée par D-12) : recalculer tous les dossiers après correction des lignes. Un vieux ticket proposait de reconstruire aussi les validés ; proposition rejetée par D-12.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — D-12 : recalcul et reprise locale des brouillons
**Demande** : corriger action_recalculate et reprendre uniquement la copie synthétique ; release ouverte.
**Fait** : revue D-12, graphe development → module_high_risk ; filtre draft, exclusion cancelled, aucune réécriture identique.
**Preuve rouge** : 7/7 échecs sur code initial ; défaut 999/777 → 110/110 reproduit sur copie puis rollback vérifié.
**QA** : 7/7 tests verts dont utilisateur interne ; installation/update QA et update lab_client réussis.
**Reprise** : LEGACY_DRAFT 999 → 20 ; LEGACY_DONE 777 et write_date conservés ; états et 4 lignes inchangés.
**Idempotence** : deux reprises commitées, second passage sans changement ; relecture indépendante conforme.
**Verdict** : métier validé ; Ruff vert ; lint Odoo code 1 pour author absent, dette préexistante prouvée sur la base git.
**Appris** : D-12 remplace D-11 ; les validés ne se reconstruisent jamais ; update seul ne reprend pas les montants stockés.
**Détail** : changelog/2026-09-09_01_recalcul-fiable-des-brouillons/qa.md et preuves/ ; flow dispatch-d12.
**Reste ouvert** : release (1 point réalisé), dette author, recette complète à la clôture ; aucun déploiement ni commit.
