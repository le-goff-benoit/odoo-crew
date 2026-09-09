# Réception indépendante — release `2026-09-09_01_frais-de-preparation-des-locations`

**Objet** : réception **sur pièces** du dossier de tâche déjà traité (points 1 « D-02 » et 2 « D-03 »),
dans une copie jetable. **Aucune base ni aucun processus Odoo n'était disponible** : rien n'a été
réexécuté. Les contrôles ci-dessous sont des vérifications de fichiers, d'empreintes et de cohérence
interne, faites avec des outils locaux. Les archives (`archives-execution/`, `historique/D02/`) ont
été lues sans modification. Le flow historique n'a pas été rouvert.

**Série** 19.0 (`.odoo-agents/config` : `ODOO_SERIES=19.0`, cohérent avec `__manifest__.py`).
**Réceptionnaire** : réception indépendante, 09.09.2026.

---

## 1. Verdict

**RECEVABLE — le dossier atteste ce qu'il annonce.** Ce que la release livre est **D-03**
(15 EUR à partir de 5 jours inclus, prêts exclus) ; le point 1 (D-02) est correctement marqué périmé
sans destruction de preuve ; la release est restée **ouverte** comme demandé.

Aucune anomalie bloquante. **Huit réserves** non bloquantes, dont **une seule** appelle une décision
humaine avant la clôture (R1). Le verdict de la QA de tâche du point 2 (« VALIDÉ, 14/14 ») est
**confirmé** : je n'ai trouvé aucun critère déclaré couvert dont la preuve citée ne le porte pas.

Ce dossier n'est **pas** une fixture documentaire synthétique : il repose sur des exécutions réelles,
dont les journaux bruts du pont sont joints et se recoupent octet pour octet avec les preuves
(§ 2.3). Ce qui est synthétique, c'est le **projet** (« Atelier Boréal », données du bac) — ce que
`LAB.md` annonce d'emblée. La demande de la campagne étant déjà étayée par ces exécutions, **aucune
nouvelle exécution Odoo n'est nécessaire à cette réception**.

---

## 2. Ce que j'ai vérifié moi-même

### 2.1 Conformité du code à la décision qui fait foi

`decisions/2026-09-09.md` (D-03) : `jours × tarif + 15 EUR si type=location ET jours >= 5`.

`lab_rental/models/business.py` :

```python
PREPARATION_FEE = 15.0
PREPARATION_FEE_MIN_DAYS = 5
...
is_long_enough = self.days >= self.PREPARATION_FEE_MIN_DAYS
return self.PREPARATION_FEE if self.kind == 'rental' and is_long_enough else 0.0
```

Conforme, borne **inclusive**, forfait **fixe**, prêts exclus sans condition de durée. Le
`@api.depends('days', 'daily_rate', 'kind')` couvre les trois entrées ; `store=True` inchangé.
Rien d'autre n'a bougé : pas de vue, pas de droit, pas de champ, `depends = ['base']`.

Les 12 tests de `tests/test_preparation_fee.py` portent leurs oracles **depuis la décision**, pas
depuis la méthode, et incluent deux non-régressions explicites sur les règles mortes (D-01 à 7 %,
D-02 à 12 EUR / 4 jours). Les 12 méthodes couvrent bien les 11 critères unitaires C01–C11.

### 2.2 Chaîne de garde du contrat de QA — intacte

| Contrôle | Résultat |
|---|---|
| SHA-256 de `revue_fonctionnelle_point2.md` déclaré dans `qa_reception_point2.md` | `7e666b30…a049d4` = **empreinte réelle du fichier** ✅ |
| SHA-256 de `revue_fonctionnelle.md` déclaré dans `qa_rapport_tache1.md` | `a8463954…dbdd3321` = **empreinte réelle** ✅ |
| Les 14 critères du contrat enregistré dans le flow | **identiques mot pour mot** aux 14 cases de `revue_fonctionnelle_point2.md` ✅ |
| Les 14 critères de `coverage.json` | identiques au contrat ; `contract_sha256` identique ✅ |
| SHA-256 des 11 fichiers de preuve cités par les 14 critères | **11/11 conformes**, aucun écart ✅ |
| `qa_reports` du flow ↔ fichiers rendus (`qa_reception_point2.md` `9775e6b6…`, `coverage.json` `db0e304e…`) | conformes ✅ (idem pour le point 1 : `07fb7890…`, `3ea7107a…`) |
| `resource-locks.json` | `claims: []` — tous les verrous relâchés ✅ |
| Nœuds du flow `frais-preparation-d03` | 9/9, `module_high_gate: pass`, `task_done: done`, statut `complete` ✅ |

Aucune preuve n'a été retouchée après coup.

### 2.3 Recoupement avec les journaux bruts du pont (contrôle non prévu par le dossier)

`archives-execution/` contient 32 journaux `labctl` produits par l'outil, hors du contrôle de
l'agent. J'ai comparé leurs empreintes à celles des preuves de la release :

- `qa_runtime.txt` (D-03) = **bridge-020** octet pour octet ; `qa_runtime_update.txt` = **bridge-021** ;
  `copie_client_avant.txt` = **bridge-022** ; `copie_client_update.txt` = **bridge-023** ;
  `copie_client_update2.txt` = **bridge-025**. Les autres preuves (`copie_client_apres.txt`,
  `…_postconditions.txt`, `…_idempotence.txt`, `rpc_seuil.txt`) sont des **extraits fidèles** des
  bridges 024, 026, 027 et 028–031 : j'ai vérifié le texte ligne à ligne.
- Les horodatages internes des bridges sont **strictement croissants** avec la numérotation
  (14:16:32 → 14:28:05), ce qui donne un ordre d'exécution opposable.
- `bridge-023` porte bien `module lab_rental: Running upgrade [19.0.1.2.0>] post-migrate` ;
  `bridge-025` (2ᵉ `-u`) **ne le porte pas** — exactement ce que la réserve consignée dans `qa.md`
  affirme. Le dossier ne surestime pas sa preuve sur ce point.
- Les tests : `0 failed, 0 error(s) of 12 tests` en install **et** en update, 12 méthodes
  `TestPreparationFee` démarrées et nommées dans le journal. Conforme au « 12/12 » annoncé.
  *(Le `"module_tests": 14` du validateur vaut `tests + 2` sur les deux runs — 12/10 au point 1,
  14/12 au point 2 : biais systématique de l'outil, pas une anomalie du dossier.)*

### 2.4 Traitement du point périmé — conforme et vérifié par différence

Comparaison de `historique/D02/` (instantané de fin du point 1) avec l'état livré :

- `revue_fonctionnelle.md`, `qa_rapport_tache1.md` et **l'intégralité** de
  `.odoo-agents/flow-artifacts/frais-preparation/` : **identiques**, non retouchés ✅
- `qa.md` : **0 ligne supprimée** — bandeau « périmé » et section du point 2 ajoutés, verdict du
  point 1 conservé mot pour mot ✅
- `README.md` : **une seule ligne réécrite**, celle du point 1, pour la marquer PÉRIMÉ ✅
- `demande.md` : purement additif (complément D-03) ✅

C'est le comportement attendu : marquer là où on lit, sans effacer.

### 2.5 Consignes de la demande

| Exigence | État |
|---|---|
| Total calculé **et stocké** | ✅ `Float`, `compute`, `store=True`, inchangé |
| Sans changer les écrans | ✅ `VUES 0 ACTIONS 0 MENUS 0 REGLES 0` sur `lab_client` ; diff sans XML |
| Sans facturer | ✅ aucune dépendance ajoutée, `depends = ['base']` |
| Tests métier + QA de tâche + journal | ✅ 12 tests, `qa.md`, `JOURNAL.md` (2 entrées, ≤ 15 lignes utiles) |
| **Release ouverte** | ✅ `.opened` présent, `README.md` porte `<!-- release ouverte -->` |
| Aucun livrable documentaire avant clôture | ✅ ni guide, ni capture, ni communication dans la release |
| Reprise de données prouvée | ✅ `migrations/19.0.1.2.0/post-migrate.py`, mesurée **à la baisse** (52.0 → 40.0) |

---

## 3. Réserves et suites

| # | Réserve | Sévérité | Suite concrète |
|---|---|---|---|
| **R1** | `'author': 'Camptocamp'` ajouté au manifest, **jamais confirmé** par l'humain, sur un projet nommé « Atelier Boréal ». Signalé trois fois par le dossier (`qa.md`, `JOURNAL.md`, `compte_rendu.md`) — c'est honnête, mais la clé est **livrée** dans le diff. | **Majeure (porte humaine)** | Poser la question à la clôture : soit confirmer l'auteur, soit retirer la clé et traiter l'avertissement de lint autrement. Ne pas clore sans réponse. |
| **R2** | `lint.txt` du point 2 est **octet pour octet identique** à celui du point 1 (`65d7d084…`) : l'artefact seul ne prouve pas qu'un lint a été rejoué après le changement D-03. | Mineure — **levée** | Levée par les bridges : `bridge-018`/`019` (deux exécutions de lint) se situent entre 14:19:21 et 14:26:23, donc **dans le segment D-03**. Suite outillage : faire estampiller la sortie de `labctl lint` (horodatage, module, empreinte du code linté), sinon un artefact de lint n'est jamais opposable. |
| **R3** | `.odoo-agents/flow-artifacts/.gitignore` vaut `*` : **les preuves ne sont pas versionnées**. Or `qa.md` et `qa_reception_point2.md`, qui sont les livrables du dossier, fondent tout leur verdict sur ces chemins (`../../.odoo-agents/flow-artifacts/…`). | Moyenne | À `/odoo-close` : recopier dans le dossier de release les preuves décisives (au minimum `copie_client_avant/apres/idempotence/postconditions`, les deux `qa_runtime`, `lint.txt`, `coverage.json`), ou intégrer leurs extraits dans `qa.md`. Sinon, après clonage, le dossier livré n'est plus vérifiable. |
| **R4** | `.odoo-agents/shell/postconditions_point2.py` a **perdu** le contrôle `AUTOMATISATIONS` présent dans `postconditions.py` (point 1). Le périmètre de la non-régression en base a rétréci d'un point à l'autre. | Mineure | Sans conséquence ici (rien ne crée d'automatisation, et `base.automation` n'est pas installé), mais rétablir la ligne avant de rejouer ces postconditions à la clôture. |
| **R5** | Le chemin **19.0.1.0.0 → 19.0.1.2.0** (traversée des deux `post-migrate` d'affilée) n'a jamais été exécuté. Déclaré comme tel par `qa.md`. | Mineure | À jouer à `/odoo-close` sur base neuve semée avec `seed_avant.py`. Le risque est faible : les deux scripts sont le **même** `add_to_compute` sur tout `lab.rental`, donc la seconde passe est un recalcul redondant et inoffensif. |
| **R6** | C13 (idempotence de la reprise) est prouvé en **rappelant le corps** du script (`reprise_idempotence.py`), pas en rejouant le fichier de migration — le 2ᵉ `-u` ne le rejoue pas. Réserve consignée par le dossier. | Mineure — **acceptable** | J'ai vérifié la fidélité de la transcription : `reprise_idempotence.py` reproduit exactement les trois instructions de `migrations/19.0.1.2.0/post-migrate.py` (`search([])` → `add_to_compute` → `flush_all`). La preuve tient. À la clôture, la base neuve donnera la mesure directe. |
| **R7** | Fichier verrou parasite `/work/.frais-preparation.lock` (0 octet) à la **racine du projet**, absent de l'instantané `historique/D02/`, non couvert par un `.gitignore` (seul `.odoo-agents/flows/` en a un). | Cosmétique | Le supprimer avant commit, et corriger le dispositif pour que le verrou s'écrive dans `.odoo-agents/flows/` comme ses homologues. |
| **R8** | Non prouvés, et **déclarés** comme tels : rendu visuel, comportement pour un utilisateur non-admin, suite complète du module, désinstallation, tours navigateur. | Attendu | Relève de `/odoo-close`. Aucune action à ce stade — la QA de tâche n'avait pas à les couvrir. |

### Recommandation métier reconduite

Le dossier signale que la règle a été **réécrite trois fois en deux jours** (D-01 → D-02 → D-03) et
que le paramétrage du seuil et du montant reste volontairement hors périmètre. Je reconduis la
recommandation : à la prochaine révision, reposer la question du paramétrage au client, en chiffrant
l'écran de réglage et la valeur par défaut à migrer. Ce n'est pas une décision à prendre en QA.

---

## 4. Propositions de correction

Aucune correction n'est proposée **dans** le module ou dans les preuves : rien n'y est faux. Les
propositions sont, par ordre :

1. **R1** — trancher `author` avec l'humain (porte de clôture).
2. **R3** — verser les preuves décisives dans le dossier de release à la clôture.
3. **R4** — rétablir la ligne `AUTOMATISATIONS` dans `postconditions_point2.py`.
4. **R7** — supprimer le verrou parasite à la racine.
5. **R5** — jouer le chemin `19.0.1.0.0 → 19.0.1.2.0` à la clôture.
6. **R2** — estampiller la sortie de `labctl lint` (amélioration du banc, `/odoo-improve`).

Ces propositions **ne remplacent ni les preuves ni les décisions reçues** ; elles s'y ajoutent.

---

## 5. Suite du cycle

La release **doit rester ouverte** (exigence de la demande, respectée). L'étape suivante est
`/odoo-close` : recette complète, recette navigateur, livrables client, README final — avec, en
entrée, R1 (question à l'humain), R3, R4 et R5.

**Sources de cette réception** : `demande.md`, `decisions/2026-09-08.md`, `decisions/2026-09-09.md`,
`changelog/2026-09-09_01_…/{README.md,qa.md,revue_fonctionnelle.md,revue_fonctionnelle_point2.md,qa_rapport_tache1.md}`,
`lab_rental/**`, `.odoo-agents/{PROJECT.md,JOURNAL.md,config,shell/*,flows/*.json,flow-artifacts/**}`,
`archives-execution/{environment.json,prompt-0.txt,prompt-1.txt,bridge-000…031.log}`,
`historique/D02/**`.
