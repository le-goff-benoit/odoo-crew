# Fragment QA — voie STATIQUE (D-03, point n°2)

Mode `graph-lane-static`. Série 19.0. Module `lab_rental`. Lecture seule.

## Lint des fichiers touchés

`odoo-lint.sh --changed 93525dd7a9 lab_rental` — 7 fichiers dans le périmètre.

| Passe | Résultat |
|---|---|
| ruff bloquant (config officielle 19.0) | **All checks passed** |
| ruff conseils (config complète) | **aucun** |
| contrôles Odoo (manifest, XML, sécurité, tests) | **0 erreur, 0 avertissement, 0 info** |

Preuve : `preuves/d03_lint.txt`. Deux allers-retours ont été nécessaires
(`import-outside-top-level` puis `unsorted-imports` sur le nouvel import de
`PREPARATION_FEE_MIN_DAYS`) ; l'état livré est propre sur les trois passes.

## Revue du diff

Fichiers touchés (`preuves/d03_diff_stat.txt`) :

- `lab_rental/models/business.py` — `PREPARATION_FEE 12.0 → 15.0`,
  `PREPARATION_FEE_MIN_DAYS 4 → 5`, en-tête et docstring réécrits sur D-03.
  Aucune modification de structure : `_preparation_fee()`, `@api.depends` et la
  définition du champ sont identiques.
- `lab_rental/__manifest__.py` — `19.0.1.1.0 → 19.0.1.2.0`, seule ligne changée.
- `lab_rental/migrations/19.0.1.2.0/post-migrate.py` — **nouveau**. Réapplique la
  formule courante ; ne calcule aucun delta.
- `lab_rental/tests/test_preparation_fee.py` — 11 tests, réécrits sur D-03.
- `lab_rental/migrations/19.0.1.1.0/` — **inchangé**, conservé volontairement.

**CA13 vérifié** : aucune vue, aucun droit (`security/ir.model.access.csv` non
touché), aucun champ ajouté, aucune dépendance ajoutée.

## Conformité 19.0

Rien de ce que la série impose ou proscrit n'est en jeu : le diff ne contient ni
XML, ni `attrs`/`states`, ni `<tree>`, ni `_sql_constraints`, ni `groups_id`, ni
`self._cr`. `api.Environment(cr, SUPERUSER_ID, {})` dans le `post-migrate` est la
forme en vigueur en 19.0.

## Résidus de la décision remplacée — CA12

`grep` sur `lab_rental/*.py`, dossier `migrations/19.0.1.1.0/` exclu : cinq
occurrences de « 12 », **toutes en commentaire ou docstring**, et toutes
explicitement historiques (« D-03 remplace D-02 (12 EUR dès quatre jours) »).
Aucun `12.0` ni `>= 4` actif. Le test
`test_fee_amount_and_threshold_are_the_ones_of_d03` verrouille les deux valeurs :
un retour silencieux à 12/4 casse un test.

## Verdict de la voie

**VERT.** Rien à signaler. Une observation pour la jointure : le module porte
maintenant deux dossiers de migration, dont un pour une décision qui n'a plus
cours — c'est correct (il sert une base restée en 19.0.1.0.0) mais cela mérite
une ligne dans les notes de la release pour que la clôture ne le supprime pas.
