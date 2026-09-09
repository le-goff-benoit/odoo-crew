# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-11 (remplacée par D-12) : recalculer tous les dossiers après correction des lignes. Un vieux ticket proposait de reconstruire aussi les validés ; proposition rejetée par D-12.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Recalcul juste des dossiers et reprise des brouillons
**Demande** : corriger `lab.dispatch.action_recalculate` (lignes annulées comptées, dossiers validés écrasés) et reprendre les brouillons existants. Release `2026-09-09_01`, point 1, laissée ouverte.
**Fait** : test rouge d'abord (4 FAIL + 3 ERROR, `110.0 != 20.0` et validé écrasé 777 → 110) ; filtrage `state == 'draft'` avant toute affectation ; `_get_snapshot_total` exclut `cancelled` ; `_repair_draft_snapshots` n'écrit qu'en cas d'écart ; migration `19.0.1.0.1/post-recalcul_brouillons.py`. Reprise jouée sur `lab_client` : 2 dossiers repris, rejeu à 0 repris / 0 write.
**Verdict** : VERT — 7/7 tests ciblés, 7/7 critères, QA renforcée (données existantes) jouée tout de suite.
**Appris** :
- D-12 « strictement inchangé » = **aucune écriture**, pas seulement même valeur : le filtre d'état va avant l'affectation, jamais après.
- `write_date` ne prouve rien dans un test unitaire (horodatage de transaction) ; espion sur `write` en test, `write_date` seulement entre transactions sur la copie.
- Pas de tolérance d'arrondi dans une reprise que le contrat ne prévoit pas : l'écart de 0,004 de LEGACY_FRACTION était un vrai écart.
- Corriger la méthode ne corrige pas les valeurs stockées : la reprise exige l'incrément de version du manifest pour être jouée.
**Reste ouvert** : clé `author` absente du manifest (dette antérieure, valeur à décider) ; `ruff` absent du poste, une voie de lint non jouée ; clôture et recette complète via `/odoo-close`.
