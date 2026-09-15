# Journal

## 2026-09-14 — Ancienne QA
**Fait** : tests de création simples verts ; ni données historiques, ni sélection mixte.
**Reste ouvert** : demande actuelle et reprise.

## 2026-09-16 — B-42 : correction et reprise locale
**Demande** : action_repair et brouillons historiques de la société initiale ; arbitrage decisions/current.md.
**Fait** : self/draft/société active, tri date/id, pas 100, exclusion cancelled, aucun sudo ; ACL/règles inchangées.
**Copie** : lab_client mise à jour ; IDs 1/2 commités à 100/20 et 200/15 sous utilisateur ordinaire 5 ; émis 3, autre société 4 et lignes intacts.
**QA** : 5 tests rouges puis les mêmes 5 verts ; droits ordinaires positifs/négatifs, second passage dans nouvelle transaction identique, zéro write au rejeu instrumenté.
**Statique** : Ruff bloquant vert ; lint Odoo rouge uniquement sur dette antérieure author absent, aucun défaut nouveau du diff.
**Appris** : PASS historique non applicable ; accès multi-société ≠ société active ; valeurs stables seules ne prouvent pas zéro écriture.
**Preuves** : changelog/2026-09-15_01_repair/qa.md, revue_fonctionnelle.md et proofs/ ; relecture non indépendante (LAB.md).
**Reste** : release ouverte, recette complète/incrément à clôture ; aucune production ni livraison. Temps/jetons inconnus faute de trace native, estimation du restant dans effort.json.
