# Preuve — `module_high_runtime_qa` (flow `d31-jours-negatifs`, voie `graph-lane-runtime`)

Rôle `odoo-tester` · mode tâche · voie exécution runtime seule · projet `/work` (Éole) · série 19.0
Module `lab_rental` · release `changelog/2026-09-09_01_interdiction-des-durees-negatives-de-loc` · décision D-31.

**Reprise après interruption** : les journaux `logs/runtime/run1-fresh-tags.log` et
`run2-suite-complete.log` (0 octet) du run précédent portent sur une base disparue et **ne valent
pas recette**. Toutes les commandes de ce fragment ont été relancées aujourd'hui (2026-09-09) sur
`lab_qa`, base neuve et vide reconstituée avec l'environnement.

## Verdict de la voie

**VERT** — sur le périmètre strict de cette voie (installation + tests ciblés + suite complète sur
base QA neuve). Aucun échec, aucun avertissement imputable au diff. Voir « Ce que ma voie ne prouve
pas » pour ce qui reste hors périmètre (A6 sur `-u`, A7, message RPC).

## Commandes exécutées

| # | Commande | Code retour | Durée mesurée | Journal |
|---|---|---|---|---|
| 1 | `/bridge/labctl qa lab_rental --quick --fresh --tags /lab_rental:TestLabRentalDaysConstraint` | 0 | 11 s (mesuré) | `.odoo-agents/flow-artifacts/d31-jours-negatifs/logs/r2-runtime/run1-fresh-tags.log` |
| 2 | `/bridge/labctl qa lab_rental` (suite complète du module, sans `--tags`) | 0 | 6 s (mesuré) | `.odoo-agents/flow-artifacts/d31-jours-negatifs/logs/r2-runtime/run2-suite-complete.log` |

Point de contrôle déclenché volontairement pour la commande 2 : la contrainte touche `lab.rental`,
modèle dont dépend le calcul de `amount_total` (compute stocké) — c'est le cas prévu par la consigne
de mode tâche. Le module `lab_rental` ne contient qu'un seul fichier de tests
(`tests/test_days_constraint.py`, classe `TestLabRentalDaysConstraint`, 6 méthodes) : la suite
complète exécute donc les 6 mêmes tests que la commande ciblée — vérifié en comparant les deux
journaux (mêmes 6 `Starting TestLabRentalDaysConstraint.*` dans les deux runs), ce n'est pas une
redite creuse mais la couverture réelle et totale du module à ce jour.

## Lignes RECETTE

```
RECETTE module=lab_rental db=lab_qa install=ok update=n.a. uninstall=n.a. tests="0 failed, 0 error(s) of 6 tests" errors=0 failed=0 skipped=0 warnings=3 total=11s base=0s quick=11s
```

```
RECETTE module=lab_rental db=lab_qa install=ok update=n.a. uninstall=n.a. tests="0 failed, 0 error(s) of 6 tests" errors=0 failed=0 skipped=0 warnings=5 total=6s install=2s tests=4s
```

`update=n.a.` dans les deux cas : `--fresh` et l'exécution normale de `labctl qa` sur base neuve
installent (`-i`), n'exécutent aucun `-u`. Cette voie ne joue donc **aucune mise à jour sur base
peuplée** — voir plus bas.

## Tableau des critères couverts par ma voie

| Critère | Test | État | Détail |
|---|---|---|---|
| A1 | `test_create_negative_days_is_rejected` | **prouvé** | vert dans les deux runs (installation neuve) |
| A2 | `test_write_negative_days_is_rejected` | **prouvé** | vert dans les deux runs |
| A3 | `test_zero_days_is_accepted` | **prouvé** | vert dans les deux runs |
| A4 | `test_positive_days_amount_total` | **prouvé** | vert dans les deux runs |
| A5 | `test_valid_rental_survives_rejection` | **prouvé** | vert dans les deux runs |
| A6 | `test_constraint_exists_in_database` | **prouvé à l'installation sur base neuve seulement** | le test interroge `pg_constraint` et passe au vert lors d'un `-i` sur `lab_qa`. Ma voie **ne prouve pas** la pose lors d'un `-u` sur une base déjà peuplée : ce cas relève de la voie copie client (`lab_client`), que je n'ai pas touchée (hors périmètre explicite de ma consigne). Ne pas lire ce vert comme couvrant le risque n°1 de la revue fonctionnelle. |
| A7 | — | **non joué par ma voie** | fabrication d'une ligne violante par `INSERT` SQL direct avant un `-u` : hors périmètre (base QA vide, pas de scénario de reprise à jouer ici) ; relève de la voie copie client |
| A8 | — | **partiellement prouvé** | le message non vide et l'absence de `_sql_constraints`/`api.constrains` sont vérifiés côté code par la voie statique, pas par la mienne ; ma voie confirme seulement que l'erreur levée en `TransactionCase` porte le message attendu (implicite dans A1/A2, pas testé explicitement pour son contenu). La remontée du message en RPC/UI n'est traversée par aucun `TransactionCase` — non prouvée par ma voie |
| A9 | — | **hors voie** | lint appartient à la voie statique, non relancé ici |

## Avertissements liés au module

Les deux runs signalent uniquement `Missing 'author' key in manifest for 'lab_rental', defaulting to ''`
(3 occurrences run 1, 5 occurrences run 2, toutes identiques). C'est une **dette antérieure** au
diff de la tâche : le manifeste n'a pas été touché par le développeur (confirmé par sa preuve,
`module_implementation_high_risk.md` §1 et §3), et cette même clé manquante est déjà signalée dans le
lint de la voie statique du run précédent. Aucun avertissement nouveau imputable au diff n'a été
observé dans mes deux runs. `ERROR/CRITICAL : 0` dans les deux journaux.

## Anomalies localisées

Aucune. Les 6 tests passent dans les deux runs, aucune erreur, aucun avertissement nouveau.

## Ce que ma voie ne prouve pas

1. **A6 sur mise à jour d'une base peuplée (`-u` sur `lab_client`)** — mes deux runs installent sur
   base neuve (`lab_qa` vidée par `--fresh`, ou base par défaut du pont sans module préexistant).
   Le mode d'échec identifié par la revue fonctionnelle (risque n°1 : une contrainte SQL posée sur une
   table déjà violante échoue silencieusement en `-u`, l'update se termine « vert » sans la
   contrainte) n'est traversé par aucune de mes commandes. C'est explicitement le rôle de la voie
   copie client, que je n'ai pas exécutée (consigne : ne pas toucher `lab_client`).
2. **A7 (comportement sur données violantes préexistantes)** — non joué par ma voie ; nécessite un
   `INSERT` SQL direct contournant l'ORM sur une base peuplée avant un `-u`, hors périmètre `qa_db_module`
   attribué ici.
3. **Message d'erreur remonté à l'utilisateur en RPC/UI** (partie non-`TransactionCase` d'A8) — un
   `TransactionCase` ne traverse pas `odoo/service/model.py`, donc la traduction en `ValidationError`
   côté RPC n'est vue par aucun de mes tests.
4. **A9 (lint)** — appartient à la voie statique, non rejoué ici.
5. **Contrôle statique du diff** (manifest, sécurité, style) — hors périmètre, voie statique.
6. Aucune preuve sur une base autre que `lab_qa` : je n'ai lancé aucune commande sur `lab_client`, ni
   `/bridge/labctl update`, ni `/bridge/labctl shell`, conformément à la consigne.
