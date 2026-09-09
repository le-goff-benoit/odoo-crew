# QA de la release — `2026-09-09_01_interdiction-des-durees-negatives-de-loc`

<!-- Une section datée par tâche. La recette complète se joue à la clôture (/odoo-close). -->

## 2026-09-09 — Point 1 : contrainte SQL `days >= 0` sur `lab.rental` (D-31) — mode tâche, QA renforcée

**Série** 19.0 (origine : `__manifest__.py`) · **module** `lab_rental` · **modèle** `lab.rental`
**Flow** `d31-jours-negatifs`, nœud `module_high_gate` (jointure des trois voies QA renforcées)
**Spécification** `revue_fonctionnelle.md` §7, critères §8 · **décision** D-31 (`/work/decisions/2026-09-08.md`)

Ce verdict est une **consolidation** : il ne rejoue aucun contrôle. Les preuves sont celles produites
par les trois voies QA, relues et recoupées avec leurs journaux :

| Voie | Fragment | Verdict de la voie |
|---|---|---|
| `graph-lane-static` | `.odoo-agents/flow-artifacts/d31-jours-negatifs/module_high_static_qa.md` | VERT AVEC RÉSERVE |
| `graph-lane-runtime` | `.odoo-agents/flow-artifacts/d31-jours-negatifs/module_high_runtime_qa.md` | VERT |
| `graph-lane-client-copy` | `.odoo-agents/flow-artifacts/d31-jours-negatifs/module_client_copy_qa.md` | VERT |

### Verdict

**VALIDÉ SOUS RÉSERVE** — la contrainte `lab_rental_check_days_positive` (`CHECK ((days >= 0))`) est
posée et effective, tous les critères d'exécution A1 à A7 sont prouvés par au moins une voie, aucune
anomalie n'est imputable au diff de la tâche ; la réserve porte sur la seule partie d'**A8** qu'aucune
des trois voies ne traverse — la remontée effective du message à l'utilisateur par la couche RPC —,
qui revient à la recette navigateur de la clôture, et sur les limites de preuve listées en §Réserves.

### Résultats d'exécution

| Contrôle | Résultat | Détail / journal |
|---|---|---|
| Lint `labctl lint lab_rental` | **rouge sur dette antérieure, vert sur le diff** | Ruff bloquant *All checks passed!*, Ruff conseils : aucun ; unique erreur `clé obligatoire manquante : author` dans `__manifest__.py`, antérieure au diff → `logs/r2-static/lint.log` |
| Revue statique du diff (forme 19.0) | **vert** | `models.Constraint` (et non `_sql_constraints`), attribut préfixé `_`, message FR non vide, placement conforme à `account_payment.py:199-202` ; aucun `self._cr` ; pas de `from . import tests` |
| Installation base neuve `lab_qa` (`-i`) | **ok** | `RECETTE … install=ok … "0 failed, 0 error(s) of 6 tests" … total=11s` → `logs/r2-runtime/run1-fresh-tags.log` |
| Suite complète du module (point de contrôle) | **6/6 verts** | `RECETTE … "0 failed, 0 error(s) of 6 tests" … total=6s` → `logs/r2-runtime/run2-suite-complete.log` ; le module n'a qu'un fichier de tests, la suite couvre donc tout le module |
| Tests ciblés `/lab_rental:TestLabRentalDaysConstraint` | **6/6 verts** | mêmes journaux, deux runs du 2026-09-09 |
| Mise à niveau `-u` sur la copie `lab_client` | **ok, sans `WARNING odoo.schema`** | `logs/r2-client/01_update.log` |
| Contrainte réellement en base après `-u` | **présente** | `A6 = OK [('lab_rental_check_days_positive', 'CHECK ((days >= 0))')]` → `logs/r2-client/02_a6_after_update.log`, confirmé `09_final_state.log` |
| Scénarios ORM A1-A5 sur `lab_client` | **tous OK** | `A1 = OK … A5 = OK`, `A2_intacte = True` → `logs/r2-client/03_a1_a5.log` |
| Cas des données violantes (A7) | **joué, risque n°1 confirmé** | update « vert » sans contrainte reposée → `logs/r2-client/04_a7_before.log`, `05_a7_update.log`, `06_a7_after.log` |
| État de la copie après QA | **propre** | 0 ligne, 0 ligne violante, contrainte en place, module `installed 19.0.1.0.0` → `logs/r2-client/09_final_state.log` |
| Avertissements | **aucun nouveau** | seules occurrences : `Missing 'author' key in manifest` (dette antérieure) ; `ERROR/CRITICAL : 0` dans les deux runs |
| Captures, guide, communication | **non produits** | interdits en release ouverte (voie normale : `/odoo-close`) |

### Couverture des critères d'acceptation

| Critère | Couvert par | État |
|---|---|---|
| **A1** création `days = -1` refusée | `test_create_negative_days_is_rejected` (runtime, 2 runs) + `03_a1_a5.log` (copie client) | **VERT** |
| **A2** écriture `days = -3` refusée, valeur restée `5` | `test_write_negative_days_is_rejected` + `A2_valeur_sql = 5` / `A2_valeur_orm = 5` | **VERT** |
| **A3** `days = 0` accepté, `amount_total == 0.0` | `test_zero_days_is_accepted` + `03_a1_a5.log` | **VERT** |
| **A4** `days = 4 × 12.5 → 50.0` (non-régression du compute stocké) | `test_positive_days_amount_total` + `03_a1_a5.log` | **VERT** |
| **A5** location valide intacte après rejet, curseur utilisable | `test_valid_rental_survives_rejection` + `A5_curseur_utilisable_count = 3` | **VERT** |
| **A6** contrainte présente dans `pg_constraint` après `-u` | copie client `02_a6_after_update.log` (après `-u`) ; runtime `test_constraint_exists_in_database` (à l'`-i`) | **VERT** — les deux modes de pose sont couverts |
| **A7** comportement sur données violantes, joué explicitement | copie client, étapes 5 à 9 | **VERT** — le critère demandait de jouer et documenter : fait, avec nettoyage et réapplication vérifiée |
| **A8** message configuré non vide, plus aucun `_sql_constraints` | statique (`grep` à zéro occurrence, message `business.py:16`) + `10_a8_message.log` (`message == attendu : True`) | **PARTIEL** — voir réserve R1 : la traversée `_sql_error_to_message` → `service/model.py` n'est jouée par aucune voie |
| **A9** lint sans écart nouveau imputable au diff | statique, `logs/r2-static/lint.log` | **VERT** — voir réserve R2 sur le code retour |

**8 critères verts sur 9, le neuvième partiel.** Aucun critère n'est en échec.

### Anomalies bloquantes

Aucune.

### Anomalies majeures

Aucune imputable au diff.

**Confirmation du risque n°1 de la revue (non-défaut du module, point d'attention de livraison)** — sur
une base portant au moins une ligne `days < 0`, `-u lab_rental` se termine « vert » (module `installed`,
aucune exception, aucun code d'erreur) alors que la contrainte **n'est pas posée** : la séquence
`post_constraint` → report → `finalize_constraints` (`~/odoo-sources/19.0/odoo/orm/registry.py:682-717`)
réduit l'échec à des lignes `odoo.schema`. Prouvé sur `lab_client` (`06_a7_after.log` :
`contrainte reposee malgre la ligne violante = False`, `lignes violantes toujours en base = 1`). C'est le
comportement standard d'Odoo 19.0, anticipé par la revue §7. **Conséquence de livraison** : sur toute
base réellement peuplée, exécuter `SELECT count(*) FROM lab_rental WHERE days < 0;` **avant** la mise à
niveau, corriger ou purger les lignes (arbitrage métier non tranché par D-31 — à faire trancher par
Luc Roy), puis vérifier `pg_constraint` après coup. Ne jamais conclure sur le seul code de sortie.

### Remarques mineures (dette antérieure, hors périmètre)

- `lab_rental/__manifest__.py` — clé `author` absente : seule cause du code retour 1 du lint et des
  3 à 5 `WARNING` des runs. Antérieure au diff (manifest non touché, version toujours `19.0.1.0.0`).
- `lab_rental/__manifest__.py` — le `name` déclaré, « Atelier Boréal — frais de préparation des
  locations », ne correspond ni au module ni à son modèle. Constaté ici, non traité : hors D-31.
- `lab_rental/models/business.py:19` — `kind` dans `@api.depends` sans être utilisé par le compute
  (risque 6 de la revue) : recalculs inutiles, dette antérieure, explicitement hors périmètre.
- `days` reste `NULL`-able en base : `CHECK (days >= 0)` laisse passer `NULL` (risque 5). Décision
  assumée par la revue (H3) ; ne pas ajouter de `NOT NULL` sans nouvelle décision.

### Réserves de la jointure (limites de preuve, sans défaut constaté)

- **R1 — A8, partie RPC/UI** : aucune des trois voies ne traverse `_sql_error_to_message`
  (`odoo/orm/models.py:3270-3284`) puis `service/model.py:207-214`. Le message est prouvé *configuré et
  conforme*, pas *affiché*. À couvrir par la recette navigateur de `/odoo-close`.
- **R2 — lint en code retour 1** : dû exclusivement à la dette `author`. A9 est vert au sens du critère
  (« sans écart nouveau imputable au diff »), mais le contrôle ne repassera au vert franc qu'après
  correction du manifest — à arbitrer à la clôture.
- **R3 — délimitation du diff non mécanique** : l'objet git `9cf40f33b0…` de `.base` est absent de
  l'historique de cette copie (`fatal: bad object`, un seul commit `762d6bd`). La voie statique a
  délimité le diff par recoupement de trois sources (preuve du développeur, revue, lecture du fichier),
  convergentes et sans contradiction, mais non vérifiables par `git diff`.
- **R4 — arbres de travail des voies non conservés** : les contrôles ont été joués dans des espaces
  éphémères (`/tmp/odoo-delegation-20260909/…`) aujourd'hui absents. Le contenu de
  `/work/lab_rental/models/business.py:14-17` correspond au diff déclaré, mais l'identité octet à octet
  entre l'arbre testé et l'arbre livré n'est pas prouvable a posteriori. La recette de clôture, jouée
  sur l'état exact à livrer, lève cette réserve.
- **R5 — divergence entre voies sur l'état de `lab_client`** : la revue avait constaté une copie **sans**
  la contrainte (3 contraintes) ; la voie copie client a trouvé une copie reconstituée la **portant**
  déjà. A7 a donc été joué sur une base où la contrainte a été déposée à la main pour simuler une base
  héritée. Le scénario reste valide et concluant, mais `lab_client` est une copie synthétique vide : elle
  ne prouve rien sur l'historique réel du client (durées négatives tolérées, journal 2026-08-01).
- **R6 — journaux du premier run d'exécution** (`logs/runtime/run2-suite-complete.log`, 0 octet) : run
  interrompu sur une base disparue, **sans valeur de recette**. Seuls `logs/r2-runtime/` font foi.

### Non testé / angles morts

- Écran et parcours utilisateur : aucun (la tâche ne change aucune vue) ; la recette navigateur de la
  clôture doit néanmoins couvrir R1.
- Droits, multi-société, compta, facturation : hors D-31 et hors modèle (`lab.rental` n'a ni `company_id`,
  ni `active`, ni `currency_id`).
- Désinstallation, tours, mise à niveau depuis une version antérieure du module : relèvent de
  `/odoo-close`.
- Comportement sur volumétrie réelle : jamais joué, la copie est vide.

### Appris (pour le journal)

- En 19.0, une contrainte de table posée sur une table contenant des lignes violantes **échoue en
  silence** à l'`-u` : l'update reste vert et la contrainte n'est pas posée. Prouvé, pas déduit
  (`logs/r2-client/06_a7_after.log`). La seule preuve acceptable qu'une règle SQL est appliquée est
  `pg_constraint`, jamais le code retour de l'update.
- Une copie client vide ne valide pas une contrainte : il faut fabriquer le cas violant pour que le
  contrôle ait une valeur.
