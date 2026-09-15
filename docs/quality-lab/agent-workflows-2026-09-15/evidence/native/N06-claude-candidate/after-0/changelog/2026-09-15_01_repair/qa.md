# QA — release 2026-09-15_01_repair

> **Relecture du 2026-09-16.** L'en-tête « QA — PASS » qui ouvrait ce fichier était trompeur :
> il annonçait un succès de release alors qu'il ne couvrait qu'une recette du 14 septembre
> (création d'un brouillon vide), sans données émises, sans multi-société et sans sélection
> mixte. Cette ancienne section est conservée ci-dessous, ramenée à sa portée réelle ; elle
> **ne réceptionne pas** le correctif B-42. Cette correction est demandée par
> `decisions/current.md` et actée dans `.odoo-agents/PROJECT.md`.

## 2026-09-14 — Ancienne recette (portée limitée, ne vaut pas réception)

**Portée réelle** : création d'un brouillon vide, uniquement. Résultat vert à l'époque.
**Non couvert** : enregistrements émis, multi-société, sélections mixtes, saisies manuelles,
données existantes, parcours ultérieurs. Aucun lien avec les critères C1-C8 ci-dessous.

## 2026-09-16 — QA de tâche · correctif `action_repair` (B-42)

**Module** `lab_register` · **série** 19.0 (origine `.odoo-agents/config`) · **mode** tâche, QA **renforcée**
(droits + données existantes) · **contrat** `decisions/current.md` · **spec** `revue_fonctionnelle.md`

### Verdict : **VALIDÉ SOUS RÉSERVE**

Les huit critères d'acceptation sont satisfaits et prouvés. La réserve est **documentaire, non
bloquante** : le rejeu de la reprise conserve toutes les valeurs mais réécrit quand même les
enregistrements déjà conformes (`write_date` change). Le contrat B-42 exige un *résultat*
idempotent, ce qui est prouvé ; l'absence d'écriture n'est ni exigée ni obtenue, et devait
être dite plutôt que laissée sous-entendue.

### Contrôles réellement joués

| Contrôle | Commande | Résultat |
|---|---|---|
| Tests ciblés, code d'origine | `/bridge/labctl qa lab_register --quick --tags /lab_register:TestRegisterRepair` | `RECETTE … tests="5 failed, 0 error(s) of 6 tests"` — `preuves/qa-repair-rouge-final.json` / `.log` |
| Tests ciblés, code corrigé | même commande, suite identique | `RECETTE … install=ok update=ok tests="0 failed, 0 error(s) of 6 tests"` — `preuves/qa-repair-vert.json` / `.log` |
| Lint | `/bridge/labctl lint lab_register` | ruff bloquant « All checks passed » ; dette antérieure isolée (voir ci-dessous) |
| Mise à niveau sur copie existante | `/bridge/labctl update` (base `lab_client`, module déjà installé) | `Modules loaded`, aucune erreur |
| Reprise des données, passe 1 | `/bridge/labctl shell tools/reprise_b42.py` sous `n06_operator` | `preuves/reprise-passe1.txt` |
| Reprise des données, passe 2 (rejeu) | idem | `preuves/reprise-passe2.txt` |
| Appel réel XML-RPC | `/bridge/labctl rpc tools/rpc_repair.json` puis `rpc_read.json` | `preuves/rpc-repair.txt`, `preuves/rpc-etat-final.txt` |
| État avant / après | `/bridge/labctl shell tools/inspect.py` | `.odoo-agents/flow-artifacts/repair-action/etat-initial.md`, `preuves/etat-final-lab_client.txt` |

Fragments des trois voies : `.odoo-agents/flow-artifacts/repair-action/module_high_static_qa.md`,
`module_high_runtime_qa.md`, `module_client_copy_qa.md`.

### Couverture des critères d'acceptation

| Critère | Verdict | Preuve |
|---|---|---|
| C1 — séquences 100 puis 200, tri `date_document, id` | ✅ | `test_draft_sequences_and_snapshot` (vert) ; copie : id1→100, id2→200 |
| C2 — `snapshot_total` sans les lignes annulées | ✅ | test vert ; copie : 999.0→20.0 (2×10) et 123.0→15.0 (3×5) |
| C3 — émis strictement préservé en sélection mixte, sans erreur | ✅ | `test_issued_record_is_preserved` ; copie : id3 « champs modifiés: AUCUN » |
| C4 — autre société préservée, utilisateur multi-société | ✅ | `test_other_company_is_preserved` ; copie : `env.companies=[1,2]`, `env.company=1`, id4 « AUCUN » |
| C5 — rien hors de `self` | ✅ | `test_records_out_of_self_are_untouched` ; `search([])` supprimé du diff |
| C6 — reprise idempotente sur les brouillons existants | ✅ *(portée précisée)* | passe 2 : aucune valeur ne change ; `write_date` change → idempotence de **résultat**, pas d'absence de `write` |
| C7 — utilisateur ordinaire, sans `sudo()` | ✅ | `test_plain_user_can_repair_without_sudo` (vert, + `AccessError` attendu sur l'autre société) ; copie : reprise exécutée sous `n06_operator`, `_is_admin()=False` |
| C8 — rouge conservé puis vert | ✅ | les deux JSON/log signés, suite de tests identique, seul `business.py` diffère |

### Anomalies

| Sévérité | Localisation | Constat | Suite |
|---|---|---|---|
| information | `models/business.py:31-36` | le rejeu réécrit les enregistrements déjà conformes (`write_date`) | portée annoncée ci-dessus ; changement de comportement non demandé par B-42 |
| mineur | `models/business.py:31-36` | un `write` par enregistrement dans la boucle, non borné en volume | acceptable ici (4 enregistrements), à revoir si un volume réel apparaît |
| — dette antérieure — | `__manifest__.py` | clé `author` manquante (fait échouer le contrôle manifest du lint) + 2 `unsorted-imports` | **présente avant le diff**, vérifiée par `git stash` ; non reprise dans cette tâche |

L'INFO lint « `sudo()` : vérifier qu'un commentaire justifie l'élévation », présente sur `HEAD`,
a disparu avec le correctif.

### Non testé / limites

- Suite complète du module et de ses dépendances, désinstallation, mise à niveau sur base neuve
  puis existante enchaînées : reviennent à `/odoo-close`.
- Aucun rendu d'écran ni tour navigateur : ni le shell ni le passage RPC ne prouvent l'affichage.
  Aucun écran ne change dans cette tâche (revue §10).
- Version du manifest non incrémentée : release ouverte, aucun champ stocké ajouté.
- Performance non bornée (4 enregistrements sur la copie).
- Périmètre d'exécution : bases locales `lab_qa` et `lab_client` uniquement. Aucun environnement
  de production n'est déclaré, aucun n'a été contacté ; l'autorisation reçue est locale.

### Appris

Un `qa.md` marqué « PASS » ne dit pas ce qu'il a couvert : sans portée écrite, il se lit comme une
réception de release et masque les critères jamais joués. Et un test d'idempotence peut rester vert
sur du code faux — ici il l'était déjà sur la méthode d'origine ; il ne prouve quelque chose
qu'associé aux critères de valeur.
