# QA — release `2026-09-09_01_interdiction-des-durees-negatives-de-loc`

## 2026-09-09 — Point n°1 : contrainte SQL `days >= 0` sur `lab.rental` (D-31) — mode tâche, niveau **renforcé**

**Série** 19.0 (origine : `__manifest__.py`) · **module** `lab_rental` · **flow** `d31-jours-negatifs`,
nœud de jointure `module_high_gate` · **décision** D-31 (`decisions/2026-09-08.md`)

Ce verdict est la **consolidation** des trois fragments QA produits en parallèle. Il n'ajoute aucune
exécution : toutes les preuves citées ont été jouées par les voies, le 2026-09-09, et sont relues ici.

| Voie | Fragment | Verdict de la voie |
|---|---|---|
| `graph-lane-static` | `.odoo-agents/flow-artifacts/d31-jours-negatifs/module_high_static_qa.md` | VERT AVEC RÉSERVE |
| `graph-lane-runtime` | `.odoo-agents/flow-artifacts/d31-jours-negatifs/module_high_runtime_qa.md` | VERT |
| `graph-lane-client-copy` | `.odoo-agents/flow-artifacts/d31-jours-negatifs/module_client_copy_qa.md` | VERT (risque n°1 confirmé) |

### Verdict

**VALIDÉ SOUS RÉSERVE** — le code est conforme à la spécification et à la série 19.0, huit critères
d'acceptation sur neuf sont prouvés, aucune anomalie bloquante n'a été trouvée. **A8 reste partiel** :
la moitié « le message est bien celui remonté à l'utilisateur » n'est établie par aucune voie, et ne
peut pas l'être dans le contexte actuel. Un critère d'acceptation non entièrement satisfait interdit
« VALIDÉ » : la jointure sort donc en **`blocked`**, en attente d'un arbitrage humain (§ À décider).

### Recoupement des trois fragments

Chaque affirmation des fragments a été confrontée à son journal :

| Contrôle | Résultat | Preuve relue |
|---|---|---|
| Lint (voie statique) | Ruff bloquant *All checks passed!*, conseils : aucun ; 1 erreur : `author` absent du manifeste | `logs/r2-static/lint.log` |
| Install + tests ciblés, base neuve `lab_qa` | `install=ok`, `0 failed, 0 error(s) of 6 tests`, 11 s | `logs/r2-runtime/run1-fresh-tags.log` |
| Suite complète du module, base `lab_qa` | `install=ok`, `0 failed, 0 error(s) of 6 tests`, 6 s ; mêmes 6 méthodes que le run ciblé (vérifié, la suite du module se réduit à cette classe) | `logs/r2-runtime/run2-suite-complete.log` |
| Mise à niveau explicite `lab_client` | terminée sans erreur ni `WARNING odoo.schema` | `logs/r2-client/01_update.log` |
| Contrainte en base après `-u` | `lab_rental_check_days_positive` / `CHECK ((days >= 0))` | `logs/r2-client/02_a6_after_update.log`, `09_final_state.log` |
| A1–A5 rejoués en ORM sur `lab_client` | tous `OK`, valeurs relues en SQL direct | `logs/r2-client/03_a1_a5.log` |
| Données violantes préexistantes (A7) | update « vert » **sans** contrainte reposée, ligne violante conservée | `logs/r2-client/04–06` |
| Nettoyage et réapplication | contrainte reposée, 0 ligne, base laissée propre | `logs/r2-client/07–09` |
| Message configuré et absence de `_sql_constraints` | message conforme, grep vide | `logs/r2-client/10_a8_message.log` |

Aucune contradiction entre les trois voies. Les deux points où elles se répondent :

- **A6** — la voie exécution ne prouvait la contrainte qu'à l'**installation** sur base neuve et le disait ;
  c'est la voie copie client qui satisfait le critère au sens strict (« après `-u` »).
- **État initial de `lab_client`** — la voie copie client constate une base **neuve, vide, portant déjà la
  contrainte**, différent de ce que la revue fonctionnelle avait relevé sur l'ancienne copie (§5). Les deux
  constats sont exacts à leur date ; la copie a été reconstituée entre-temps. Sans conséquence sur le
  verdict : A7 a été joué en fabriquant explicitement le cas violant, ce que la revue exigeait précisément
  parce que la copie ne prouve rien par elle-même.

### Anomalies bloquantes

Aucune.

### Anomalies majeures

Aucune imputable au diff de la tâche.

### Remarques mineures et dette antérieure

1. **`__manifest__.py` — clé `author` absente.** Fait sortir le lint en échec. Dette antérieure : le
   manifeste n'a pas été touché (version `19.0.1.0.0` inchangée, absent des fichiers modifiés déclarés par
   le développeur), donc hors périmètre D-31. À corriger à la clôture, où la version du manifeste bouge de
   toute façon.
2. **`kind` dans `@api.depends` de `_compute_amount_total`** (`lab_rental/models/business.py:19`) — dépendance
   inutile, recalculs superflus. Risque 6 de la revue, hors périmètre, non traité.
3. **`days` reste `NULL`-able en base** — `CHECK (days >= 0)` laisse passer `NULL`. Hypothèse H3 de la revue,
   assumée : ajouter `NOT NULL` sortirait de D-31 et créerait un second risque de données.

### Réserves de méthode (à ne pas perdre)

- **Aucun `git diff` mécanique n'a pu délimiter le diff de la tâche** : le sha de `.base`
  (`9cf40f33b0e2d52d86f90d1c328e4d6f09de23de`) n'existe pas dans le dépôt de cette copie, qui a été
  initialisée à l'état « déjà développé ». La délimitation repose sur le recoupement de trois sources
  documentaires (preuve du développeur, revue, lecture du fichier), toutes concordantes — mais c'est une
  garantie documentaire, pas mécanique. L'imputation de la dette `author` en dépend.
- Le lint a été joué par le pont sur la copie montée du module
  (`/tmp/odoo-delegation-.../backend/addons/lab_rental`), pas sur `/work/lab_rental` directement.

### Couverture des critères d'acceptation

Réception structurée : `qa_coverage.json` (contrat `cf836fabee21`, 9 critères, preuves empreintées).

| Critère | Couvert par | État |
|---|---|---|
| A1 création `days = -1` refusée | runtime (2 runs) + copie client | **covered** |
| A2 écriture `days = -3` refusée, valeur restée 5 | runtime + copie client (relecture SQL + ORM) | **covered** |
| A3 `days = 0` accepté, total 0 | runtime + copie client | **covered** |
| A4 `4 × 12.5 = 50.0` | runtime + copie client | **covered** |
| A5 location valide survit au rejet, curseur utilisable | runtime + copie client | **covered** |
| A6 contrainte présente après `-u` | copie client (`02`, `09`) | **covered** |
| A7 comportement sur données violantes | copie client (`04`→`09`) | **covered — risque confirmé** |
| A8 message remonté à l'utilisateur + zéro `_sql_constraints` | statique (grep) + copie client (message configuré) | **partial** |
| A9 lint sans écart nouveau imputable au diff | statique | **covered** |

**Pourquoi A8 n'est que partiel.** Le critère est composé. Sa seconde condition est prouvée (aucune
occurrence de `_sql_constraints` ni `@api.constrains`). Sa première ne l'est qu'à moitié : le message
configuré sur l'objet `models.Constraint` est non vide et conforme au texte attendu, mais rien ne prouve
qu'il **arrive à l'utilisateur**. La traduction de `CheckViolation` en `ValidationError` a lieu dans
`odoo/service/model.py:207-214`, que ni un `TransactionCase` ni `labctl shell` ne traversent. Les trois
voies le déclarent elles-mêmes non joué ; je ne le requalifie pas en vert.

### À décider (humain)

**Comment satisfaire la partie « remontée à l'utilisateur » d'A8 ?** Deux voies, l'arbitrage n'est pas le mien :

1. **La reporter à la clôture** — le nœud `browser_qa` de `/odoo-close` rejoue les critères utilisateur en
   navigateur sur la copie client et verrait le message réel. C'est le lieu naturel de ce contrôle, et la
   revue elle-même range le message dans « Ce que l'utilisateur verra » (§10). A8 resterait `partial` au
   niveau de la tâche, assumé comme tel.
2. **Le prouver maintenant** — ajouter un `HttpCase` (ou un appel RPC) au module, ce qui rouvre
   l'implémentation et exige une exécution Odoo. Aucune base ni exécution n'est disponible dans ce contexte :
   cette voie suppose un environnement rendu à nouveau disponible.

**Point d'attention impératif pour la livraison** (ne relève pas d'une décision, mais ne doit pas se perdre) :
A7 a **prouvé** qu'un `-u` sur une base contenant une ligne `days < 0` se termine en succès apparent
**sans poser la contrainte** (comportement standard, `odoo/orm/registry.py:682-717`). La procédure de reprise
de la revue (§7), précisée par la voie copie client, est **obligatoire** avant toute mise à niveau chez le
client : compter les lignes violantes, les arbitrer avec Luc Roy (mise à 0 ou suppression — non tranché par
D-31), puis mettre à niveau et **vérifier `pg_constraint`**. Le seul code de sortie de l'update ne prouve rien.

### Non testé / angles morts

- Passage réel par la couche RPC/HTTP (partie utilisateur d'A8) — voir ci-dessus.
- Comportement sur une base réellement peuplée de l'historique client : `lab_client` est une copie
  synthétique de laboratoire, vide, pas la sauvegarde du client.
- Recette complète (base neuve intégrale, désinstallation, tours, captures) : elle appartient à la clôture,
  pas à la QA de tâche.
- Droits, comptabilité, facturation : hors périmètre de D-31, non touchés par le diff.

### Appris (pour le journal)

- Une contrainte SQL ajoutée sur une table déjà peuplée de lignes violantes **échoue silencieusement** en
  `-u` : le module reste `installed`, l'update sort sans erreur, la contrainte n'est pas posée. Vérifier
  `pg_constraint` est le seul contrôle qui vaille. Prouvé ici, pas supposé.
- Un critère d'acceptation qui mêle « configuré » et « remonté à l'utilisateur » ne peut pas être clos par
  un `TransactionCase` : soit il porte un `HttpCase`, soit il est explicitement renvoyé à la recette
  navigateur dès la rédaction de la revue.
