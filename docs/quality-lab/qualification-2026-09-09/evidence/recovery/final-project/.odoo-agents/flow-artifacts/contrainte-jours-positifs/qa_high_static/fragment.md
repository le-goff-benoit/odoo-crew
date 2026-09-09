# QA — voie conformité statique (`module_high_static_qa`)

**Propriétaire** `claude-r2-tester-static` · **module** `lab_rental` · **série** 19.0
**Release** `changelog/2026-09-09_01_interdiction-des-durees-negatives-sur-le/`
**Périmètre** : lecture seule, aucune exécution, aucune écriture en base.

## Verdict C01 — **pass**

Critère : « dans le code source du modèle, la contrainte `days >= 0` est
déclarée via `models.Constraint('CHECK(days >= 0)', ...)` et non
`_sql_constraints`. »

Extrait constaté, `lab_rental/models/business.py:8-11` :
```python
    _days_positive = models.Constraint(
        'CHECK(days >= 0)',
        "Le nombre de jours doit être positif ou nul.",
    )
```
- Forme `models.Constraint` (pas `_sql_constraints`) : conforme, seule forme
  valide en 19.0 (`~/.odoo19-agents/SERIES_MATRIX.md:31` : `_sql_constraints`
  est une erreur en 19.0, `models.Constraint` est la forme correcte).
- Expression SQL `CHECK(days >= 0)` : conforme à D-31 (Q1 borne zéro incluse,
  `/work/decisions/2026-09-08.md:1`) et à la revue fonctionnelle
  (`revue_fonctionnelle.md:37-40`).
- Message français littéral « Le nombre de jours doit être positif ou nul. » :
  comparaison caractère à caractère avec `/work/decisions/2026-09-08.md:4` —
  identique, ponctuation (point final) comprise.
- Placement dans le modèle : juste après `_description`, avant les champs —
  conforme à l'ordre imposé du guide 19.0 (attributs privés → objets de table
  déclaratifs → champs → compute), voir
  `~/.odoo19-agents/ODOO19_STYLE_GUIDE.md:186-194` et l'exemple de squelette
  `:156-166` qui place `models.Constraint` exactement à cette position.
- Confirmé par le lint (`ruff` bloquantes 19.0) : `All checks passed!`.

Aucune preuve manquante sur ce critère : **pass**, sans réserve.

## Revue du diff (comparé à `28fbbd6`)

```
git diff 28fbbd6 -- lab_rental/
 lab_rental/__manifest__.py    | 2 +-
 lab_rental/models/business.py | 5 +++++
 2 files changed, 6 insertions(+), 1 deletion(-)
+ non suivis (créés par la tâche) : lab_rental/tests/__init__.py,
  lab_rental/tests/test_days_constraint.py
```

Fichiers du module non touchés par le diff, vérifiés un par un :
`lab_rental/__init__.py`, `lab_rental/models/__init__.py`,
`lab_rental/security/ir.model.access.csv` — inchangés (`git diff` vide sur
`security/` et `views/`, ce dernier répertoire n'existe pas dans le module).

### Périmètre annoncé tenu

- **Aucune vue** : le module ne contient aucun fichier XML de vue, aucun
  diff sur ce plan.
- **Aucun droit** : `lab_rental/security/ir.model.access.csv` identique
  avant/après (`git diff` vide), une seule ligne d'accès pour `lab.rental`
  (`base.group_user`, CRUD complet), inchangée.
- **`_compute_amount_total` et le calcul du total inchangés** :
  `lab_rental/models/business.py:19-22` — `record.amount_total =
  record.days * record.daily_rate`, code strictement identique au diff (la
  méthode n'apparaît pas dans le patch, seule la nouvelle contrainte est
  ajoutée en amont).
- **Jours nuls toujours valides** : `days=0` respecte `CHECK(days >= 0)`
  (comparateur large `>=`), aucune modification du champ `days` (toujours
  `fields.Integer(default=0)`, `lab_rental/models/business.py:14`).

Aucune anomalie sur le respect du périmètre.

### Ligne éditoriale 19.0

- Ordre des membres du modèle : conforme (voir C01 ci-dessus). Pas de
  marqueur de section (`#=== FIELDS ===#` etc.) dans le fichier, mais le
  fichier ne les utilisait déjà pas avant la tâche (modèle à 4 champs, un
  seul compute) — dette antérieure hors diff, non introduite par la tâche,
  non bloquante au vu de la taille du modèle.
- `_description` déjà présent avant la tâche (`'Location synthétique'`),
  non touché.
- Forme de l'objet de table (`models.Constraint`) : conforme, voir C01.
- Message de contrainte : phrase complète, en français, point final —
  conforme au style attendu (`~/.odoo19-agents/ODOO19_STYLE_GUIDE.md:239-242`,
  exemple `"The name must be unique per company."`, forme équivalente en
  français ici).

Aucune anomalie de style introduite par le diff.

### Lecture des tests livrés (`lab_rental/tests/test_days_constraint.py`)

5 tests dans `TestLabRentalDaysConstraint(TransactionCase)`,
`@tagged('post_install', '-at_install')` :

1. `test_create_negative_days_is_rejected` (lignes 16-30) — `create` avec
   `days=-1` sous `assertRaises(IntegrityError)` + `savepoint()` +
   `mute_logger('odoo.sql_db')`, puis vérifie par `search` qu'aucun
   enregistrement partiel ne subsiste. Assertion significative : couvre bien
   le rejet **et** l'absence de résidu.
2. `test_write_negative_days_is_rejected` (lignes 32-49) — création valide,
   puis `write(days=-1)` rejeté, puis relecture (`invalidate_recordset` +
   accès aux champs) vérifiant `days=5`, `daily_rate=10.0`,
   `amount_total=50.0` inchangés. Assertion significative.
3. `test_zero_days_is_accepted` (lignes 51-70) — `days=0` accepté à la
   création et via `write` ramenant à 0, sur deux enregistrements distincts.
   Assertion significative (vérifie `days` et `amount_total`).
4. `test_amount_total_matches_days_times_daily_rate` (lignes 72-85) — calcul
   vérifié pour plusieurs valeurs, dont `days=0`. Assertion significative,
   mais ce test **déborde légèrement du périmètre C01** (il porte sur le
   calcul du total, pas sur la contrainte) — non anormal en soi puisque la
   revue fonctionnelle demande explicitement de vérifier la non-régression
   du calcul (§ Comportement, `revue_fonctionnelle.md:94`), remarque
   mineure seulement pour traçabilité.
5. `test_rejected_write_preserves_existing_valid_rental` (lignes 87-117) —
   rejet d'un `write(days=-1)`, puis `exists()`, relecture des 3 champs, et
   `search_count` égal à 1 sur le nom pour exclure un doublon partiel.
   Assertion significative, couvre bien C07 (conservation).

Aucun test qui n'assère rien de significatif, aucun test susceptible de
masquer un échec (les `assertRaises` encadrent bien l'opération qui doit
échouer, pas une opération annexe ; les `flush_all()` sont placés à
l'intérieur du bloc `with`, donc l'exception se déclenche au bon endroit).

**Non couvert par ces tests** (attendu, hors périmètre de cette voie) : les
critères C02 à C08 exigent une preuve **XML-RPC réelle** sur `lab_client`
(A8 du contrat, `decisions/2026-09-08.md:4`). Ces 5 tests `TransactionCase`
prouvent le comportement ORM interne, pas le message exact retourné sur le
canal XML-RPC (`ValidationError` encapsulant le message SQL, voir
`revue_fonctionnelle.md:61`, risque 1) ni la mise à jour du module sur
`lab_client`. Cette limite est déjà déclarée par l'implémentation
(`implementation.md:112-124`) et relève des autres voies QA du flow, hors
mandat de cette voie statique.

## Lint — dette antérieure vs anomalies introduites

Résultat `/bridge/labctl lint lab_rental` (journal complet :
`logs/lint.log`) :
```
Ruff (règles bloquantes 19.0) : All checks passed!
Ruff (conseils) : aucun
Contrôles Odoo : 1 erreur, 0 avertissement, 0 info
  ERREUR __manifest__.py : clé obligatoire manquante : `author`
```

Vérification de l'antériorité de cette erreur :
```
git show 28fbbd6:lab_rental/__manifest__.py
{'name': 'Atelier Boréal — frais de préparation des locations',
 'version': '19.0.1.0.0', 'license': 'LGPL-3', 'depends': ['base'],
 'data': ['security/ir.model.access.csv'], 'installable': True}
```
La clé `author` était déjà absente avant l'ouverture de la release — **dette
antérieure**, non introduite par le diff de cette tâche. Le seul changement
du manifest par le diff est `version: 19.0.1.0.0 → 19.0.1.1.0`, cohérent
avec une release à tâche unique. Non bloquant pour cette tâche ; ne pas la
corriger ici sort du périmètre annoncé (« aucune modification d'écran, de
droit, ni de règle de calcul » — la revue ne mentionne pas non plus
`author`, et la demande est explicitement bornée à la contrainte).

Aucune anomalie introduite par le diff de la tâche, statique ou de style.

## Récapitulatif

| Point | Verdict |
|---|---|
| C01 | **pass** |
| Périmètre du diff tenu (vues/droits/calcul inchangés) | conforme |
| Ordre des membres / forme `models.Constraint` / message littéral | conforme |
| Tests livrés : couverture et pertinence des assertions | conforme (dans la limite ORM, RPC hors mandat) |
| Lint | 1 erreur, dette antérieure, hors diff — pas d'anomalie introduite |

Aucune anomalie bloquante ni majeure sur le périmètre de cette voie
(conformité statique). Le point mineur relevé (test 4 débordant légèrement
sur le calcul du total) n'appelle pas de correction : il découvre une
propriété explicitement demandée par la spec, pas un défaut.

## Preuves

- `/work/lab_rental/models/business.py`
- `/work/lab_rental/__manifest__.py`
- `/work/lab_rental/tests/__init__.py`
- `/work/lab_rental/tests/test_days_constraint.py`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_high_static/logs/lint.log`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_high_static/fragment.md` (ce fichier)
