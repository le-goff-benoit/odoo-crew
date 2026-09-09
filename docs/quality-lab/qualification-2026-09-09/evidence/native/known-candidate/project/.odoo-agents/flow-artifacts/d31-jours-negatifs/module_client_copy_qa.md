# QA de tâche — voie `graph-lane-client-copy` — copie client `lab_client`

**Flow** `d31-jours-negatifs` · **projet** Éole (`/work`) · **série** 19.0 · **module** `lab_rental`
**Décision** D-31 (`/work/decisions/2026-09-08.md`) · **release**
`changelog/2026-09-09_01_interdiction-des-durees-negatives-de-loc/`
**Rôle** `odoo-tester`, mode tâche, voie copie client uniquement. Verrous : `module_code` lecture,
`client_copy` écriture. Aucun fichier de `/work/lab_rental/` modifié.

## Verdict de la voie

**VERT** — sur cette copie synthétique reconstituée, D-31 est tenue à tous les niveaux que ma voie
permet de contrôler : la contrainte SQL existe réellement après une mise à niveau explicite (A6), les
cinq scénarios A1-A5 se comportent conformément à la spécification, et le cas A7 — le seul que ma voie
puisse prouver — confirme **exactement** le risque n°1 signalé par la revue fonctionnelle : un `-u` sur
une base portant une ligne violante se termine sans exception, alors que la contrainte n'est **pas**
posée. Ce n'est pas une anomalie du module : c'est le comportement standard d'Odoo 19.0
(`odoo/orm/registry.py:682-717`), que la spécification anticipait déjà et pour lequel elle prescrit une
procédure de reprise (§7 de `revue_fonctionnelle.md`). Je le classe donc comme confirmation du risque
documenté, pas comme un défaut nouveau du module — mais c'est un point d'attention impératif pour la
clôture et pour toute vraie mise à niveau chez le client.

## État initial constaté de `lab_client` (avant toute action de ma voie)

Script : `scripts/r2_00_state_initial.py` — journal : `logs/r2-client/00_state_initial.log`

```
total lab_rental       = 0
days < 0               = 0
pg_constraint (avant)  = [('lab_rental_check_days_positive', 'CHECK ((days >= 0))'),
                          ('lab_rental_create_uid_fkey', ...), ('lab_rental_pkey', ...),
                          ('lab_rental_write_uid_fkey', ...)]
colonne days            = ('days', 'YES', 'integer')
module state             = installed  latest_version = 19.0.1.0.0
```

Constat important, distinct de ce qu'avait noté la revue fonctionnelle sur l'**ancienne** `lab_client` :
cette copie **neuve** est vide (0 enregistrement) mais porte déjà le code du module avec la contrainte,
posée dès l'installation initiale du snapshot — la contrainte n'était donc **pas** absente au départ. La
mise à niveau explicite demandée (`/bridge/labctl update`, étape suivante) reste nécessaire pour prouver
A6 au sens strict (« après `-u` »), et surtout pour dérouler le scénario A7 qui simule une base héritée
sans la contrainte.

## Commandes exécutées

| # | Commande | Journal | Objet |
|---|---|---|---|
| 1 | `labctl shell r2_00_state_initial.py` | `logs/r2-client/00_state_initial.log` | état initial |
| 2 | `labctl update` | `logs/r2-client/01_update.log` | mise à niveau explicite, base dans l'état initial |
| 3 | `labctl shell r2_02_a6_after_update.py` | `logs/r2-client/02_a6_after_update.log` | A6 après update |
| 4 | `labctl shell r2_03_a1_a5.py` | `logs/r2-client/03_a1_a5.log` | A1, A2, A3, A4, A5 |
| 5 | `labctl shell r2_04_a7_before.py` | `logs/r2-client/04_a7_before.log` | A7 — dépose de la contrainte + insertion SQL directe `days=-3` |
| 6 | `labctl update` | `logs/r2-client/05_a7_update.log` | A7 — rejeu de l'update sur base violante |
| 7 | `labctl shell r2_06_a7_after.py` | `logs/r2-client/06_a7_after.log` | A7 — constat post-update |
| 8 | `labctl shell r2_07_cleanup.py` | `logs/r2-client/07_cleanup.log` | nettoyage de la ligne violante |
| 9 | `labctl update` | `logs/r2-client/08_reapply_update.log` | réapplication propre |
| 10 | `labctl shell r2_09_final_state.py` | `logs/r2-client/09_final_state.log` | état final |
| 11 | `labctl shell r2_10_a8_message.py` | `logs/r2-client/10_a8_message.log` | A8 — message configuré |

Tous les scripts sont dans `scripts/`.

### Étape 2 — mise à niveau (`labctl update`)

Aucune erreur, aucun `WARNING odoo.schema`. Log complet dans `01_update.log`.

### Étape 3 — A6 après update

```
pg_constraint (après update) = [('lab_rental_check_days_positive', 'CHECK ((days >= 0))'), ...]
A6 = OK
```

### Étape 4 — A1 à A5 (RPC/ORM, savepoints)

```
A1 = OK (CheckViolation levee)
A2 = OK (CheckViolation levee)
A2_valeur_sql = 5
A2_valeur_orm = 5
A2_intacte = True
A3 = OK
A4 = OK
A5 = OK
A5_curseur_utilisable_count = 3
total apres nettoyage = 0
```

Chaque violation a été encadrée par `cr.savepoint()` ; `psycopg2.errors.CheckViolation` a bien été levée
au niveau base (pas `ValidationError`, conformément à ce que prévoyait le développeur : la traduction en
`ValidationError` n'a lieu qu'en couche RPC, non traversée ici). Après A2, la valeur relue **à la fois**
par l'ORM et par un `SELECT` SQL direct est restée `5`. Après A5, le curseur reste utilisable (un
`SELECT count(*)` a réussi juste après). Les enregistrements de test créés pour A2-A5 ont été supprimés
en fin de script ; la base est repassée à 0 ligne.

### Étapes 5-7 — A7 : cas des données violantes

C'est le contrôle central de ma voie, que ni la voie base neuve ni la voie exécution ne peuvent
produire.

**Avant l'update** (`04_a7_before.log`) : contrainte déposée par `ALTER TABLE ... DROP CONSTRAINT`, puis
une ligne insérée en SQL brut (`INSERT INTO lab_rental ... days=-3 ...`), contournant totalement l'ORM.

```
lignes violantes en base = 1
contraintes restantes    = [('lab_rental_pkey',), ('lab_rental_create_uid_fkey',),
                             ('lab_rental_write_uid_fkey',)]
```

**Rejeu de `labctl update`** (`05_a7_update.log`) — extrait significatif :

```
odoo.registry: module lab_rental: creating or updating database tables
odoo.schema: check constraint "lab_rental_check_days_positive" of relation "lab_rental" is violated by some row
odoo.modules.loading: Module lab_rental loaded in 0.03s, 48 queries (+48 other)
odoo.schema: check constraint "lab_rental_check_days_positive" of relation "lab_rental" is violated by some row
odoo.schema: check constraint "lab_rental_check_days_positive" of relation "lab_rental" is violated by some row
odoo.modules.loading: Modules loaded.
odoo.registry: Registry loaded in 2.407s
```

Le processus se termine **sans exception**, sans code d'erreur du pont : la ligne
`odoo.schema: ... is violated by some row` apparaît en `INFO`, `WARNING` **et** `ERROR` successivement
(exactement la séquence `post_constraint` → report → `finalize_constraints` décrite au risque n°1 de la
revue, `odoo/orm/registry.py:682-717`), mais l'update global affiche `Modules loaded.` et se termine
proprement.

**Constat après update** (`06_a7_after.log`) — la preuve décisive :

```
pg_constraint = [('lab_rental_create_uid_fkey', ...), ('lab_rental_pkey', ...), ('lab_rental_write_uid_fkey', ...)]
contrainte reposee malgre la ligne violante = False
lignes violantes toujours en base = 1
module state = installed
```

**Conséquence prouvée** : sur une base peuplée d'au moins une ligne `days < 0`, une mise à niveau
`-u` **réussit en apparence** (module `installed`, aucune erreur remontée à l'appelant) alors que la
contrainte `lab_rental_check_days_positive` **n'est pas posée**. La règle D-31 n'est donc **pas**
appliquée tant que la donnée violante subsiste, et rien dans la sortie normale de l'update ne l'indique
sans lecture des logs `odoo.schema` ou un contrôle explicite de `pg_constraint`.

**Procédure de reprise qui en découle** (confirme et précise §7 de la revue fonctionnelle) :
1. Avant tout `-u` sur une base réelle : `SELECT count(*) FROM lab_rental WHERE days < 0;`.
2. Si le résultat est `> 0`, **corriger ou purger ces lignes avant** la mise à niveau (arbitrage métier
   non tranché par D-31 — mise à 0 ou suppression — à faire valider par Luc Roy).
3. Rejouer la mise à niveau, puis **vérifier explicitement** `pg_constraint` (A6) : l'absence d'erreur à
   l'`-u` ne suffit pas, il faut vérifier la présence réelle de `lab_rental_check_days_positive` avec la
   bonne définition.
4. Ne jamais se fier au seul code de sortie du script d'update pour conclure que D-31 est appliquée sur
   une base peuplée.

**Nettoyage et réapplication** (`07_cleanup.log`, `08_reapply_update.log`, `09_final_state.log`) :
la ligne violante a été supprimée (`DELETE FROM lab_rental WHERE days < 0`, commit), puis l'update a été
rejoué sans aucun `WARNING odoo.schema` cette fois. État final :

```
pg_constraint = [('lab_rental_check_days_positive', 'CHECK ((days >= 0))'), ...]
A6 final = OK
total lab_rental final = 0
lignes violantes finales = 0
module state = installed  latest_version = 19.0.1.0.0
```

### Étape 11 — A8 (message d'erreur)

```
objet Constraint present : True
message configure   = "Le nombre de jours d'une location ne peut pas être négatif."
definition SQL      = 'CHECK(days >= 0)'
message == attendu  = True
grep _sql_constraints (vide attendu) : ''
nom de contrainte en base = ('lab_rental_check_days_positive',)
```

Le message configuré sur l'objet `models.Constraint` correspond au message attendu du critère A8, et
aucune occurrence de `_sql_constraints` ne subsiste dans le module. **Ce que je ne peux pas prouver
depuis `labctl shell`** : que ce message est bien celui qui traverse `_sql_error_to_message`
(`odoo/orm/models.py:3270-3284`) puis `service/model.py:207-214` pour arriver, sous forme de
`ValidationError`, jusqu'à un appel RPC/HTTP réel — `labctl shell` exécute dans un contexte serveur
direct, sans passer par la couche de service RPC. C'est un test qui appartient à l'écran (hors
périmètre de ma voie et de cette clôture de release selon la consigne).

## Tableau des critères couverts par ma voie

| Critère | État | Preuve |
|---|---|---|
| A1 création `days=-1` refusée | **OK** | `03_a1_a5.log`, `CheckViolation` levée dans savepoint |
| A2 écriture `days=-3` refusée, valeur restée 5 | **OK** | `03_a1_a5.log`, `A2_intacte = True` (SQL + ORM) |
| A3 `days=0` accepté, `amount_total=0.0` | **OK** | `03_a1_a5.log` |
| A4 `days=4 × 12.5 = 50.0` | **OK** | `03_a1_a5.log` |
| A5 location valide survit au rejet, curseur utilisable | **OK** | `03_a1_a5.log` |
| A6 contrainte présente après `-u` sur base existante | **OK** | `02_a6_after_update.log` et `09_final_state.log` |
| A7 comportement sur données violantes | **OK — risque confirmé** | `04_a7_before.log`, `05_a7_update.log`, `06_a7_after.log` : update « vert », contrainte non reposée |
| A8 message configuré non vide, `_sql_constraints` absent | **OK partiel** | `10_a8_message.log` — chemin RPC/UI non couvert par cette voie |
| A9 lint | hors voie | dévolu à `graph-lane-static`, non rejoué ici |

## État dans lequel je laisse la base

`lab_client` est laissée **propre** : module `lab_rental` installé (`19.0.1.0.0`), contrainte
`lab_rental_check_days_positive` (`CHECK ((days >= 0))`) présente en base, **0 ligne** dans
`lab_rental` (identique à l'état initial constaté). Aucune donnée résiduelle de test, aucune ligne
violante.

## Ce que ma voie ne prouve pas

- Le passage réel par la couche RPC/HTTP (`service/model.py`) qui traduit `CheckViolation` en
  `ValidationError` côté utilisateur : `labctl shell` reste en exécution serveur directe. La partie
  écran d'A8 reste à voir en interface, hors périmètre ici (revient à la clôture).
- Toute question de droits, compta, facturation : hors périmètre de D-31 et de ma voie.
- Le lint (`A9`) et la suite complète des tests automatisés sur `lab_qa` : dévolus aux deux autres voies
  QA en parallèle (statique, exécution) ; je n'y ai pas touché.
- Le comportement sur une base réellement peuplée de l'historique client (volumes, autres modèles
  liés) : `lab_client` reste une copie synthétique de laboratoire, pas la sauvegarde réelle du client.
- L'arbitrage métier de la procédure de reprise (mise à 0 ou suppression des lignes violantes) : non
  tranché par D-31, à remonter à Luc Roy le cas échéant — je ne me suis pas substitué à cette décision,
  je l'ai seulement vérifiée nécessaire et exécutée temporairement dans un scénario contrôlé, nettoyé
  ensuite.
