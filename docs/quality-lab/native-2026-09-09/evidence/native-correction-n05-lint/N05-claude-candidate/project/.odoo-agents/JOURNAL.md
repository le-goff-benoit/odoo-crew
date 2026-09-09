# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-11 (remplacée par D-12) : recalculer tous les dossiers après correction des lignes. Un vieux ticket proposait de reconstruire aussi les validés ; proposition rejetée par D-12.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — action_recalculate : annulées exclues, validés figés, brouillons repris
**Demande** : corriger `action_recalculate` de `lab.dispatch` et reprendre les brouillons
existants sur la copie synthétique `lab_client` (contrat D-12, `decisions/2026-09-08.md`).
**Fait** : `_snapshot_amount` isole le montant hors lignes annulées ; `action_recalculate`
filtre les brouillons **avant** la boucle (un validé n'est donc pas écrit du tout) ;
`_reprise_snapshot_brouillons` n'écrit que si la valeur diffère ; migration
`19.0.1.0.1/post-migrate.py` ; 7 tests dans `lab_dispatch/tests/`.
**Verdict** : VERT — rouge d'abord prouvé (`110.0 != 20.0`, `110.0 != 777.0`, reprise
absente), puis 7/7 verts, base neuve propre, copie reprise 999.0→20.0 et 20.004→20.0,
`LEGACY_DONE` 777.0 avec `write_date` inchangée, rejeu à 0 correction. Release ouverte.
**Appris** : « figé » = *aucune écriture*, pas *même valeur* : filtrer avant la boucle.
Comparer un `Float()` sans `digits` avec une précision arrondie masque les dérives fines
(20.004 vs 20.0) : ici la comparaison exacte est la bonne, et elle est stable.
Une reprise de données doit être portée par une migration du module pour être rejouable ;
elle impose donc d'incrémenter la version **pendant** la tâche, pas à la clôture.
**Reste ouvert** : clé `author` absente du manifest (dette antérieure, fait échouer le lint)
— à trancher avant la clôture. Release `2026-09-09_01` ouverte, `/odoo-close` à venir.
