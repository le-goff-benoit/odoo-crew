# Journal

## 2026-09-14 — Ancienne QA
**Fait** : tests de création simples verts ; ni données historiques, ni sélection mixte.
**Reste ouvert** : demande actuelle et reprise.

## 2026-09-16 — B-42, correction et reprise locale
**Demande** : réparer action_repair et les brouillons historiques de la société initiale ; arbitrage decisions/current.md.
**Fait** : self/draft/société active, tri date/id, pas 100, total hors cancelled ; suppression sudo et écritures inutiles.
**Copie** : ids 1/2 = 100/20 et 200/15 persistés ; issued id 3, société 2 id 4 et huit lignes inchangés.
**Preuves** : six tests rouges puis six verts ; update réussi ; droits ordinaires positifs/négatifs ; rejeu zéro write et métadonnées stables.
**QA** : critères métier satisfaits ; lint diff/Ruff conformes, dette author préexistante du manifest conservée ; relecture non indépendante.
**Appris** : accès multi-société ≠ société active ; ancien PASS de création vide inapplicable ; Fault RPC seul ≠ preuve de réparation.
**Dossier** : changelog/2026-09-15_01_repair/{revue_fonctionnelle.md,qa.md,proofs/}.
**Reste** : release ouverte, recette de clôture/incrément ultérieurs ; aucun déploiement distant. Temps/jetons non mesurables dans ce banc.
