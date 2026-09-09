# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-11 (remplacée par D-12) : recalculer tous les dossiers après correction des lignes. Un vieux ticket proposait de reconstruire aussi les validés ; proposition rejetée par D-12.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Recalcul des dossiers en brouillon (D-12)
**Demande** : corriger `lab.dispatch.action_recalculate` et reprendre les brouillons existants sur la copie synthétique.
**Fait** : test de non-régression écrit d'abord et **rouge sur le code d'origine** (5 échecs/6) ; `action_recalculate` filtre désormais `state == 'draft'` avant toute écriture et exclut les lignes `cancelled` ; reprise idempotente versionnée dans la release ; `author` ajouté au manifest (clé obligatoire manquante, valeur à confirmer).
**Verdict** : VALIDÉ — lint vert, 6/6 tests ciblés (install + update), reprise sur `lab_client` : LEGACY_DRAFT 999→20, LEGACY_DONE 777 intact, second passage `modifies=0`.
**Appris** : dans une même transaction, `write_date` vient de `cr.now()` et ne bouge pas — prouver « aucune écriture » demande un espion sur `write` en test ; `write_date` ne redevient discriminant qu'entre transactions (script sur la copie). Les deux preuves ont été produites.
**Reste ouvert** : release `2026-09-09_01` **ouverte** (1 point, 1 réalisé) — recette complète, captures et livrables à la clôture (`/odoo-close`). À arbitrer : valeur de `author` ; garde-fou d'idempotence « au bit près » sur les brouillons (non exigé par D-12) ; `digits` des `Float` (dette).
