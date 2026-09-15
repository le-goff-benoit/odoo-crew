# Journal

## 2026-09-14 — Ancienne QA
**Fait** : tests de création simples verts ; ni données historiques, ni sélection mixte.
**Reste ouvert** : demande actuelle et reprise.

## 2026-09-16 — N-17 : préparation et reprise locale
**Demande** : corriger cron, zéro manuel, duplication et reliquat ; reprendre la copie synthétique.
**Fait** : méthodes corrigées, neuf tests ; rouge métier confirmé puis vert (0 échec/erreur), installation/update et copie contrôlés.
**Reprise** : id 1, 999 → 7 ; ids 2/3/4 intacts à 0/2/88 ; rejeu sans write, commit et relecture indépendante de session.
**Verdict** : QA de tâche renforcée validée ; revue et preuves dans changelog/2026-09-15_01_repair/qa.md.
**Limites** : relecture non indépendante selon LAB.md ; lint global rouge uniquement pour author absent antérieurement, diff/Ruff propres.
**Appris** : zéro explicite ≠ automatique ; copy ouvre une nouvelle demande ; reliquat fige la source avant le prochain cron.
**Reste** : release ouverte, recette complète et version à la clôture ; aucun déploiement. Mesures natives indisponibles, estimation du restant conservée.
