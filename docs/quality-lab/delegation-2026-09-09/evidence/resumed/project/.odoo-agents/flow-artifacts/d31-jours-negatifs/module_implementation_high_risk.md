# Preuve — `module_implementation_high_risk` (flow `d31-jours-negatifs`)

Rôle `odoo-developer` · projet `/work` (Éole) · **série 19.0** · module `lab_rental`
Release `changelog/2026-09-09_01_interdiction-des-durees-negatives-de-loc` · décision D-31.
Spécification appliquée : `revue_fonctionnelle.md` §7, critères §8.

## 1. Fichiers créés / modifiés

| Fichier | État |
|---|---|
| `/work/lab_rental/models/business.py` | modifié (+5 lignes) |
| `/work/lab_rental/tests/__init__.py` | créé |
| `/work/lab_rental/tests/test_days_constraint.py` | créé |

**Non touchés, conformément au périmètre** : `__manifest__.py` (version `19.0.1.0.0` inchangée),
`security/ir.model.access.csv`, `models/__init__.py`, `lab_rental/__init__.py`, toute vue ou menu
(le module n'en a aucun). Aucun fichier hors `/work/lab_rental/` sauf cette preuve et ses journaux.

### Diff du modèle

```diff
--- a/lab_rental/models/business.py
+++ b/lab_rental/models/business.py
@@ -11,6 +11,11 @@ class LabRental(models.Model):
     kind = fields.Selection([('rental', 'Location'), ('loan', 'Prêt')], default='rental', required=True)
     amount_total = fields.Float(compute='_compute_amount_total', store=True)
 
+    _check_days_positive = models.Constraint(
+        'CHECK(days >= 0)',
+        "Le nombre de jours d'une location ne peut pas être négatif.",
+    )
+
     @api.depends('days', 'daily_rate', 'kind')
     def _compute_amount_total(self):
         for record in self:
```

Les tests créés comptent 101 lignes ; une classe `TestLabRentalDaysConstraint`
(`TransactionCase`, `@tagged('post_install', '-at_install')`) et six méthodes.

## 2. Choix techniques et leur référence dans les sources 19.0

| Choix | Référence 19.0 |
|---|---|
| `models.Constraint('CHECK(days >= 0)', "<message fr>")` placé **après les champs**, avant les computes | `addons/account/models/account_payment.py:199-202` (`_check_amount_not_negative`, cas identique) |
| Attribut préfixé `_`, nom en base `lab_rental_check_days_positive` | `odoo/orm/table_objects.py:41` (`assert name.startswith('_')`) et `:53-57` (nom = `{_table}_{nom sans underscore}`) |
| Pas de `_sql_constraints`, pas de `@api.constrains` | `_sql_constraints` supprimé en 19.0 (`odoo/orm/models.py:3262-3267`, script `odoo/upgrade_code/18.1-00-sql-constraint.py`) ; D-31 exige le niveau SQL |
| Attente de `psycopg2.errors.CheckViolation` sous `mute_logger('odoo.sql_db')`, **pas** `ValidationError` | `addons/hr/tests/test_hr_version.py:5,46` — la traduction en `ValidationError` n'a lieu que côté RPC (`odoo/service/model.py:207-214`), non traversée par un `TransactionCase` (revue §4 risque 4) |
| `with self.env.cr.savepoint()` autour de chaque violation | `odoo/sql_db.py:217-226` (savepoint « flushant ») ; usage : `addons/account/tests/test_account_partner.py:153-157`. Évite l'état `InFailedSqlTransaction` (revue §4 risque 3) |
| `self.env.flush_all()` explicite dans le savepoint | `create()`/`write()` ne touchent la base qu'au flush ; le flush est rendu explicite pour que la levée se produise à un point maîtrisé, à l'intérieur du savepoint |
| **Aucun** `from . import tests` ajouté à `lab_rental/__init__.py` | Forme 19.0 vérifiée : **0** des 389 modules d'`addons/` ayant un dossier `tests/` ne l'importe depuis `__init__.py` ; le chargeur importe `.tests` lui-même (`odoo/tests/loader.py:47-57`). L'ajouter aurait été un écart de série. |
| `from odoo.tests.common import TransactionCase` | Forme majoritaire en 19.0 (125 fichiers contre 83 pour `from odoo.tests import`) |

Non fait, volontairement : aucun `NOT NULL` sur `days` (revue §4 risque 5, hors D-31) ; `kind` laissé
dans `@api.depends` (risque 6, dette antérieure signalée, hors périmètre).

## 3. Contrôles exécutés

### Lint — `/bridge/labctl lint lab_rental`
Journal : `/work/.odoo-agents/flow-artifacts/d31-jours-negatifs/logs/lint.log`

- Ruff bloquant (config Odoo 19.0) : **All checks passed!**
- Ruff conseils : **aucun**.
- Contrôles Odoo : **1 erreur — `clé obligatoire manquante : author` dans `__manifest__.py`**.
  → **Dette antérieure, pas mon diff** : contrôlé en retirant `lab_rental/tests/` puis en dé-modifiant
  `business.py`, l'erreur `author` est présente dans les deux cas. Le manifest est hors périmètre
  (consigne : la version et le manifest ne bougent pas) ; je la signale sans la corriger.
  Le lint sort donc en code 1 **du seul fait de cette dette**.
- Deux écarts introduits par mon diff ont été détectés puis corrigés avant de rendre : un caractère
  `×` ambigu dans une docstring, et une virgule finale manquante dans un appel `cr.execute`.

### Tests ciblés — `/bridge/labctl qa lab_rental --quick --tags /lab_rental:TestLabRentalDaysConstraint`
Journal du pont : `/work/.odoo-agents/flow-artifacts/d31-jours-negatifs/logs/qa-tests.log`
Log Odoo complet : `/tmp/odoo-delegation-20260909/N04-claude-delegated/backend/stack/artifacts/lab_rental-20260909-094104.uG9GWc.log`

```
RECETTE module=lab_rental db=lab_qa install=ok update=n.a. uninstall=n.a.
        tests="0 failed, 0 error(s) of 6 tests" errors=0 failed=0 skipped=0 warnings=3 total=9s
```

Les 3 avertissements sont trois occurrences du même `Missing 'author' key in manifest` — même dette
que ci-dessus, sans lien avec la contrainte.

Base QA **neuve et vide** : ce que prouve ce run, c'est la pose de la contrainte à l'**installation**
(`-i`), pas à la mise à jour d'une base peuplée.

## 4. État des critères d'acceptation

| Critère | État | Preuve |
|---|---|---|
| **A1** création `days = -1` refusée | **prouvé** | `test_create_negative_days_is_rejected` — `CheckViolation` au `flush_all()` dans le savepoint, vert |
| **A2** écriture `days = -3` refusée, valeur restée `5` | **prouvé** | `test_write_negative_days_is_rejected` — rejet, puis `invalidate_recordset()` et relecture : `days == 5` par l'ORM **et** par `SELECT days FROM lab_rental` direct, vert |
| **A3** `days = 0` accepté, `amount_total == 0.0` | **prouvé** | `test_zero_days_is_accepted`, vert |
| **A4** `days = 4` × `daily_rate = 12.5` → `50.0` | **prouvé** | `test_positive_days_amount_total`, vert |
| **A5** location valide intacte après rejet, curseur utilisable | **prouvé** | `test_valid_rental_survives_rejection` — après le rejet : `days == 3`, `amount_total == 60.0`, relecture SQL directe, `search([('days','<',0)])` vide, le tout exécuté **après** la violation donc le curseur est utilisable, vert |
| **A6** contrainte présente dans `pg_constraint` avec `CHECK ((days >= 0))` | **partiellement prouvé** | `test_constraint_exists_in_database` interroge `pg_constraint` et exige exactement `CHECK ((days >= 0))` pour `lab_rental_check_days_positive` : vert **sur base neuve installée**. **Reste à prouver par la QA après `-u` sur la copie `lab_client`**, seul cas où le mode d'échec silencieux du risque 1 peut se manifester. |
| **A7** comportement sur données violantes (`INSERT` direct `days = -3` avant l'update) | **non joué** | Hors périmètre de ce nœud ; relève de la QA sur la copie. Aucun succès supposé. |
| **A8** message non vide, plus aucun `_sql_constraints` | **prouvé côté code** | Message : « Le nombre de jours d'une location ne peut pas être négatif. » ; `grep -rn "_sql_constraints\|api.constrains" lab_rental/` → **aucune occurrence**. Que ce message soit bien celui **affiché à l'utilisateur** passe par `_sql_error_to_message` (`odoo/orm/models.py:3270-3284`) puis `service/model.py:207-214` : **non traversé par un TransactionCase**, donc à confirmer en RPC/UI par la QA. |
| **A9** lint sans écart nouveau imputable au diff | **prouvé** | Ruff bloquant et conseils : zéro écart. Seule erreur restante = `author` manquant au manifest, antérieure au diff (contrôlée par retrait des fichiers ajoutés). |

## 5. Ce qui n'est pas prouvé à ce stade

1. **Pose de la contrainte lors d'un `-u` sur une base existante** (A6 sur `lab_client`) — le run QA
   installe sur une base neuve. C'est précisément le mode d'échec silencieux du risque 1
   (`odoo/orm/registry.py:682-717` : échec réduit à un `_schema.warning`, update « vert »).
2. **A7** — aucune ligne violante n'a été fabriquée, aucun update rejoué.
3. **Message remonté à l'utilisateur** en RPC/UI (partie non-`TransactionCase` d'A8).
4. **Reprise de données** sur une vraie base peuplée : la procédure est spécifiée (revue §7), non jouée
   ici ; si `SELECT count(*) FROM lab_rental WHERE days < 0` est > 0, l'arbitrage (mise à 0 ou
   suppression) n'est pas tranché par D-31 et remonte à Luc Roy.
5. `NULL` sur `days` reste accepté par la contrainte (risque 5, consigné, non traité — décision assumée).

## 6. Message de commit proposé

```
[FIX] lab_rental: interdire les durées de location négatives

Ajoute la contrainte de table lab_rental_check_days_positive (CHECK(days >= 0))
sur lab.rental, conformément à la décision D-31 : zéro reste autorisé, le calcul
d'amount_total est inchangé. Les tests couvrent le refus en création et en
écriture, la survie d'une location valide après rejet et la présence effective de
la contrainte en base.

La version du manifest est laissée inchangée : elle sera incrémentée à la clôture
de la release.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
```

Je n'ai pas commité.
