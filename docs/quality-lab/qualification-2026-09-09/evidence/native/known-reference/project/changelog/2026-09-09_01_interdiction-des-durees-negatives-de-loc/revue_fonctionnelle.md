# Revue fonctionnelle — D-31 : interdire les durées négatives sur `lab.rental`

**Projet** Éole (`/work`) · **série** 19.0 · **module concerné** `lab_rental` · **modèle** `lab.rental`
**Flow** `d31-jours-negatifs` · nœud `functional_review` · **décision de référence** `/work/decisions/2026-09-08.md` (D-31, Luc Roy)

## 1. Ce que je comprends

*En tant que gestionnaire de locations, je veux que la base refuse une durée négative afin qu'aucun total de location ne soit calculé à l'envers.*

Périmètre : ajout d'une contrainte de table `days >= 0` sur `lab.rental`, avec zéro accepté ; `daily_rate`
et le calcul `amount_total = days × daily_rate` restent inchangés ; tests de refus en création et en
écriture, plus la survie d'une location valide après un rejet. Aucune vue, aucun droit.

**Problème réel** : `days` est aujourd'hui un `fields.Integer(default=0)` sans borne
(`/work/lab_rental/models/business.py:9`) et le total est stocké (`amount_total`, compute stocké) — une
saisie négative produit donc un montant négatif persisté et propagé. Le `JOURNAL.md` du projet
(entrée 2026-08-01) précise que cette tolérance était **volontaire** pour des essais : ce n'est pas une
régression mais un changement de contrat, ce qui déplace le risque vers les **données existantes**.

Deux questions sont closes par D-31 et **non rouvertes ici** : borne zéro incluse ; contrainte **SQL**
(et non `@api.constrains`).

## 2. Verdict standard Odoo 19.0

**À DÉVELOPPER** — mais en réemployant strictement le mécanisme standard, sans une ligne de logique métier.

Odoo 19.0 fournit l'objet de table `Constraint`, exposé sous `models.Constraint` :

- `~/odoo-sources/19.0/odoo/orm/table_objects.py:79` — `class Constraint(TableObject)` ;
  signature `__init__(self, definition: str, message: ConstraintMessageType = '')`
  (`table_objects.py:82-101`). La docstring donne exactement notre cas : `CHECK (x > 0)`.
- Export : `~/odoo-sources/19.0/odoo/models/__init__.py:25`
  → `from odoo.orm.table_objects import Constraint, Index, UniqueIndex`.
- Nommage imposé : l'attribut de classe **doit commencer par `_`**
  (`table_objects.py:41` : `assert name.startswith('_')`), et le nom en base devient
  `{_table}_{nom sans underscore}` (`table_objects.py:53-57`) → ici `lab_rental_check_days_positive`.
- Modèle à copier tel quel, cas identique au nôtre :
  `~/odoo-sources/19.0/addons/account/models/account_payment.py:199-202`
  ```
  _check_amount_not_negative = models.Constraint(
      'CHECK(amount >= 0.0)',
      'The payment amount cannot be negative.',
  )
  ```
- Le message est remonté à l'utilisateur via `_sql_error_to_message`
  (`~/odoo-sources/19.0/odoo/orm/models.py:3270-3284`), puis converti en `ValidationError`
  côté RPC dans `~/odoo-sources/19.0/odoo/service/model.py:207-214`.
- `_sql_constraints` **n'existe plus** en 19.0 : seule reste l'application des `_table_objects`
  (`~/odoo-sources/19.0/odoo/orm/models.py:3262-3267`), et un script de migration dédié acte la bascule
  (`~/odoo-sources/19.0/odoo/upgrade_code/18.1-00-sql-constraint.py`). Utiliser `_sql_constraints`
  serait un défaut de série, pas un style.

**Série suivante** : la forme `models.Constraint` est celle introduite en 18.1/19.0 et conservée en
19.x ; le développement ne crée aucune dette de migration.

## 3. Voies possibles

| Voie | Effort | Ce que l'utilisateur obtient | Coût à la migration | Recommandée |
|---|---|---|---|---|
| Configuration seule | — | Rien : aucun paramètre standard ne borne un Integer custom | — | non |
| Studio / base | faible | Une règle applicative contournable par import/RPC, non garantie en base | moyen | non |
| Code custom (`odoo-developer`) | ~1 h | Refus au niveau base, toutes voies confondues (UI, import, RPC, SQL applicatif) | quasi nul (forme standard) | **oui** |

**Justification de la voie** : le projet possède déjà un module custom (`/work/lab_rental`) qui porte le
champ `days` ; la règle appartient au même module que le champ, et D-31 exige une contrainte SQL —
que Studio ne sait pas poser. → `odoo-developer`.

## 4. Contradictions et risques

| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|---|---|---|---|
| 1 | **Haute** | Une contrainte SQL ajoutée sur une table contenant déjà des lignes violantes **échoue silencieusement** en mode `-u`. Preuve : `registry.post_constraint` capture l'exception et, hors installation, se contente d'un `_schema.info` puis d'un report (`~/odoo-sources/19.0/odoo/orm/registry.py:682-701`) ; `finalize_constraints` réessaie et, en cas d'échec, ne fait qu'un `_schema.warning` (`registry.py:703-717`). L'update se termine **en succès apparent, sans contrainte en base**. | Le module s'installerait « vert » alors que la règle D-31 n'est pas appliquée chez le client. C'est le risque numéro un de cette tâche. | La QA de tâche doit **prouver la présence de la contrainte en base** (`pg_constraint`), pas seulement l'absence d'erreur à l'update. Critère A6. |
| 2 | **Haute** | État réel de la copie `lab_client` : **0 enregistrement** `lab.rental`, donc **0 avec `days < 0`**. Contrôlé le 2026-09-09 en lecture via `/bridge/labctl shell` (voir §5 preuve). | Bonne nouvelle pour l'application de la contrainte, mais **la copie ne reflète pas** l'historique décrit au journal (durées négatives tolérées). La copie ne prouve donc **rien** sur la vraie base client. | Ne pas conclure « pas de reprise nécessaire ». La QA doit **fabriquer** une ligne à `days = -3` puis rejouer l'update pour vérifier le comportement (critère A7), et la procédure de reprise doit être écrite même si la copie est vide. |
| 3 | Moyenne | « Conservation d'une location valide après rejet » : une violation `CHECK` met le curseur PostgreSQL en état **aborted** ; toute requête suivante du test échoue avec `InFailedSqlTransaction` si l'exception n'est pas capturée dans un savepoint. | Le test « la location valide existe toujours » ne peut pas s'exécuter sans précaution, ou pire, passera pour une mauvaise raison. | Encadrer chaque violation attendue par `self.env.cr.savepoint()` (`~/odoo-sources/19.0/odoo/sql_db.py:217-226`), sur le modèle de `~/odoo-sources/19.0/addons/account/tests/test_account_partner.py:153-157`. |
| 4 | Moyenne | Le point de levée dépend du **flush** : `create()`/`write()` ne touchent la base qu'au flush. L'erreur remonte en `psycopg2.errors.CheckViolation` (sous-classe d'`IntegrityError`) et **pas** en `ValidationError` : la traduction en `ValidationError` a lieu dans la couche RPC (`service/model.py:213`), non traversée par un `TransactionCase`. | Un test écrit avec `assertRaises(ValidationError)` serait rouge alors que le code est bon. | Tester `psycopg2.errors.CheckViolation` avec `mute_logger('odoo.sql_db')`, exactement comme `~/odoo-sources/19.0/addons/hr/tests/test_hr_version.py:46`. Forcer le flush (`self.env.flush_all()`) dans le savepoint. |
| 5 | Basse | La colonne `days` est **nullable** en base (contrôlé : `is_nullable = YES`). `CHECK (days >= 0)` laisse passer `NULL` (résultat *unknown*). | Une valeur nulle échapperait à la règle. | Accepté en l'état : l'ORM écrit `0` par défaut (`default=0`) et D-31 ne parle pas de NULL. Consigné, pas traité. Ne pas ajouter de `NOT NULL` : ce serait hors décision et un second risque de données. |
| 6 | Basse | `_compute_amount_total` dépend de `kind` (`business.py:15`) sans l'utiliser. | Dette antérieure, recalculs inutiles. | **Hors périmètre** : ne pas y toucher dans cette tâche, la signaler seulement. |
| 7 | Basse | Non-dits balayés : pas de multi-société, multi-devise, portail, mobile ni archivage sur ce modèle (`business.py` n'a ni `company_id`, ni `active`, ni `currency_id`). Aucun droit à modifier (`security/ir.model.access.csv` inchangé). | Aucun. | Aucun. |

## 5. Preuve du contrôle sur la copie `lab_client`

Exécuté en lecture seule le 2026-09-09 via `/bridge/labctl shell` (aucun `commit`) :

```
PREUVE lab_client / lab.rental
total          = 0
days < 0       = 0
days = 0       = 0
SQL direct days<0 = 0
contraintes existantes: [('lab_rental_pkey', 'PRIMARY KEY (id)'),
                         ('lab_rental_create_uid_fkey', ...),
                         ('lab_rental_write_uid_fkey', ...)]
module state: installed  latest_version: 19.0.1.0.0
colonne days : integer, is_nullable = YES
```

**Lecture du résultat, sans embellissement** : la contrainte s'appliquera sans obstacle sur cette copie —
mais parce qu'elle est **vide**, pas parce que les données sont saines. La copie fournie ne contient pas
les données synthétiques annoncées dans le briefing ; je le signale plutôt que de le supposer. Le
contrôle « pas de blocage à l'update » réalisé sur cette copie n'a donc **aucune valeur probante** pour
une base réellement peuplée : d'où le critère A7, qui exige de fabriquer le cas violant.

## 6. Hypothèses retenues (à défaut de réponse)

- H1 — La règle vaut pour **tous** les `kind` (`rental` et `loan`) : D-31 ne distingue pas.
- H2 — Aucune reprise de données à effectuer sur la copie (elle est vide) ; la procédure de reprise est
  néanmoins spécifiée pour la vraie base (§7).
- H3 — `NULL` sur `days` reste toléré (risque 5).
- H4 — Message d'erreur en français, le projet étant francophone.
- H5 — Aucune mise en production dans le cadre de cette tâche (D-31 : « aucune mise en production »).

## 7. Spécification

### Modèle de données
- `lab.rental` : ajouter un objet de table, **pas** un champ ni une méthode :
  `_check_days_positive = models.Constraint('CHECK(days >= 0)', "<message>")`, placé après les champs,
  sur le modèle de `account_payment.py:199`. Nom en base attendu : `lab_rental_check_days_positive`.
- Aucun changement sur `name`, `days`, `daily_rate`, `kind`, `amount_total`, ni sur `_compute_amount_total`.
- **Interdit** : `_sql_constraints` (supprimé en 19.0), et `@api.constrains` (D-31 exige le niveau SQL).

### Comportement
- `days < 0` → refus en base, en création comme en modification, quelle que soit la voie (UI, import, RPC).
- `days = 0` → accepté, `amount_total = 0`.
- `days > 0` → inchangé, `amount_total = days × daily_rate`.
- Après un refus, la transaction courante est invalidée : les enregistrements déjà validés ne sont pas
  altérés (comportement PostgreSQL, à prouver par test).

### Interface
Aucune vue, aucun menu, aucun champ visible ajouté. Le seul effet visible est un message d'erreur.

### Sécurité
Aucun changement : `security/ir.model.access.csv` reste tel quel. Aucun groupe, aucune règle
d'enregistrement. Une contrainte de table s'applique aussi à `sudo()` — c'est voulu.

### Reprise de données
1. Avant tout `-u` sur une base peuplée : `SELECT count(*) FROM lab_rental WHERE days < 0;`
2. Si le compte est > 0 : **corriger les lignes d'abord**, arbitrage métier requis (mise à 0 ou
   suppression) — non tranché par D-31, donc à remonter à Luc Roy le cas échéant.
3. Puis seulement mettre à jour le module, et **vérifier la présence de la contrainte** (critère A6) :
   la seule absence d'erreur à l'update ne prouve rien (risque 1).
4. Sur `lab_client` : rien à corriger (0 ligne), étape 1 déjà faite et tracée ci-dessus.

### Hors périmètre
Vues et écrans ; droits d'accès ; `daily_rate` et la formule d'`amount_total` ; le `kind` superflu dans
`@api.depends` (risque 6) ; un éventuel `NOT NULL` sur `days` ; toute action sur une base de production.

## 8. Critères d'acceptation

- [ ] **A1** — Étant donné une location valide, quand on crée `lab.rental` avec `days = -1`,
      alors la base refuse : `psycopg2.errors.CheckViolation` au flush, sous `mute_logger('odoo.sql_db')`.
- [ ] **A2** — Étant donné une location existante à `days = 5`, quand on écrit `days = -3`,
      alors la base refuse de la même manière et la valeur en base reste `5`.
- [ ] **A3** — Étant donné une création avec `days = 0`, alors elle réussit et `amount_total == 0.0`.
- [ ] **A4** — Étant donné `days = 4` et `daily_rate = 12.5`, alors `amount_total == 50.0`
      (non-régression du compute stocké).
- [ ] **A5** — Étant donné une location valide créée puis un rejet (A1 ou A2) encadré par
      `self.env.cr.savepoint()`, alors, après le rejet, la location valide est toujours lisible avec
      ses valeurs intactes et le curseur reste utilisable pour la suite du test.
- [ ] **A6** — Après `-u lab_rental` sur la copie, la contrainte existe réellement :
      `SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='lab_rental'::regclass`
      retourne `lab_rental_check_days_positive` avec `CHECK ((days >= 0))`. Preuve à joindre à la QA.
- [ ] **A7** — Comportement sur données violantes, à jouer **explicitement** puisque la copie est vide :
      insérer une ligne `days = -3` en contournant l'ORM (`INSERT` SQL direct) **avant** l'update,
      rejouer l'update, et constater/documenter que la contrainte n'est **pas** posée alors que l'update
      se termine sans erreur (risque 1). Nettoyer la ligne, réappliquer, vérifier A6. Si ce contrôle ne
      peut pas être joué, le dire explicitement dans la QA — pas de succès supposé.
- [ ] **A8** — Le message d'erreur configuré est bien celui remonté à l'utilisateur (non vide),
      et le module ne contient plus aucune occurrence de `_sql_constraints`.
- [ ] **A9** — `labctl lint lab_rental` sans écart nouveau imputable au diff de la tâche.

## 9. Estimation et découpage

Un seul incrément, indivisible (contrainte + tests). Environ 1 h dev + QA.
**Niveau QA : renforcé** — la demande touche aux **données existantes** (changement de contrat sur un
champ déjà peuplé en clientèle, tolérance historique documentée au journal) et le mode d'échec
principal est silencieux. QA sur la copie `lab_client` obligatoire, avec A6 et A7.
Ni droits, ni comptabilité, ni facturation (D-31 : « aucune facturation »).

## 10. Ce que l'utilisateur verra

Rien de nouveau à l'écran. Un seul changement perceptible : la saisie d'un nombre de jours négatif,
jusqu'ici acceptée, est désormais refusée avec un message explicite (« Le nombre de jours d'une location
ne peut pas être négatif. »), et l'enregistrement n'est pas sauvegardé. Zéro jour reste autorisé.
À reprendre dans la communication de clôture pour les utilisateurs qui se servaient de valeurs négatives
comme d'un artifice d'essai : cet usage n'est plus possible.

VERDICT : module_high_risk
