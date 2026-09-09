# Implémentation — Interdiction des durées négatives sur `lab.rental` (D-31)

**Nœud** `module_implementation_high_risk` · **module** `lab_rental` · **série** 19.0

## Fichiers créés / modifiés

```
 lab_rental/__manifest__.py    | 2 +-
 lab_rental/models/business.py | 5 +++++
 2 files changed, 6 insertions(+), 1 deletion(-)
```
+ créés (non suivis avant cette tâche) :
- `lab_rental/tests/__init__.py`
- `lab_rental/tests/test_days_constraint.py`

## Code de la contrainte

`lab_rental/models/business.py`, ajoutée juste après `_description`, avant les
champs (ordre éditorial 19.0 : attributs privés → objets de table → défauts →
champs → computes) :

```python
class LabRental(models.Model):
    _name = 'lab.rental'
    _description = 'Location synthétique'

    _days_positive = models.Constraint(
        'CHECK(days >= 0)',
        "Le nombre de jours doit être positif ou nul.",
    )

    name = fields.Char(required=True)
    days = fields.Integer(default=0)
    daily_rate = fields.Float(default=0)
    kind = fields.Selection([('rental', 'Location'), ('loan', 'Prêt')], default='rental', required=True)
    amount_total = fields.Float(compute='_compute_amount_total', store=True)
```

Aucun autre membre du modèle touché. Aucune vue, aucun droit
(`security/ir.model.access.csv` inchangé), aucun changement de
`_compute_amount_total`.

## Version du manifest

`19.0.1.0.0` → `19.0.1.1.0` (release à tâche unique livrée d'un coup, comme
demandé).

## Lint (`/bridge/labctl lint lab_rental`)

Verdict : **1 erreur préexistante, hors périmètre de la tâche** —
`clé obligatoire manquante : author` dans `__manifest__.py`. Vérifié via
`git show HEAD:lab_rental/__manifest__.py` : cette clé était déjà absente
avant toute modification de cette tâche (le module n'a jamais eu de champ
`author`). La demande interdit explicitement de toucher à autre chose que la
contrainte — je ne corrige pas cette dette, je la signale seulement.

- Ruff (règles bloquantes 19.0) : `All checks passed!`
- Ruff (conseils) : aucun
- Contrôles Odoo (manifest/XML/sécurité/tests) : 1 erreur (`author` manquant,
  dette antérieure), 0 avertissement, 0 info — rien sur le diff de la tâche.

Journal complet : `logs/lint.log`.

## Tests (`/bridge/labctl qa lab_rental --quick --tags /lab_rental:TestLabRentalDaysConstraint`)

Invocation avec `--tags` acceptée directement (pas de repli nécessaire).

Résultat : **5 tests, 0 échec, 0 erreur**, en 16s (install `-i` + tests).
```
RECETTE module=lab_rental db=lab_qa install=ok update=n.a. uninstall=n.a.
tests="0 failed, 0 error(s) of 5 tests" errors=0 failed=0 skipped=0
warnings=3 total=16s quick=16s
```
Les 3 avertissements relevés dans l'analyse des logs sont la même dette
antérieure (`Missing 'author' key in manifest for 'lab_rental'`), répétée à
chaque chargement de module — aucun avertissement lié au code ajouté.

Tests écrits (`lab_rental/tests/test_days_constraint.py`,
`TestLabRentalDaysConstraint`, `TransactionCase`,
`@tagged('post_install', '-at_install')`) :
1. `test_create_negative_days_is_rejected` — `create(days=-1)` lève
   `psycopg2.IntegrityError` au flush ; aucun enregistrement partiel ne
   subsiste ensuite (`search` sur le nom).
2. `test_write_negative_days_is_rejected` — `write(days=-1)` sur un
   enregistrement valide existant lève la même exception ; l'enregistrement
   relu conserve ses valeurs d'avant tentative.
3. `test_zero_days_is_accepted` — `days=0` accepté à la création et via un
   `write` ramenant `days` à 0.
4. `test_amount_total_matches_days_times_daily_rate` — `amount_total`
   recalculé correctement (`days * daily_rate`), y compris pour `days=0`.
5. `test_rejected_write_preserves_existing_valid_rental` — après le rejet
   d'un `write(days=-1)`, l'enregistrement existe toujours (`exists()`) avec
   ses valeurs d'avant tentative, et un seul enregistrement porte le nom
   utilisé (pas de doublon partiel).

Chaque cas de rejet est encadré par
`with self.cr.savepoint(), mute_logger('odoo.sql_db'), self.assertRaises(IntegrityError): ... ; self.env.flush_all()`,
motif vérifié dans les sources 19.0 (`odoo/addons/base/tests/test_sql.py::TestSqlTools.test_add_constraint`
pour `CheckViolation`/`assertRaises`, `addons/purchase/tests/test_purchase.py`
pour l'association `assertRaises(IntegrityError)` + `self.cr.savepoint()` +
`mute_logger` permettant de continuer à utiliser le curseur après le rejet).
`IntegrityError` est importé de `psycopg2` (classe mère de
`psycopg2.errors.CheckViolation`, comme dans `mail_group`/`hr_holidays`).

Journal complet du run QA (sortie intégrale du pont, y compris le journal
serveur Odoo) : `logs/qa.log`. Le chemin `.../artifacts/lab_rental-...log`
mentionné en fin de sortie est interne au conteneur Docker de l'autre côté du
pont, non accessible depuis ce bac à sable — j'ai donc conservé la sortie
complète telle que renvoyée par `/bridge/labctl`, qui contient déjà tous les
messages du serveur pour ce run.

## Limites / ce qui n'est PAS couvert par cette tâche

- **Pas de preuve XML-RPC réelle** (critère A8 et le message exact
  « L'opération ne peut pas être terminée : Le nombre de jours doit être
  positif ou nul. »). Cette tâche couvre le niveau ORM/`TransactionCase`
  (contrainte, conservation des données, calcul). D'après le graphe du flow
  (`odoo_flow.py status contrainte-jours-positifs`), la preuve RPC via
  `/bridge/labctl rpc` sur `lab_client` relève des nœuds QA qui suivent ce
  nœud d'implémentation, pas de ce nœud.
- **Pas de vérification de la mise à jour du module sur `lab_client`**
  (`/bridge/labctl update`) : hors périmètre de ce nœud (implémentation +
  tests sur base QA neuve), également confié à la suite du flow.
- Dette de manifest (`author` manquant) signalée, non corrigée.

## Fichiers concernés (chemins absolus)

- `/work/lab_rental/models/business.py`
- `/work/lab_rental/__manifest__.py`
- `/work/lab_rental/tests/__init__.py`
- `/work/lab_rental/tests/test_days_constraint.py`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/logs/lint.log`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/logs/qa.log`

ISSUE: done
