# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-11 (remplacée par D-12) : recalculer tous les dossiers après correction des lignes. Un vieux ticket proposait de reconstruire aussi les validés ; proposition rejetée par D-12.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Recalcul fiable des dossiers brouillons (release 2026-09-09_01, point n°1)
**Demande** : corriger `lab.dispatch.action_recalculate` et reprendre les brouillons de la copie synthétique.
**Fait** : filtre `state == 'draft'` + exclusion des lignes `cancelled` ; migration `19.0.1.0.1/post-migrate.py`
idempotente ; 5 tests ; manifest 19.0.1.0.0 → 19.0.1.0.1.
**Verdict** : VALIDÉ (QA renforcée, données existantes). Test rouge 4/5 avant, 5/5 vert après ;
reprise rejouée deux fois sur `lab_client` sans dérive (999,00 → 20,00 ; validé 777,00 intact).
**Appris** : « strictement inchangé » (D-12) se lit au sens fort — on saute le dossier validé, on ne le
réécrit pas avec la même valeur ; `write_date` sert de preuve. Corriger le calcul ne corrige pas les
données : la reprise exige un incrément de version, sinon la migration ne se déclenche jamais.
**Reste ouvert** : `author` manquant dans le manifest (dette antérieure, à arbitrer) ; `ruff` absent de
l'environnement donc étape 1/3 du lint ignorée ; release **laissée ouverte** — clôture par `/odoo-close`.
