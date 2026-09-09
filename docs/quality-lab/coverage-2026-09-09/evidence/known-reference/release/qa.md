# QA de la release — interdiction des durées négatives de location

<!-- Une section datée par tâche. Verdict unique de l'orchestrateur, fusion des
     fragments de voies. Le détail des exécutions reste dans les fragments cités. -->

## 2026-09-09 — Point 1 · Contrainte SQL `days >= 0` sur `lab.rental` (D-31) — mode tâche, **risque renforcé**

**Série** 19.0 (origine : `__manifest__.py`) · **module** `lab_rental` · **modèle** `lab.rental`
**Flow** `d31-jours-negatifs`, nœud `module_high_gate` (jointure des trois voies QA renforcées)
**Spécification** `revue_fonctionnelle.md` §7-§8 · **décision** `/work/decisions/2026-09-08.md` (D-31, Luc Roy)

### Verdict

**VALIDÉ SOUS RÉSERVE** — les neuf critères d'acceptation sont couverts par au moins une preuve
d'exécution ou de lecture ; aucune anomalie imputable au diff de la tâche. Les réserves ne portent
pas sur le code livré mais sur trois points qui restent ouverts : la remontée du message à
l'utilisateur en RPC/UI (partie non statique d'A8, qui appartient à la recette navigateur de
clôture), le risque n°1 confirmé et non corrigible dans le module (un `-u` sur une base portant une
ligne `days < 0` réussit en apparence sans poser la contrainte), et la traçabilité du diff, faute
d'objet git de base dans cette copie.

Aucune reprise n'est demandée : aucun critère n'est en échec, aucune régression n'a été introduite,
et aucun contrôle obligatoire de la QA de tâche renforcée n'a été omis.

### Origine des preuves

Cette section **fusionne** trois fragments produits par les voies QA ; elle ne rejoue rien. Aucune
base ni exécution Odoo n'était disponible au moment de la jointure : les contrôles cités ont été
exécutés par les voies, leurs journaux sont relus, pas reproduits.

| Voie | Fragment | Verdict de la voie |
|---|---|---|
| `graph-lane-static` | `.odoo-agents/flow-artifacts/d31-jours-negatifs/module_high_static_qa.md` | VERT AVEC RÉSERVE |
| `graph-lane-runtime` | `.odoo-agents/flow-artifacts/d31-jours-negatifs/module_high_runtime_qa.md` | VERT |
| `graph-lane-client-copy` | `.odoo-agents/flow-artifacts/d31-jours-negatifs/module_client_copy_qa.md` | VERT |
| (amont) implémentation | `.odoo-agents/flow-artifacts/d31-jours-negatifs/module_implementation_high_risk.md` | — |

### Résultats d'exécution (relevés dans les fragments et leurs journaux)

| Contrôle | Résultat | Détail |
|---|---|---|
| Lint `labctl lint lab_rental` | **échec sur dette antérieure uniquement** | Ruff bloquant *All checks passed!*, conseils : aucun ; seule erreur `clé obligatoire manquante : author` dans `__manifest__.py`, antérieure au diff (`logs/r2-static/lint.log`) |
| Installation base neuve `lab_qa` | **ok** | `RECETTE … install=ok … 0 failed, 0 error(s) of 6 tests` (`logs/r2-runtime/run1-fresh-tags.log`) |
| Suite complète du module, base chaude | **ok, 6/6** | `RECETTE … install=ok … of 6 tests … total=6s` (`logs/r2-runtime/run2-suite-complete.log`) — le module n'a qu'une classe de test, la suite recouvre les tests ciblés |
| Mise à jour `-u` sur copie client `lab_client` | **ok** | `logs/r2-client/01_update.log` puis `08_reapply_update.log`, sans `WARNING odoo.schema` |
| Contrainte réellement posée (`pg_constraint`) | **ok** | `lab_rental_check_days_positive` / `CHECK ((days >= 0))` (`02_a6_after_update.log`, `09_final_state.log`) |
| Comportement sur donnée violante | **risque n°1 confirmé** | contrainte déposée + `INSERT` direct `days = -3` → `-u` sans exception, contrainte **non reposée**, ligne violante conservée (`04/05/06_a7_*.log`) |
| Tests | **6/6 verts**, 0 skip | deux runs indépendants sur `lab_qa`, plus rejeu ORM des mêmes scénarios sur `lab_client` |
| Désinstallation / tours / captures | **non joués** | hors QA de tâche : appartiennent à la recette de clôture |
| État laissé sur `lab_client` | **propre** | module installé `19.0.1.0.0`, contrainte présente, 0 ligne, aucune donnée de test résiduelle (`09_final_state.log`) |

### Anomalies bloquantes

Aucune.

### Anomalies majeures

Aucune imputable au diff de la tâche.

### Remarques mineures et dette antérieure

- **D1 — `lab_rental/__manifest__.py` : clé `author` absente.** Dette antérieure, constatée
  identique avant et après le diff (voie statique, §« Anomalies localisées ») ; elle fait sortir le
  lint en code 1 et produit les avertissements `Missing 'author' key in manifest` des runs. Hors
  périmètre D-31 (« le manifest ne bouge pas ») ; à traiter à la clôture, quand la version du
  manifest sera de toute façon incrémentée.
- **D2 — `lab_rental/models/business.py:19` : `kind` dans `@api.depends` de `_compute_amount_total`
  sans être utilisé.** Dette antérieure signalée par la revue (risque 6), volontairement non
  touchée.
- **D3 — `days` reste `NULL`-able en base.** `CHECK (days >= 0)` laisse passer `NULL` ; décision
  assumée par la revue (risque 5), hors D-31. Consignée, non traitée.

### Couverture des critères d'acceptation

| Critère | Couvert par | État |
|---|---|---|
| **A1** création `days = -1` refusée | `test_create_negative_days_is_rejected` (runtime, 2 runs) + rejeu ORM sur `lab_client` (`03_a1_a5.log` : `A1 = OK`) | **VERT** |
| **A2** écriture `days = -3` refusée, valeur restée `5` | même test (runtime) + `lab_client` : `A2_valeur_sql = 5`, `A2_valeur_orm = 5`, `A2_intacte = True` | **VERT** |
| **A3** `days = 0` accepté, `amount_total == 0.0` | `test_zero_days_is_accepted` + `A3 = OK` sur `lab_client` | **VERT** |
| **A4** `days = 4 × 12.5 → 50.0` (non-régression du compute stocké) | `test_positive_days_amount_total` + `A4 = OK` | **VERT** |
| **A5** location valide intacte après rejet, curseur utilisable | `test_valid_rental_survives_rejection` + `A5 = OK`, `A5_curseur_utilisable_count = 3` | **VERT** |
| **A6** contrainte présente après `-u` sur base existante | `lab_client` : `02_a6_after_update.log` (`A6 = OK`) et surtout `08/09` — base sans contrainte après le scénario A7, `-u` rejoué, contrainte **reposée** avec `CHECK ((days >= 0))`. Le vert de la voie runtime ne vaut que pour `-i` sur base neuve et n'est pas retenu comme preuve d'A6. | **VERT** |
| **A7** comportement sur données violantes | `lab_client`, séquence complète `04 → 05 → 06` : `-u` terminé sans exception (`Modules loaded.`), `contrainte reposee malgre la ligne violante = False`, `lignes violantes toujours en base = 1`, puis nettoyage et réapplication vérifiée | **VERT — risque n°1 confirmé et documenté** |
| **A8** message configuré non vide, plus aucun `_sql_constraints` | Statique : message `business.py:16` non vide, `grep _sql_constraints\|api.constrains` → aucune occurrence ; `lab_client` : `message == attendu = True`. **Partie non couverte** : que ce message traverse `_sql_error_to_message` puis `service/model.py` jusqu'à un `ValidationError` RPC/UI — aucune voie ne passe par la couche de service. | **PARTIEL** — réserve R1 |
| **A9** lint sans écart nouveau imputable au diff | Voie statique : Ruff bloquant et conseils à zéro ; seule erreur = D1, antérieure | **VERT** |

Périmètre tenu, vérifié par la voie statique : aucune vue (`find -name "*.xml"` sans résultat),
`security/ir.model.access.csv` inchangé, `daily_rate` et `_compute_amount_total` inchangés,
`version = '19.0.1.0.0'` inchangée — conforme à la revue §7 et à la demande (« aucun écran ni droit
à modifier »).

### Réserves

- **R1 — A8 côté utilisateur non prouvé.** Un `TransactionCase` et `labctl shell` s'exécutent hors
  couche RPC : la conversion de `CheckViolation` en `ValidationError` porteuse du message français
  n'est traversée par aucune preuve. À couvrir par la recette navigateur de `/odoo-close`
  (saisie d'un nombre de jours négatif à l'écran, message attendu : « Le nombre de jours d'une
  location ne peut pas être négatif. »). Ce n'est pas un défaut du code : la revue elle-même situait
  ce contrôle à l'écran.
- **R2 — mode d'échec silencieux à la mise à niveau (risque n°1, désormais prouvé).** Sur une base
  portant au moins une ligne `days < 0`, `-u` se termine « vert » sans poser la contrainte
  (`odoo/orm/registry.py:682-717`). D-31 ne serait alors **pas** appliquée sans que rien ne le
  signale. La procédure de reprise de la revue §7 devient obligatoire et doit figurer dans les
  livrables de clôture : compter les lignes violantes **avant** l'update, les arbitrer (mise à 0 ou
  suppression — **non tranché par D-31, à remonter à Luc Roy**), puis vérifier `pg_constraint`
  après coup. Ne jamais conclure sur le seul code de sortie de l'update.
- **R3 — délimitation du diff non mécanique.** `git diff` contre le `.base`
  (`9cf40f33b0e2d52d86f90d1c328e4d6f09de23de`) échoue (`fatal: bad object`) : cette copie ne
  contient qu'un commit initial portant déjà l'état développé. La voie statique a délimité le diff
  par recoupement de trois sources documentaires (preuve du développeur, revue, lecture du fichier)
  et non par un diff vérifiable. La classification « dette antérieure » de D1 repose sur cette
  méthode de substitution ; elle est cohérente mais non prouvée mécaniquement.
- **R4 — traçabilité des chemins de contrôle.** Le lint et les runs ont été joués via le pont, sur
  des copies du module (`/tmp/odoo-delegation-20260909/N04-…/backend/addons/lab_rental`), sans
  empreinte reliant ces copies à `/work/lab_rental`. La lecture du fichier réel à la jointure
  confirme que `business.py:14-17` porte bien le bloc contrôlé, mais aucune preuve d'empreinte
  (`odoo_evidence.py`) n'a été produite.
- **R5 — écart documentaire dans le fragment runtime.** Il déclare les journaux du run précédent
  (`logs/runtime/run1-fresh-tags.log`, `run2-suite-complete.log`) « 0 octet » ; en réalité seul
  `run2` est vide, `run1` fait 27 Ko et contient une ligne `RECETTE` complète 6/6. Sans effet sur le
  verdict — les runs retenus sont ceux de `logs/r2-runtime/`, relancés le 2026-09-09 — mais l'écart
  est consigné pour ne pas laisser une preuve mal décrite dans le dossier.
- **R6 — représentativité de la copie.** `lab_client` est une copie synthétique de laboratoire, vide
  au départ et portant déjà la contrainte à l'état initial. Elle ne représente ni les volumes ni
  l'historique décrit au journal du projet (durées négatives tolérées avant D-31). Le scénario A7 a
  dû **fabriquer** le cas violant ; le comportement sur une base client réellement peuplée reste à
  vérifier au moment de la mise à niveau réelle.

### Non testé / angles morts

- Recette de clôture : base neuve intégrale, désinstallation, tours navigateur, captures — non
  jouées, conformément au principe « tâche légère, release lourde ».
- Chemin RPC/HTTP et écran (R1).
- Reprise de données sur une base réellement peuplée (R2, R6) ; l'arbitrage métier n'est pas tranché.
- Droits, comptabilité, facturation : hors D-31, aucun contrôle mené, aucun fichier de sécurité
  touché.
- `NULL` sur `days` (D3) : aucune preuve, aucune règle demandée.

### Appris (pour le journal, à écrire au nœud `journal_task`)

- Sur une table déjà peuplée de lignes violantes, une contrainte 19.0 `models.Constraint` **n'est pas
  posée** et l'`-u` se termine sans erreur : le seul contrôle qui le détecte est une lecture de
  `pg_constraint`. Prouvé ici sur `lab_client` (`06_a7_after.log`), pas seulement déduit des sources.
- Une base de QA neuve ne prouve jamais la pose d'une contrainte à la mise à niveau : `-i` et `-u`
  ne passent pas par le même chemin.
- Le `.base` d'une release ne vaut que si l'objet git existe dans la copie de travail ; sinon la QA
  statique perd sa délimitation mécanique du diff.
