# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-11 (remplacée par D-12) : recalculer tous les dossiers après correction des lignes. Un vieux ticket proposait de reconstruire aussi les validés ; proposition rejetée par D-12.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Recalcul D-12 et reprise synthétique
**Demandé** : corriger action_recalculate et reprendre les seuls brouillons sur lab_client ; release ouverte.
**Fait** : filtrage des brouillons/lignes non annulées, validés sans écriture ni recalcul, 7 tests et reprise shell versionnée.
**Preuve rouge** : 6 échecs sur 7 avant correction ; défaut rejoué sur copie puis rollback vérifié.
**Verdict QA** : VALIDÉ — lint ciblé vert, installation/update et 7/7 tests ; trois voies sensibles vertes.
**Reprise** : LEGACY_DRAFT 999 → 20 ; LEGACY_DONE reste à 777 ; second passage 0 modification, relecture indépendante conforme.
**Appris** : D-12 remplace D-11 ; un correctif d'action ne répare pas les snapshots existants. Les validés restent figés.
**Candidate leçon** : --quick peut donner un faux vert sur une base vide existante ; contrôler le nombre de tests et l'état du module, pas seulement le code de sortie.
**Détail** : changelog/2026-09-09_01_recalcul-des-brouillons/qa.md ; flow recalculate → task_done.
**Reste ouvert** : release (1/1 point réalisé), recette complète/clôture sur demande ; auteur du manifest manquant préexistant. Aucun déploiement.
