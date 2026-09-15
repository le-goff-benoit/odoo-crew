# Journal

## 2026-09-14 — Ancienne QA
**Fait** : tests de création simples verts ; ni données historiques, ni sélection mixte.
**Reste ouvert** : demande actuelle et reprise.

## 2026-09-16 — N-17 : préparation, duplication et reliquat
**Demande** : decisions/current.md, correction et reprise autorisée de la copie synthétique ; release ouverte.
**Fait** : cron drafts automatiques, zéro manuel préservé, duplication réinitialisée, reliquat au restant avec source done.
**QA** : 14 assertions rouges puis 9 tests verts ; installation/update QA et update lab_client réussis.
**Reprise** : ID 1 : 999→7 ; IDs 2/3/4 : 0/2/88 inchangés ; rejeu dans un nouveau shell stable, write_date compris.
**Verdict** : tâche reçue, 7 critères couverts, relecture non indépendante conformément à LAB.md.
**Dette** : author absent avant la tâche, lint global rouge sur ce seul défaut ; Ruff et diff sans défaut introduit.
**Appris** : une valeur zéro ne prouve pas une absence de saisie ; duplication et reliquat se contrôlent jusque dans le cron suivant.
**Preuves** : changelog/2026-09-15_01_repair/qa.md, coverage.json, preuves/ ; update.log prouve l'update malgré le reçu mal classé par --module.
**Reste** : recette complète et version à la clôture ; aucun commit/déploiement. Durées et jetons par rôle non mesurables faute de trace native.
