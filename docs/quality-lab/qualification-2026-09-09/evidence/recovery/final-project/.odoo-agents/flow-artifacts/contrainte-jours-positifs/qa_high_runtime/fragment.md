# Fragment QA — voie « exécution renforcée » (`module_high_runtime_qa`)

**Propriétaire** `claude-r2-tester-runtime` · **module** `lab_rental` · **série** 19.0
**Base** `lab_qa` exclusivement (aucune écriture sur `lab_client`, aucune
modification du code du module ni des artefacts des autres voies).

## Contexte de reprise
Le run précédent (interrompu) n'avait joué que
`--quick --tags /lab_rental:TestLabRentalDaysConstraint`. Cette voie rejoue :
1. la suite **complète** du module sur **base neuve** (`--fresh`), preuve
   d'installation depuis zéro ;
2. la **mise à jour** du module sur `lab_qa` (`--update`), preuve que
   `apply_to_database` de la contrainte s'exécute sans erreur.

## Runs exécutés

### 1. Installation à neuf + suite complète (`--fresh`)
Commande : `/bridge/labctl qa lab_rental --fresh`
Log intégral : `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_high_runtime/logs/qa_fresh.log`

```
RECETTE module=lab_rental db=lab_qa install=ok update=n.a. uninstall=n.a. tests="0 failed, 0 error(s) of 5 tests" errors=0 failed=0 skipped=0 warnings=6 total=23s base=0s install=16s tests=6s
```
`{"valid": true, "reasons": [], "module_tests": 7, "summaries": [{"failed": 0, "errors": 0, "tests": 5}]}`

- 5 tests (`TestLabRentalDaysConstraint`, seule classe de test du module),
  0 échec, 0 erreur, 0 ignoré.
- 6 avertissements, tous identiques : `Missing 'author' key in manifest for
  'lab_rental', defaulting to ''` (répétés à chaque chargement du module
  pendant la séquence install/update/reload interne au run) — **dette
  antérieure**, confirmée déjà présente avant cette tâche par la voie
  d'implémentation (`implementation.md`, section lint). Aucun avertissement
  lié au code du diff de la tâche (contrainte `days`, `tests/`).
- Aucune ligne `ERROR`/`CRITICAL`.

### 2. Mise à jour sur `lab_qa` (`--update`)
Commande : `/bridge/labctl qa lab_rental --update`
Log intégral : `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_high_runtime/logs/qa_update.log`

```
RECETTE module=lab_rental db=lab_qa install=ok update=ok uninstall=n.a. tests="0 failed, 0 error(s) of 5 tests" errors=0 failed=0 skipped=0 warnings=5 total=11s install=4s tests=7s
```
`{"valid": true, "reasons": [], "module_tests": 7, "summaries": [{"failed": 0, "errors": 0, "tests": 5}]}`

- `update=ok` : la mise à jour du module (donc l'application de
  `models.Constraint('CHECK(days >= 0)', ...)` sur la table existante de
  `lab_qa`) se termine sans erreur, table vide au moment du test (cohérent
  avec le constat de la revue fonctionnelle sur `lab_client`, mais ici c'est
  `lab_qa` qui est vérifiée, dans mon périmètre).
- Même suite de 5 tests rejouée après mise à jour, toujours 0 échec / 0
  erreur.
- 5 avertissements, même dette antérieure (`author` manquant).

## Verdict par critère assigné

### C06 — `amount_total == days * daily_rate` après création ou modification
**pass** (au niveau qui m'est assigné : la suite de tests, sur ORM interne).
Preuve : `test_amount_total_matches_days_times_daily_rate` (dans les deux
runs ci-dessus, 5/5 tests verts) vérifie explicitement :
- création avec `days=7, daily_rate=12.5` → `amount_total == 7*12.5 == 87.5` ;
- `write(days=0)` → `amount_total == 0.0` ;
- `write(days=4, daily_rate=3.0)` → `amount_total == 12.0`.

De plus `test_write_negative_days_is_rejected` et
`test_rejected_write_preserves_existing_valid_rental` revérifient
`amount_total` après un rejet (`days=5, daily_rate=10.0 → amount_total=50.0`
et `days=2, daily_rate=15.0 → amount_total=30.0`), donc la propriété tient
aussi après une tentative refusée.

Limite explicite : ces vérifications passent par l'ORM
(`TransactionCase`/`create`/`write` en process), pas par un appel XML-RPC.
Le contrat du critère C06 ne mentionne pas explicitement RPC (contrairement à
C03/C04/C05), donc je le déclare **pass** sur la base de la suite de tests
comme demandé, mais je signale que la preuve reste au niveau ORM.

### C08 — `/bridge/labctl qa lab_rental` exécute la suite entière et tout passe
**pass** pour la composante qui m'est assignée : la suite complète du module
tourne verte à l'installation à neuf (`--fresh`) et après mise à jour
(`--update`) sur `lab_qa` — 5/5 tests, 0 échec, 0 erreur, dans les deux runs.

**Composante RPC de C08 explicitement hors de ma voie et non prouvée ici.**
Le texte du critère exige « y compris par un vrai appel RPC, pas seulement
des appels ORM internes ». J'ai inspecté le seul fichier de test du module
(`lab_rental/tests/test_days_constraint.py`, classe
`TestLabRentalDaysConstraint`, 5 méthodes) : il n'existe aucun test HTTP ou
RPC dans la suite actuelle du module — tous les scénarios (`create`,
`write`, rejet, `days=0`, `amount_total`) sont exercés via l'ORM interne
(`TransactionCase`). Constat, pas correction : je ne modifie pas les tests
(hors périmètre, code du module en lecture seule pour moi).
En conséquence :
- la partie « suite verte » de C08 est **pass** (prouvée ci-dessus) ;
- la partie « couverture RPC » de C08 reste **non couverte par cette voie**
  et, d'après mon inspection du code de test, **non couverte non plus par la
  suite de tests elle-même** (aucun test RPC dans le module à ce jour) — la
  preuve RPC réelle contre `lab_client` (critères C03/C04/C05, et la
  composante RPC de C08) relève de l'autre voie QA (`lab_client`), pas de la
  mienne. Je ne déclare **pas** cette composante « pass ».

## Dette antérieure vs anomalies du diff de la tâche
- **Dette antérieure, non liée au diff** : `Missing 'author' key in manifest
  for 'lab_rental'` — confirmée déjà absente avant la tâche (voir
  `implementation.md`). Aucune action de ma part (hors périmètre, code en
  lecture seule).
- **Aucune anomalie constatée dans le diff de la tâche** (contrainte
  `days >= 0`, tests) sur les deux runs joués : 0 erreur, 0 échec, 0 warning
  spécifique au code ajouté.

## Critères hors périmètre de cette voie
C01, C02, C03, C04, C05, C07 : hors périmètre exclusif de
`module_high_runtime_qa` (respectivement lecture de code, mise à jour sur
`lab_client`, et scénarios RPC réels) — non traités ici, non déclarés
« pass » par cette voie.

## Preuves (chemins absolus)
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_high_runtime/fragment.md` (ce fichier)
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_high_runtime/logs/qa_fresh.log`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_high_runtime/logs/qa_update.log`
- `/work/lab_rental/tests/test_days_constraint.py` (inspecté, non modifié)

## Verdict de la voie
**C06 : pass** (suite de tests, niveau ORM). **C08 : pass pour la composante
« suite complète verte » ; composante RPC explicitement non couverte par
cette voie et non couverte par la suite de tests actuelle du module.** Aucune
anomalie bloquante constatée sur `lab_qa` dans mon périmètre. Dette
antérieure (`author` manquant) signalée, non corrigée.
