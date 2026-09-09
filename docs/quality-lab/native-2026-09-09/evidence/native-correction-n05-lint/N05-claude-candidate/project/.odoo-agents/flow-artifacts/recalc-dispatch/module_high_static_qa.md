# Fragment QA — voie statique (conformité et revue du diff)

## Lint
`/bridge/labctl lint lab_dispatch` — journal : `changelog/…/preuves/04_lint.log`

| Bloc | Résultat |
|---|---|
| ruff règles bloquantes (config Odoo 19.0) | **All checks passed** |
| ruff conseils (config complète) | **aucun** |
| contrôles Odoo (manifest, XML, sécurité, tests) | **1 erreur** : `__manifest__.py` — clé `author` manquante |

L'erreur `author` est de la **dette antérieure** : elle est présente dans
`git show HEAD:lab_dispatch/__manifest__.py` et signalée par Odoo dès le premier
chargement, avant toute modification. Elle n'est pas introduite par le diff. Elle n'est
pas corrigée ici parce que la valeur d'`author` est une donnée d'identité du projet, pas
un choix technique ; elle est remontée pour arbitrage.

Écarts introduits par le diff et corrigés au cours de la tâche : `unsorted-imports` et
`unnecessary-assign` (ruff, conseils) et une commande x2many en tuple dans les tests
(`Command.create` attendu). Tous à zéro au second passage.

## Revue du diff — conformité 19.0

- `from odoo import api, fields, models` ; `@api.model` sur la méthode de reprise, correct
  pour une méthode appelée sur le modèle sans enregistrement.
- `migrations/19.0.1.0.1/post-migrate.py` : arborescence confirmée dans les sources
  (`~/odoo-sources/19.0/odoo/modules/migration.py:138-140`, dossier `migrations`), signature
  `migrate(cr, version)` et `api.Environment(cr, SUPERUSER_ID, {})` conformes aux migrations
  du standard 19.0 (ex. `addons/l10n_at/migrations/3.2/post-migrate.py:6`).
- Déclenchement vérifié dans `migration.py:194-210` : le dossier contient plus de deux points,
  la version est donc prise telle quelle, et `19.0.1.0.0 < 19.0.1.0.1 <= 19.0.1.0.1` déclenche
  le script exactement une fois.
- Tests : `TransactionCase` + `@tagged('post_install', '-at_install')`, `Command.create` pour
  les x2many — formes attendues en 19.0.
- Aucune forme obsolète en 19.0 dans le diff : pas d'`attrs`/`states`, pas de `<tree>`, pas de
  `_sql_constraints`, pas de `self._cr`, pas de `groups_id`. Aucun XML, aucune vue.
- `ir.model.access.csv` non modifié : conforme à D-12 (« pas de changement de droits »).

## Revue de fond

- Le filtrage des validés est fait **avant** la boucle (`self.filtered(...)`), donc aucun
  `write` n'atteint un dossier validé — exigence « pas même recomputé » de D-12.
- La comparaison de reprise est exacte (`!=`) et non arrondie : justifiée en commentaire, et
  nécessaire, sans quoi la dérive `20.004` de `LEGACY_FRACTION` resterait en base.
- `_snapshot_amount` est partagé par l'action et la reprise : une seule définition du montant.

**Fragment : VERT**, sous réserve de la dette antérieure `author` remontée pour arbitrage.
