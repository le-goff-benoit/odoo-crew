# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-11 (remplacée par D-12) : recalculer tous les dossiers après correction des lignes. Un vieux ticket proposait de reconstruire aussi les validés ; proposition rejetée par D-12.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Recalcul des brouillons et reprise (release 2026-09-09_01, point 1)
**Demande** : corriger `action_recalculate` de `lab.dispatch` (lignes annulées comptées, dossiers
validés écrasés) et reprendre les brouillons existants sur la copie `lab_client`.
**Fait** : test rouge d'abord (6 échecs / 7 sur le code d'origine), puis filtrage des brouillons
**avant** l'écriture et exclusion des lignes `cancelled` ; script de reprise rejouable dans la release.
**Verdict** : VERT — lint ciblé 0 anomalie (partiel : `ruff` absent), install + update OK,
7/7 tests ciblés, reprise passe 1 = 1 écriture, passe 2 = 0 écriture, validé id=2 figé à 777,00.
**Appris** :
- Écarter les validés par `filtered` avant le `write` : recalculer puis comparer touche `write_date`,
  ce que « strictement inchangé » interdit.
- Un test de non-écriture n'est discriminant qu'en repoussant `write_date` dans le passé : dans une
  même transaction elle vaut déjà l'horodatage de la transaction.
- `labctl qa … --quick` peut rendre un **faux vert** : `-u` sur un module non installé ne collecte
  aucun test et le verdict reste « propre ». Lire le compte de tests, pas le verdict.
- Corriger le calcul ne corrige pas les valeurs en base : la reprise est un livrable à part entière.
**Reste ouvert** : release ouverte — recette complète, captures, guide et version du manifest à
`/odoo-close`. Leçon candidate (faux vert `--quick`) à porter par `/odoo-feedback`.
