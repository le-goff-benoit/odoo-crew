# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-11 (remplacée par D-12) : recalculer tous les dossiers après correction des lignes. Un vieux ticket proposait de reconstruire aussi les validés ; proposition rejetée par D-12.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Recalcul fiable des dossiers en brouillon (release 2026-09-09_01, point 1)
**Demande** : corriger `action_recalculate` de `lab.dispatch` et reprendre les brouillons existants.
**Fait** : test rouge d'abord (4 échecs / 5 sur le code fautif), puis filtrage sur `state == 'draft'`
et exclusion des lignes `cancelled` via `_get_lines_total()` ; reprise idempotente jouée deux fois
sur la copie `lab_client` (2 modifiés, puis 0).
**Verdict** : VALIDÉ — QA sensible à trois voies, 6/6 critères, `LEGACY_DONE` intact à 777.0.
**Appris** :
- Deux défauts vivaient dans la même ligne (lignes annulées comptées *et* validés écrasés) : les
  séparer dans deux tests distincts a évité qu'une seule correction masque l'autre.
- Une reprise qui compare des totaux avec une tolérance à 2 décimales laisse passer un écart de
  0,004 (`LEGACY_FRACTION`) : comparaison exacte, la précision monétaire n'est pas le contrat.
- Le total figé ne doit pas devenir un champ calculé stocké : un `compute` recalculerait les
  dossiers validés et violerait D-12.
**Reste ouvert** : release **ouverte** — clé `author` absente du manifest (dette antérieure à
`d6b5c10`) et emballage de la reprise en script de migration, à arbitrer à `/odoo-close`.
