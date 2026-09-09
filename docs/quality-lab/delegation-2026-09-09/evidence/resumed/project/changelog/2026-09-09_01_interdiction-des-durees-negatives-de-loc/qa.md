# QA — release 2026-09-09_01

<!-- Une section datée par tâche. Verdict unique de l'orchestrateur, fusion des
     fragments de voie ; les preuves détaillées vivent dans .odoo-agents/flow-artifacts/. -->

## 2026-09-09 — Point n°1 · Contrainte SQL `days >= 0` sur `lab.rental` (D-31)

**Verdict : VERT AVEC RÉSERVE** — les neuf critères d'acceptation A1→A9 sont satisfaits.
La réserve ne porte pas sur le code livré : elle porte sur une dette antérieure de lint et sur
une limite de la copie de laboratoire (voir « Réserves »).

Module `lab_rental` · série **19.0** · mode **tâche** (QA renforcée, trois voies).
Décision de référence : **D-31** (`decisions/2026-09-08.md`, Luc Roy).
Spécification et critères : `revue_fonctionnelle.md` §7-§8.

### Reprise après interruption

L'exécution précédente de la chaîne a été interrompue par sa limite de durée **pendant les voies
QA** : revue fonctionnelle et développement avaient rendu leurs fragments, les trois voies QA n'en
avaient rendu aucun. Leurs trois revendications abandonnées ont été libérées avec motif, puis
réattribuées (`odoo_flow.py release/claim`, propriétaires `-r2`). La revue et le code ont été
**repris tels quels** : leurs preuves — vérification de forme dans les sources 19.0, arbitrage D-31 —
ne dépendent d'aucune base et restent valides.

En revanche l'environnement Odoo a été reconstitué : `lab_client` est une **nouvelle** copie
synthétique (module du snapshot, aucune location), `lab_qa` une **nouvelle** base vide. **Toutes les
preuves d'exécution du run précédent ont donc été écartées** (le journal `run2-suite-complete.log`
d'alors est vide : c'est le point d'interruption). Tout ce qui est affirmé ci-dessous a été rejoué
aujourd'hui sur ces bases-ci.

### Contrôles exécutés

| Contrôle | Voie | Résultat | Preuve |
|---|---|---|---|
| `labctl lint lab_rental` (Ruff bloquant + conseils + contrôles Odoo) | statique | Ruff : **All checks passed!**, conseils : aucun. Sortie en échec (code 1) du **seul** fait de `author` manquant au manifest — dette antérieure | `logs/r2-static/lint.log` |
| Revue de forme 19.0 du diff (chaque affirmation vérifiée dans `~/odoo-sources/19.0`, fichier:ligne) | statique | **aucune anomalie** | `module_high_static_qa.md` |
| `labctl qa lab_rental --quick --fresh --tags /lab_rental:TestLabRentalDaysConstraint` | exécution | `install=ok`, **0 failed, 0 error(s) of 6 tests**, 11 s | `logs/r2-runtime/run1-fresh-tags.log` |
| `labctl qa lab_rental` — suite complète du module (point de contrôle : le modèle porte le compute `amount_total`) | exécution | `install=ok`, **0 failed, 0 error(s) of 6 tests**, 6 s | `logs/r2-runtime/run2-suite-complete.log` |
| `labctl update` (mise à niveau `-u` sur la copie `lab_client`) + contrôle de `pg_constraint` | copie client | contrainte **posée**, aucun `WARNING odoo.schema` | `logs/r2-client/01_update.log`, `02_a6_after_update.log` |
| Scénarios A1→A5 rejoués en ORM sur `lab_client` (`labctl shell`, savepoints) | copie client | tous conformes | `logs/r2-client/03_a1_a5.log` |
| Scénario A7 : `INSERT` SQL brut `days = -3` contrainte déposée → `-u` → constat → nettoyage → `-u` | copie client | **risque n°1 reproduit**, puis base remise propre | `logs/r2-client/04→09_*.log` |

### Critères d'acceptation

| # | Critère | Couvert par | État |
|---|---|---|---|
| **A1** | création `days = -1` refusée (`CheckViolation` au flush) | test `test_create_negative_days_is_rejected` (6/6 verts sur `lab_qa`) **et** rejeu ORM sur `lab_client` | **satisfait** |
| **A2** | écriture `days = -3` refusée, valeur en base restée `5` | `test_write_negative_days_is_rejected` **et** rejeu sur `lab_client` (`A2_intacte = True`, relecture SQL **et** ORM) | **satisfait** |
| **A3** | `days = 0` accepté, `amount_total == 0.0` | `test_zero_days_is_accepted` **et** rejeu sur `lab_client` | **satisfait** |
| **A4** | `days = 4 × 12.5 → 50.0` (non-régression du compute stocké) | `test_positive_days_amount_total` **et** rejeu sur `lab_client` | **satisfait** |
| **A5** | location valide intacte après rejet, curseur utilisable | `test_valid_rental_survives_rejection` **et** rejeu sur `lab_client` (`count = 3` après la violation) | **satisfait** |
| **A6** | après `-u`, `pg_constraint` contient `lab_rental_check_days_positive` / `CHECK ((days >= 0))` | voie copie client, **après mise à niveau réelle** sur base existante (`02_a6_after_update.log`, confirmé en `09_final_state.log`) ; la voie base neuve ne le prouvait qu'à l'installation | **satisfait** |
| **A7** | données violantes : contrainte **non** posée alors que l'update se termine sans erreur, puis nettoyage et A6 revérifié | voie copie client, joué explicitement (voir ci-dessous) | **satisfait — et le risque est confirmé** |
| **A8** | message configuré non vide, plus aucune occurrence de `_sql_constraints` | voie statique (message `business.py:16`, `grep` sans occurrence de `_sql_constraints`/`@api.constrains`) + voie copie client (message lu sur l'objet `Constraint`) | **satisfait sur le code** — voir réserve 3 |
| **A9** | lint sans écart nouveau imputable au diff | voie statique | **satisfait** |

### A7 — ce que la copie a réellement prouvé

Contrainte déposée, une ligne `days = -3` insérée en SQL brut, puis `labctl update` rejoué :

- Odoo journalise `check constraint "lab_rental_check_days_positive" … is violated by some row`
  en `INFO`, puis `WARNING`, puis `ERROR` ;
- l'update se termine néanmoins par `Modules loaded.`, **sans exception ni code d'erreur** ;
- après coup, `pg_constraint` **ne contient pas** la contrainte, le module reste `installed`,
  la ligne violante est toujours là.

C'est le comportement standard de la série (`odoo/orm/registry.py:682-717`), anticipé au risque n°1
de la revue — pas un défaut du module. **Conséquence opérationnelle**, à reprendre à la clôture et
avant toute mise à niveau sur une base réelle :

1. avant tout `-u` : `SELECT count(*) FROM lab_rental WHERE days < 0;` ;
2. si `> 0`, corriger ou purger **avant** la mise à niveau — l'arbitrage (mise à `0` ou suppression)
   **n'est pas tranché par D-31** et revient à Luc Roy ;
3. après le `-u`, contrôler explicitement `pg_constraint` : l'absence d'erreur ne prouve rien ;
4. ne jamais conclure que D-31 est appliquée sur la seule sortie du script de mise à niveau.

### Réserves (aucune n'est un défaut introduit par la tâche)

1. **Dette antérieure** : `lab_rental/__manifest__.py` n'a pas de clé `author` — le lint sort en
   échec pour ce seul motif et les runs de tests remontent le même avertissement. Le manifest est
   hors périmètre (version `19.0.1.0.0` volontairement inchangée jusqu'à la clôture). À arbitrer.
2. **`git diff` contre `.base` impossible dans cette copie** : le sha `9cf40f33…` référencé par
   `changelog/…/.base` n'existe pas dans l'historique (`fatal: bad object`, un unique commit
   `762d6bd` qui contient déjà l'état développé). La voie statique a délimité le diff en croisant
   trois sources (preuve du développeur, revue fonctionnelle, lecture du fichier) et le dit
   explicitement : la délimitation n'est pas mécaniquement vérifiable ici.
3. **A8 côté utilisateur non traversé** : ni un `TransactionCase` ni `labctl shell` ne passent par
   `_sql_error_to_message` (`odoo/orm/models.py:3270-3284`) puis `service/model.py:207-214`. Que le
   message français soit bien celui affiché en RPC/UI reste à voir à l'écran — **c'est la clôture
   (`/odoo-close`) qui le fera**, aucun écran n'étant produit pendant la release ouverte.
4. **`NULL` sur `days`** reste accepté par la contrainte (aucun `NOT NULL` : hors D-31, décision
   assumée et consignée).
5. `lab_client` est une copie **synthétique et vide** : rien n'est prouvé sur des volumes réels.

### Périmètre tenu

Aucune vue, aucun droit, aucun changement de `daily_rate` ni de `amount_total`, version du manifest
inchangée, aucune écriture en production, aucun déploiement. `lab_client` est laissée dans son état
initial : module `installed` en `19.0.1.0.0`, contrainte en place, **0 ligne**, aucune donnée de test
résiduelle.

### Fragments de voie (preuves détaillées)

- `.odoo-agents/flow-artifacts/d31-jours-negatifs/module_high_static_qa.md`
- `.odoo-agents/flow-artifacts/d31-jours-negatifs/module_high_runtime_qa.md`
- `.odoo-agents/flow-artifacts/d31-jours-negatifs/module_client_copy_qa.md`
