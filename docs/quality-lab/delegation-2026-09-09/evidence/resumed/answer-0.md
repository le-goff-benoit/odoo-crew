```
[3/4 tester]    VALIDÉ AVEC RÉSERVE — 3 voies rejouées, 6/6 tests, A1→A9 satisfaits, A7 reproduit sur la copie
[4/4 journal]   entrée écrite · PROJECT.md : D-31 actée + 2 pièges · flow TERMINÉ · release laissée ouverte
```

# Interdiction des durées négatives de location (D-31)

**Projet** Éole · **série** 19.0 (config + manifest) · **release** `changelog/2026-09-09_01_interdiction-des-durees-negatives-de-loc` (point n°1) · **module** `lab_rental`

## À décider
- **Lignes `days < 0` d'une base réelle** : D-31 ne tranche pas entre mise à 0 et suppression. La reprise de données est bloquée là-dessus → Luc Roy.
- **`author` manquant dans `__manifest__.py`** : dette antérieure au diff, le lint sort en échec pour ce seul motif. À corriger ou assumer.

## Reprise
Le flow existant a été repris, jamais recréé. Les trois voies QA portaient des revendications abandonnées par l'exécution interrompue : libérées avec motif (`odoo_flow.py release`), réattribuées à de nouveaux propriétaires `-r2`. La revue fonctionnelle et le code ont été repris tels quels — leurs preuves sont des vérifications de forme dans les sources 19.0, indépendantes de toute base. Les preuves d'exécution du run précédent ont été écartées : l'environnement a été reconstitué, tout a été rejoué aujourd'hui.

## Réalisation (reprise, non réécrite)
`lab_rental/models/business.py` : `_check_days_positive = models.Constraint('CHECK(days >= 0)', …)` — la forme 19.0, `_sql_constraints` étant supprimé de la série. `lab_rental/tests/test_days_constraint.py` : 6 tests, violations encadrées par `cr.savepoint()`, attente de `CheckViolation` et non de `ValidationError`. Manifest, vues, droits, `daily_rate` et `amount_total` intacts.

## QA de tâche — trois voies déléguées en une vague
Verrous compatibles : `module_code` en lecture partagée, trois écritures disjointes (`qa_db_module`, `client_copy`, trois fragments). J'ai vérifié chaque fragment et ses journaux avant de fermer son nœud.

| Contrôle | Résultat |
|---|---|
| Lint (Ruff bloquant + conseils) | aucun écart ; échec du seul fait de `author` |
| Tests ciblés, `lab_qa` neuve | 0 failed, 0 error / 6 tests — 11 s |
| Suite complète du module | 0 failed, 0 error / 6 tests — 6 s |
| Mise à niveau `-u` sur `lab_client` + `pg_constraint` | contrainte posée, aucun `WARNING odoo.schema` |
| A1→A5 rejoués en ORM sur la copie | conformes |
| A7 — ligne violante avant `-u` | risque reproduit, base remise propre |

**A1→A9 : neuf critères satisfaits.** A6 est prouvé là où il compte — après une vraie mise à niveau sur base existante, pas seulement à l'installation.

**A7 est le résultat qui compte** : avec une ligne `days = -3` insérée en SQL brut, `-u` se termine par `Modules loaded.` sans exception, et `pg_constraint` ne contient pas la contrainte. C'est le comportement standard de la série (`odoo/orm/registry.py:682-717`), pas un défaut du module — mais il signifie qu'une mise à niveau verte ne prouve pas que D-31 s'applique. La procédure de reprise est écrite dans `qa.md` et dans `PROJECT.md`.

## Reste à faire
- **A8 côté utilisateur non traversé** : ni `TransactionCase` ni `labctl shell` ne passent par la couche RPC. Que le message français soit celui affiché reste à voir à l'écran — c'est `/odoo-close`, aucun écran ne se produit pendant une release ouverte.
- `git diff` contre `.base` (`9cf40f33…`) échoue dans cette copie : l'objet git n'existe pas. La voie statique a délimité le diff par recoupement documentaire et le dit comme une limite, pas comme une preuve.
- `NULL` sur `days` reste accepté (hors D-31, assumé).
- Leçon candidate pour `/odoo-feedback` : une preuve d'exécution ne survit pas à la base sur laquelle elle a été prise ; à la reprise d'un flow, seules les preuves de forme tiennent.

## Release
1 point, 1 réalisé. **Release laissée ouverte** — flow `d31-jours-negatifs` TERMINÉ, 9 étapes. Clôture et recette complète : `/odoo-close`. Aucun écran, aucun droit, aucun déploiement, aucune écriture en production ; `lab_client` rendue dans son état initial (0 ligne, contrainte en place).