# QA de la release — `2026-09-09_01_interdiction-des-durees-negatives-de-loc`

## 2026-09-09 — Point 1 : contrainte SQL `days >= 0` sur `lab.rental` (D-31) — mode tâche, niveau renforcé

**Projet** Éole (`/work`) · **série** 19.0 (origine : `__manifest__.py`) · **module** `lab_rental`
**Flow** `d31-jours-negatifs`, jointure `module_high_gate` · **orchestrateur** `claude-orchestrateur-d31`
**Réception structurée** : `qa_coverage.json` (contrat `cf836fabee21`) et `qa_reception_d31.md` (rendu `5ec57ccd5e46`) — ce rapport généré fait foi pour les critères, leurs statuts et les empreintes des preuves.

### Verdict

**À REPRENDRE** — 8 critères sur 9 couverts, **A8 partiel** : la seule condition non prouvée est que le
message configuré est bien **celui remonté à l'utilisateur**. Aucune des trois voies ne traverse
`_sql_error_to_message` (`odoo/orm/models.py:3270-3284`) puis `odoo/service/model.py:207-214` : un
`TransactionCase` comme `labctl shell` s'exécutent en contexte serveur direct, sans couche RPC/HTTP.
Ce n'est pas un défaut constaté du code — c'est un **contrôle obligatoire manquant**, et le contrat
D-31 ne se satisfait pas d'une preuve statique du message. Rien d'autre ne bloque : la contrainte est
posée, prouvée en base, et le comportement sur données violantes est établi.

### Fragments consolidés (preuves d'entrée, non rejouées ici)

| Voie | Nœud | Verdict de la voie | Preuve |
|---|---|---|---|
| Statique (lint, forme 19.0, diff) | `module_high_static_qa` | VERT AVEC RÉSERVE | `.odoo-agents/flow-artifacts/d31-jours-negatifs/module_high_static_qa.md` |
| Exécution base QA neuve (`lab_qa`) | `module_high_runtime_qa` | VERT | `…/module_high_runtime_qa.md` |
| Copie client (`lab_client`) | `module_client_copy_qa` | VERT (risque n°1 confirmé) | `…/module_client_copy_qa.md` |
| Implémentation | `module_implementation_high_risk` | livré | `…/module_implementation_high_risk.md` |

Aucune commande Odoo n'a été rejouée à la jointure : ni base, ni exécution disponibles dans ce contexte.
La consolidation est une relecture des preuves des trois voies, recoupée avec les journaux cités et
avec le code réel de `/work/lab_rental`.

### Résultats d'exécution retenus

| Contrôle | Résultat | Source |
|---|---|---|
| Lint `labctl lint lab_rental` | Ruff bloquant *All checks passed!*, conseils : aucun ; **code 1** dû à la seule dette `author` manquant au manifest | `logs/r2-static/lint.log` |
| Installation base neuve `lab_qa` + tests ciblés | `install=ok`, **6/6 tests**, 0 erreur | `logs/r2-runtime/run1-fresh-tags.log` |
| Suite complète du module (point de contrôle) | `install=ok`, **6/6 tests**, 0 erreur | `logs/r2-runtime/run2-suite-complete.log` |
| Mise à niveau `-u` sur copie `lab_client` | sans erreur, **contrainte présente** en base ensuite | `logs/r2-client/01_update.log`, `02_a6_after_update.log` |
| Scénarios A1-A5 sur copie client | tous OK, valeur intacte, curseur utilisable | `logs/r2-client/03_a1_a5.log` |
| Données violantes (A7) | update « vert » **sans contrainte posée** ; après nettoyage, contrainte reposée | `logs/r2-client/04→09` |
| Message remonté en RPC/UI | **non joué** | — |

### Couverture des critères d'acceptation

| Critère | Couvert par | État |
|---|---|---|
| A1 création `days=-1` refusée | `03_a1_a5.log` + 2 runs `lab_qa` | **couvert** |
| A2 écriture refusée, valeur restée 5 | `03_a1_a5.log` (ORM + SQL direct) + tests | **couvert** |
| A3 `days=0` accepté, total 0 | `03_a1_a5.log` + tests | **couvert** |
| A4 `4 × 12.5 = 50.0` | `03_a1_a5.log` + tests | **couvert** |
| A5 location valide intacte, curseur utilisable | `03_a1_a5.log` + tests | **couvert** |
| A6 contrainte en base après `-u` | `02_a6_after_update.log`, `09_final_state.log` | **couvert** |
| A7 comportement sur données violantes | `04` → `09` (scénario complet, nettoyé) | **couvert** |
| A8 message non vide **et** remonté à l'utilisateur ; plus de `_sql_constraints` | `10_a8_message.log`, voie statique | **partiel** — chemin RPC/UI non traversé |
| A9 lint sans écart nouveau | `logs/r2-static/lint.log` | **couvert** |

### Anomalies

Aucune anomalie bloquante ni majeure imputable au diff de la tâche. Le code livré
(`lab_rental/models/business.py:14-17`, `tests/test_days_constraint.py`) est conforme à la
spécification §7 et à la forme 19.0 (`models.Constraint`, attribut préfixé `_`, aucun `_sql_constraints`
ni `@api.constrains`).

**Manque à combler pour lever le « À REPRENDRE »** :
- **M1 — A8, partie utilisateur.** Prouver que « Le nombre de jours d'une location ne peut pas être
  négatif. » est bien le message reçu côté client. Voie la plus courte : un test de niveau RPC dans le
  module (`HttpCase` + `call_kw` sur `lab.rental.create`) attendant une `ValidationError` porteuse de ce
  message ; il traverse `service/model.py` que `TransactionCase` ne traverse pas. À défaut, un contrôle
  navigateur — mais c'est alors la clôture (`/odoo-close`) qui le porte, et le critère reste ouvert
  jusque-là. Retour à l'étape 2 (`odoo-developer`) pour ce seul ajout : le code métier n'est pas en cause.

### Réserves (n'empêchent pas la reprise, à porter à la clôture)

1. **Risque n°1 confirmé, et il ne disparaît pas.** Sur une base portant au moins une ligne `days < 0`,
   un `-u` se termine « vert » **sans poser la contrainte** (`06_a7_after.log` : `contrainte reposee
   malgre la ligne violante = False`, ligne violante toujours présente, module `installed`). Toute mise
   à niveau réelle exige donc, dans l'ordre : compter les lignes violantes, les arbitrer avec Luc Roy
   (mise à 0 ou suppression — **non tranché par D-31**), mettre à jour, puis **vérifier `pg_constraint`**.
   À reprendre telle quelle dans la communication de clôture.
2. **Dette antérieure** : `author` absent de `__manifest__.py` — fait sortir le lint en code 1 et produit
   3 à 5 avertissements à chaque chargement. Hors périmètre D-31, à traiter à la clôture.
3. **Délimitation du diff non mécanique** : `git diff` contre le sha de `.base` échoue (objet absent de
   cette copie). La voie statique a délimité le diff par recoupement de trois sources documentaires.
   Recoupé une fois de plus ici avec le fichier réel : `business.py` ne contient que le bloc annoncé.
   La réserve reste : aucune preuve mécanique que rien d'autre n'a bougé depuis l'ouverture de la release.
4. **Preuves issues d'environnements successifs** : la revue fonctionnelle décrivait une `lab_client`
   *sans* la contrainte, la voie copie client a travaillé sur une copie reconstituée qui la portait déjà ;
   les répertoires d'exécution diffèrent d'un fragment à l'autre (`N04-claude-delegated`,
   `N04-claude-resumed`) et ces arborescences n'existent plus. Les conclusions restent valides — chaque
   voie a rejoué ses contrôles sur l'état qu'elle a constaté — mais aucune preuve ne rattache
   mécaniquement le module testé sous `/tmp/.../addons/lab_rental` au contenu actuel de `/work/lab_rental`.
5. **Inexactitude relevée dans un fragment, non corrigée** (les fragments ne se modifient pas) :
   `module_high_runtime_qa.md` annonce que les deux journaux du run précédent (`logs/runtime/`) font
   0 octet ; `run1-fresh-tags.log` fait en réalité 27 125 octets et contient un run vert (6/6, 14 s).
   Seul `run2-suite-complete.log` est vide. Sans conséquence : les runs retenus sont ceux de `r2-runtime`.
6. **Non traité, assumé** : `NULL` sur `days` échappe au `CHECK` (revue §4 risque 5) ; `kind` superflu
   dans `@api.depends` (risque 6, dette antérieure).

### Appris (pour le journal)

- Trois voies QA « vertes » ne font pas un critère couvert : A8 était composé, et sa seconde condition
  n'appartenait à aucune des trois voies. La jointure est le seul endroit où ce trou devient visible.
- En 19.0, un `-u` sur une table contenant des lignes violantes **réussit sans poser la contrainte**
  (`odoo/orm/registry.py:682-717`) : preuve reproduite en laboratoire. Vérifier `pg_constraint` après
  toute mise à niveau qui ajoute une contrainte de table est désormais un réflexe à écrire dans la recette.
