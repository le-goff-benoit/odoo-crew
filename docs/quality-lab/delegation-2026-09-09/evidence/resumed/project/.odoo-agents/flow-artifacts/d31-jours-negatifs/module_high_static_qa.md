# QA de tâche — voie `graph-lane-static` (conformité statique et revue du diff)

Flow `d31-jours-negatifs` · projet `/work` (Éole) · série **19.0** · module `lab_rental`
Rôle `odoo-tester`, voie statique seule (lecture de `module_code`, aucune écriture dans le module).

## Verdict de la voie

**VERT AVEC RÉSERVE** — aucune anomalie de forme 19.0 trouvée dans le diff de la tâche ; le lint
échoue uniquement sur une dette antérieure (`author` manquant) hors périmètre. La réserve porte sur
l'impossibilité mécanique de `git diff` contre `.base`, contournée par une méthode de substitution
décrite ci-dessous, et sur le fait que ma voie ne prouve rien à l'exécution (A1-A7, une partie d'A6/A8).

## Commandes exécutées

| Commande | Code retour | Journal |
|---|---|---|
| `/bridge/labctl lint lab_rental` | 1 (échec) | `/work/.odoo-agents/flow-artifacts/d31-jours-negatifs/logs/r2-static/lint.log` |
| `git diff 9cf40f33b0e2d52d86f90d1c328e4d6f09de23de -- lab_rental` | échec (`fatal: bad object`) | commande interactive, non journalisée séparément — voir ci-dessous |
| `git log --oneline -a`, `git status`, `git show 762d6bd --stat`, `git show 762d6bd:lab_rental/models/business.py` | 0 | interactif |
| Lectures ciblées dans `~/odoo-sources/19.0` (`grep -n`, `sed -n`) pour chaque affirmation de forme | 0 | interactif |

Le lint sort en échec **uniquement** à cause de `clé obligatoire manquante : author` dans
`__manifest__.py` — Ruff bloquant : *All checks passed!*, Ruff conseils : aucun.

## Délimitation du diff de la tâche (contournement de l'échec `git diff`)

`git diff` contre le sha `9cf40f33b0e2d52d86f90d1c328e4d6f09de23de` référencé par
`changelog/2026-09-09_01_.../.base` échoue : `fatal: bad object 9cf40f33b0e2d52d86f90d1c328e4d6f09de23de`.
Confirmé : `git log --oneline -a` ne montre qu'un unique commit (`762d6bd Dossier synthétique initial`,
2026-09-09 09:45:21), `git status` est propre. Cette copie a été initialisée directement avec l'état
« déjà développé » du module — l'objet de base de la release n'existe donc pas dans cet historique.
`git diff`/`git blame` ne peuvent donc **pas** délimiter le diff de la tâche dans cette copie ; ce n'est
pas contournable par une autre commande git.

Méthode de substitution retenue, à trois sources croisées :
1. **Preuve du développeur** (`module_implementation_high_risk.md` §1) — tableau des fichiers
   créés/modifiés et diff explicite de `business.py` (+5 lignes : le bloc `_check_days_positive`
   uniquement) ; `tests/__init__.py` et `tests/test_days_constraint.py` marqués « créé ».
2. **Revue fonctionnelle** (§7 « Modèle de données ») — même bloc de contrainte annoncé, même
   contenu attendu, aucun changement sur `name`, `days`, `daily_rate`, `kind`, `amount_total`.
3. **Lecture du fichier réel** (`business.py`) — le bloc `_check_days_positive` (lignes 14-17)
   correspond exactement au diff annoncé par le développeur ; le reste du fichier (champs, compute)
   est identique à ce que la revue décrit comme préexistant (« `days` est aujourd'hui un
   `fields.Integer(default=0)` sans borne », §1).

Diff de la tâche retenu, sur cette base croisée : `business.py:14-17` (ajout du seul
`_check_days_positive`) + les deux fichiers `tests/__init__.py` et `tests/test_days_constraint.py`
en totalité. Tout le reste de `business.py`, ainsi que `__manifest__.py`,
`security/ir.model.access.csv`, `models/__init__.py` et `lab_rental/__init__.py`, est traité comme
préexistant / hors diff — cohérent avec le tableau « non touchés » de la preuve du développeur.

## Anomalies localisées

| Fichier:ligne | Gravité | Introduit par le diff ? | Constat |
|---|---|---|---|
| `lab_rental/__manifest__.py` (clé `author` absente) | Mineure (lint bloquant en sortie de code, mais sans lien avec la contrainte) | **Non** — dette antérieure. Vérifié : le manifest n'a pas été touché (absent des fichiers modifiés listés par le développeur, version toujours `19.0.1.0.0`, `data` toujours limité à `security/ir.model.access.csv`) ; aucun moyen de le reprouver par un diff avant/après faute d'objet git de base, mais la preuve croisée (déclaration du développeur + périmètre annoncé par la revue « aucune vue, aucun droit, manifest inchangé ») converge sans contradiction. | À corriger un jour, mais **hors périmètre de cette tâche** ; ne bloque pas D-31. |
| — | — | — | Aucune autre anomalie trouvée dans le diff de la tâche (business.py:14-17, tests/__init__.py, tests/test_days_constraint.py). |

Aucune anomalie de forme 19.0 : `models.Constraint` (et non `_sql_constraints`), nom d'attribut
`_check_days_positive` conforme (préfixe `_`, donc nom en base `lab_rental_check_days_positive`
d'après `~/odoo-sources/19.0/odoo/orm/table_objects.py:44,55-57`), message en français non vide,
placement après les champs et avant le compute (identique à
`~/odoo-sources/19.0/addons/account/models/account_payment.py:199-202`), aucun `self._cr` — seul
`self.env.cr` est utilisé dans les tests (`tests/test_days_constraint.py:23,24,28,38,75,91,99`), pas
de `from . import tests` dans `lab_rental/__init__.py` (contenu : `from . import models` seulement).

## Vérifications de forme faites dans les sources 19.0 (fichier:ligne, pas de mémoire)

| Affirmation à contrôler | Vérifié dans | Résultat |
|---|---|---|
| `models.Constraint` existe et prend `(definition, message='')` | `~/odoo-sources/19.0/odoo/orm/table_objects.py:79` (`class Constraint(TableObject)`), `:85` (`__init__`) | conforme |
| Export public `models.Constraint` | `~/odoo-sources/19.0/odoo/models/__init__.py:25` (`from odoo.orm.table_objects import Constraint, Index, UniqueIndex`) | conforme |
| Nom d'attribut doit commencer par `_` | `~/odoo-sources/19.0/odoo/orm/table_objects.py:44` (`assert name.startswith('_')`) — la revue fonctionnelle citait `:41`, léger décalage de 3 lignes sans conséquence sur le fond | conforme, écart de référence mineur (dans le document de revue, pas dans le code) |
| Nom en base = `{_table}_{nom sans underscore}` | `~/odoo-sources/19.0/odoo/orm/table_objects.py:55-58` (`full_name`) | conforme, `lab_rental_check_days_positive` attendu |
| Précédent exact `CHECK(x >= 0)` en standard | `~/odoo-sources/19.0/addons/account/models/account_payment.py:199-200` (`_check_amount_not_negative`) | conforme, décalage de référence négligeable (`:199-202` cité, `:199-200` la définition stricte) |
| `_sql_constraints` supprimé, seul `_add_sql_constraints`/`_table_objects` subsiste | `~/odoo-sources/19.0/odoo/orm/models.py:3244,3262` | conforme — aucune trace de l'ancien mécanisme par dictionnaire dans `orm/models.py` ; une unique occurrence résiduelle de la chaîne `_sql_constraints` existe ailleurs dans les sources standard (`addons/lunch/models/lunch_supplier.py`), sans rapport avec notre module |
| Message utilisateur remonté via `_sql_error_to_message` | `~/odoo-sources/19.0/odoo/orm/models.py:3270-3284` | conforme |
| `CheckViolation` (pas `ValidationError`) attendu en `TransactionCase`, sous `mute_logger` | `~/odoo-sources/19.0/addons/hr/tests/test_hr_version.py:4,9,46` (`from psycopg2.errors import CheckViolation`, `from odoo.tools import mute_logger`, `with self.assertRaises(CheckViolation), mute_logger('odoo.sql_db'):`) | conforme dans l'esprit — ce précédent standard n'utilise **pas** de savepoint explicite (contrairement au nôtre) |
| Motif `cr.savepoint()` pour encadrer une violation attendue | `~/odoo-sources/19.0/odoo/sql_db.py:216-217` (méthode `savepoint`) et usage `~/odoo-sources/19.0/addons/account/tests/test_account_partner.py:153-158` (`self.cr.savepoint()`) | conforme sur le principe ; le précédent standard encadre un `UserError` (pas un `CheckViolation`) et utilise `self.cr` plutôt que `self.env.cr` — les deux accès pointent vers le même curseur en `TransactionCase`, pas une anomalie |
| Chargement automatique de `tests/` sans `from . import tests` dans `__init__.py` | `~/odoo-sources/19.0/odoo/tests/loader.py:47-58` (`_get_tests_modules` / `find_spec('.tests', ...)`) | conforme, le chargeur importe lui-même le sous-paquet |
| `_sql_constraints` / `@api.constrains` absents du module | `grep -rn "_sql_constraints\|api.constrains" /work/lab_rental/` → aucune occurrence | conforme (A8) |

## Critères d'acceptation couverts par ma voie

| Critère | État | Preuve |
|---|---|---|
| **A8** — message non vide, zéro `_sql_constraints`/`@api.constrains` dans le module | **VERT** | Message présent et non vide (`business.py:16`) ; `grep -rn "_sql_constraints\|api.constrains" /work/lab_rental/` → aucune occurrence. La partie « message effectivement remonté à l'utilisateur en RPC/UI » (via `_sql_error_to_message`) n'est **pas** couverte par ma voie : non joué. |
| **A9** — lint sans écart nouveau imputable au diff | **VERT** | `lint.log` : Ruff bloquant *All checks passed!*, Ruff conseils aucun ; seule erreur = `author` manquant, dette antérieure au diff (voir méthode de délimitation ci-dessus), non introduite par la tâche. |
| Périmètre tenu (aucune vue, aucun droit, `daily_rate`/`amount_total` inchangés, version manifest inchangée) | **VERT** | `find /work/lab_rental -name "*.xml"` → aucun résultat ; `security/ir.model.access.csv` identique à la ligne unique attendue ; `business.py` ne modifie ni `daily_rate` ni le compute `_compute_amount_total` (formule `record.days * record.daily_rate` inchangée) ; manifest : `version = '19.0.1.0.0'`, `data = ['security/ir.model.access.csv']` — inchangés. |
| A1, A2, A3, A4, A5, A7 | **non joué** | Ce sont des critères d'exécution (tests, base peuplée) ; ma voie ne les couvre pas. Lecture du code : les tests correspondants existent et semblent structurellement corrects (savepoint, `flush_all`, relecture SQL directe pour A2/A5), mais je n'ai lancé aucun test — aucun vert attribué. |
| A6 | **non joué** (partiel, hors voie) | La contrainte est bien déclarée dans le code et son nom attendu (`lab_rental_check_days_positive`) est cohérent avec les règles de nommage 19.0 vérifiées ci-dessus, mais la présence réelle en base (surtout après `-u` sur `lab_client`, seul cas qui expose le risque 1) relève de l'exécution — non joué par ma voie. |

## Ce que ma voie ne prouve pas

- Aucune exécution de test : A1 à A5 et A7 restent entièrement à la charge des voies d'exécution
  (base QA, copie client). Je n'ai lancé ni `/bridge/labctl qa`, ni `update`, ni `shell`, conformément
  au périmètre qui m'est assigné.
- A6 n'est vérifié par ma lecture que sur la forme du code (nom, CHECK) — pas sur son effet réel en
  base, ni après un `-u` sur une base déjà peuplée, seul cas exposant le mode d'échec silencieux
  documenté au risque 1 de la revue fonctionnelle.
- A8 n'est couvert par ma voie que pour la partie statique (message non vide dans le code, absence de
  `_sql_constraints`/`@api.constrains`) ; la remontée effective du message à l'utilisateur via
  `_sql_error_to_message` puis la couche RPC n'est pas traversée par une lecture statique.
- Je n'ai pas pu produire de `git diff` réel entre l'état d'ouverture de la release et l'état actuel :
  la délimitation du diff de la tâche repose sur le croisement de trois sources documentaires
  (preuve du développeur, revue fonctionnelle, lecture du fichier), pas sur un diff git vérifiable
  mécaniquement. Si l'une de ces trois sources était fausse ou incomplète, ma délimitation du diff le
  serait aussi — je le signale comme limite structurelle de cette voie dans cette copie.
- Rien n'est dit sur l'état des deux autres voies QA en cours (exécution sur base QA, copie client) :
  je n'y ai pas touché, conformément à la consigne.
