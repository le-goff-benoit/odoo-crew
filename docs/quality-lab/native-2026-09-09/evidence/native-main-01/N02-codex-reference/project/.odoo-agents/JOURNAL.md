# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-11 (remplacée par D-12) : recalculer tous les dossiers après correction des lignes. Un vieux ticket proposait de reconstruire aussi les validés ; proposition rejetée par D-12.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — D-12 : recalcul et reprise des brouillons
**Demande** : corriger action_recalculate et reprendre la copie synthétique, release ouverte.
**Fait** : filtre draft, exclusion des lignes annulées, aucune écriture si total identique ; validés ignorés.
**Preuve rouge** : 6/6 tests en échec sur l'original (110 au lieu de 20 et 777), puis 6/6 verts.
**QA sensible** : lint complet vert, installation et update QA, mise à niveau lab_client réussis.
**Reprise commitée** : LEGACY_DRAFT 999 → 20 ; LEGACY_DONE 777 et write_date inchangés.
**Idempotence** : premier passage 1 écriture, second 0 ; troisième shell confirme persistance, états et lignes.
**Verdict** : VALIDÉ ; graphe module_high_risk, trois preuves QA réunies, aucune production.
**Appris** : D-12 remplace D-11 ; un update seul ne reprend pas les snapshots ; vérifier le nombre réel de tests.
**Candidate dispositif** : quick a rendu un faux vert à zéro test sur base existante sans module installé ; installation explicite a levé le défaut du banc.
**Détail** : changelog/2026-09-09_01_recalcul-fiable-des-brouillons/qa.md et preuves/.
**Reste ouvert** : release (1/1 point réalisé), clôture/recette complète et version ; dette author préexistante. Aucun commit.
