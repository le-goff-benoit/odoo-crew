# QA copie client (`lab_client`) — voie XML-RPC — contrainte-jours-positifs

**Nœud** `module_client_copy_qa` · **propriétaire** `claude-r2-tester-client-copy`
**Module** `lab_rental` · **série** 19.0 · **base** `lab_client` (copie synthétique)

Toutes les écritures ci-dessous ont été faites sur la copie synthétique `lab_client`
via `/bridge/labctl update` et `/bridge/labctl rpc`. Aucune autre base, aucun autre
fichier du dépôt (module en lecture seule) n'a été touché.

## Verdict par critère

### C02 — mise à jour du module sur `lab_client` sans erreur
**pass**
- Preuve : `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_client/logs/update.log`
- Extrait : `Module lab_rental loaded in 0.07s, 50 queries (+50 other)` puis
  `Modules loaded.` / `Registry loaded in 5.676s`, aucune ligne `ERROR`. Seuls
  avertissements présents : `Missing 'author' key in manifest` (dette
  antérieure déjà signalée par l'implémentation, hors périmètre).

### C03 — `create(days=-1)` échoue avec le message exact
**pass**
- Requête : `.../qa_client/rpc/01_create_negative.json`
  (`create` sur `lab.rental`, `name=QA-CLIENT-NEG-01, days=-1, daily_rate=10.0`)
- Preuve : `.../qa_client/logs/01_create_negative.log`
- Extrait : `"outcome": "fault", ... "fault_string": "The operation cannot be
  completed: Le nombre de jours doit être positif ou nul."`
- Le message contient exactement la phrase « Le nombre de jours doit être
  positif ou nul. » (sous-chaîne du fault, conforme à l'analyse de risque de
  la revue fonctionnelle sur l'encadrement standard `The operation cannot be
  completed: `).

### C04 — `write(days=-1)` échoue avec le même message, valeurs inchangées
**pass**
- Enregistrement de base créé par RPC : id **3**, `QA-CLIENT-BASE-03`,
  `days=5, daily_rate=20.0` → `amount_total=100.0`
  (`.../qa_client/rpc/03_create_base_for_write.json`,
  `.../qa_client/logs/03_create_base_for_write.log`,
  résultat `[3]`).
- Lecture avant tentative : `.../qa_client/rpc/04_read_base_before.json` /
  `.../qa_client/logs/04_read_base_before.log` →
  `{"id": 3, "name": "QA-CLIENT-BASE-03", "days": 5, "daily_rate": 20.0, "amount_total": 100.0}`
- Tentative refusée : `.../qa_client/rpc/05_write_negative.json` /
  `.../qa_client/logs/05_write_negative.log` →
  `"outcome": "fault", ... "fault_string": "The operation cannot be
  completed: Le nombre de jours doit être positif ou nul."` (message
  identique à C03).
- Relecture après échec : `.../qa_client/rpc/06_read_base_after.json` /
  `.../qa_client/logs/06_read_base_after.log` →
  `{"id": 3, "name": "QA-CLIENT-BASE-03", "days": 5, "daily_rate": 20.0, "amount_total": 100.0}`
  — identique à la lecture d'avant tentative : `days`, `daily_rate`,
  `amount_total` inchangés.

### C05 — création et modification avec `days=0` réussissent
**pass**
- Création : `.../qa_client/rpc/02_create_zero.json` /
  `.../qa_client/logs/02_create_zero.log` → `{"outcome": "result", "result": [2]}`
  (enregistrement id 2, `QA-CLIENT-ZERO-02`, `days=0`).
- Modification : `.../qa_client/rpc/07_write_zero.json` /
  `.../qa_client/logs/07_write_zero.log` → `{"outcome": "result", "result": true}`
  (`write(days=0)` sur l'enregistrement id 3, précédemment `days=5`).
- Confirmation par relecture : `.../qa_client/rpc/08_read_zero_after.json` /
  `.../qa_client/logs/08_read_zero_after.log` →
  `{"id": 3, "name": "QA-CLIENT-BASE-03", "days": 0, "daily_rate": 20.0, "amount_total": 0.0}`.

### C07 — après le rejet du `write`, l'enregistrement existe toujours, valeurs d'avant tentative, pas de doublon
**pass**
- Relecture ciblée par nom (garantit l'unicité, pas seulement l'id) :
  `.../qa_client/rpc/06_read_base_after.json` /
  `.../qa_client/logs/06_read_base_after.log` (méthode `search_read` sur
  `[["name", "=", "QA-CLIENT-BASE-03"]]`) → **un seul** résultat, id 3,
  valeurs identiques à celles d'avant la tentative de `write(days=-1)`
  (`days=5, daily_rate=20.0, amount_total=100.0`) : aucune perte, aucun
  enregistrement partiel, aucun doublon.

## Enregistrements créés sur `lab_client`
| id | name | days (final) | daily_rate | amount_total (final) | via |
|---|---|---|---|---|---|
| 2 | QA-CLIENT-ZERO-02 | 0 | 15.0 | (non relu après création, hors périmètre C05 création) | create |
| 3 | QA-CLIENT-BASE-03 | 0 (après scénario C05, modifié depuis 5) | 20.0 | 0.0 (après scénario C05) | create + write |

Aucun enregistrement `QA-CLIENT-NEG-01` (id) n'existe : la tentative `create(days=-1)`
a été refusée avant toute insertion (C03).

## Anomalies localisées
Aucune. Le comportement observé sur `lab_client` correspond exactement à ce que
prévoyait la revue fonctionnelle (`changelog/2026-09-09_01_interdiction-des-durees-negatives-sur-le/revue_fonctionnelle.md`,
risque #1) : le fault XML-RPC encadre le message métier du texte standard du
noyau (« The operation cannot be completed: … »), et la phrase exacte demandée
par A8/D-31 y figure intégralement comme sous-chaîne.

## Fichiers de preuve (chemins absolus)
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_client/logs/update.log`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_client/rpc/01_create_negative.json`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_client/logs/01_create_negative.log`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_client/rpc/02_create_zero.json`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_client/logs/02_create_zero.log`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_client/rpc/03_create_base_for_write.json`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_client/logs/03_create_base_for_write.log`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_client/rpc/04_read_base_before.json`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_client/logs/04_read_base_before.log`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_client/rpc/05_write_negative.json`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_client/logs/05_write_negative.log`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_client/rpc/06_read_base_after.json`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_client/logs/06_read_base_after.log`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_client/rpc/07_write_zero.json`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_client/logs/07_write_zero.log`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_client/rpc/08_read_zero_after.json`
- `/work/.odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_client/logs/08_read_zero_after.log`

## Verdict de la voie
**VALIDÉ** — les cinq critères assignés (C02, C03, C04, C05, C07) sont
**pass**, chacun avec une preuve XML-RPC réelle horodatée sur `lab_client`.
Aucune anomalie localisée. Cette voie ne se prononce pas sur C01, C06, C08
(hors périmètre assigné) ni sur les autres bases (`lab_qa`, conformité
statique).
