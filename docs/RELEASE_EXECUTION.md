# Intentions, contrats et exécution observable

Les fichiers de release appartiennent à l'orchestrateur. Le cockpit les lit et
prépare les commandes ; il n'écrit pas un second état de workflow.

## Préparer les intentions

```bash
python3 scripts/odoo_intentions.py update PROJET/changelog/RELEASE --file intentions-definition.json
```

La définition contient `items`. Exemple minimal :

```json
{"items":[{"id":"I01","text":"Voir le total par section",
 "source":{"path":"changelog/RELEASE/demande.md"},
 "purpose":"Relire les montants par section",
 "criteria":["Chaque section montre son total"],
 "constraints":[],"decisions":[],"questions":[]}]}
```

Le registre `intentions.json` (schéma 1) conserve le texte original de chaque
source, son empreinte, une révision et l'historique complet des remplacements.
Une mise à jour de couverture conserve la source historique ; une nouvelle version
de la source se demande explicitement avec `source.refresh: true`.
États : `clarify`, `ready`, `planned`, `satisfied`, `deferred`. Une question ouverte
maintient `clarify`. Un ajout ne réécrit pas les intentions précédentes.

`reconcile RELEASE` reconstruit les liens des tâches. La satisfaction exige les
réceptions applicables **et** une couverture explicite de tous les critères :

```json
{"coverage":[{"criterion":"Chaque section montre son total",
 "task":"T01","task_criterion":"Chaque section montre son total"}]}
```

Ces liens font partie de la définition d'intention mise à jour par l'orchestrateur ;
le critère de tâche doit exister textuellement. Cette vérification de cohérence ne
remplace pas la relecture métier des résultats. Une solution standard sans tâche
utilise `satisfy RELEASE --intention I01 --proof chemin-relatif.json` : preuve
réussie et vérifiée, aucune question ouverte. Une intention sans couverture reste
planifiée même lorsque les tâches liées sont reçues.

## Écrire le contrat avant le développement

Les plans historiques schéma 1 restent lisibles. Schéma 2 pour un nouveau plan :

```json
{"schema":2,"author":{"role":"orchestrator","provider":"codex","model":"MODELE_PRINCIPAL"},
 "decisions":[],"intentions_file":"changelog/RELEASE/intentions.json",
 "tasks":[{"id":"T01","title":"Totaliser les sections",
 "request":"changelog/RELEASE/demande.md","request_excerpt":"Texte exact et unique de cette demande",
 "intentions":["I01"],"acceptance":["Chaque section montre son total"],
 "route":"module","risk":"normal","depends_on":[],"scopes":["module_custom"],
 "reads":[],"writes":["module_custom"],
 "checks":[{"id":"sections","command":["python3","-m","unittest","test_sections"],
 "environment":"copie-neutralisee-identifiee","cases":["section vide","section avec lignes","sous-section"]}],
 "execution":{"provider":"codex","model":"MODELE_RETENU","effort":"medium"}}]}
```

Une tâche technique sans intention porte `technical_reason`. Les cas doivent
viser les résultats attendus : par exemple, deux demandes modifiant une hiérarchie
de rapport partagent d'abord un arbitrage de cette hiérarchie ; un test de séquence
vérifie l'ordre contractuel sans figer une valeur destinée à changer dans la tâche
suivante. La mécanique vérifie les références et formes, pas la justesse de ces
arbitrages. Le principal garde la responsabilité de leur pertinence.

`request_excerpt` évite qu'une demande indépendante ajoutée au même document
invalide la tâche reçue. L'extrait doit rester exact et unique ; sa modification
périme le contrat. Sans extrait, l'empreinte du document entier reste conservatrice.
Les champs liés d'une intention entrent dans le contrat, sans inclure son simple
statut ou sa liste de tâches. `revise RELEASE --file changement.json --reason SOURCE`
archive l'ancienne version ; une tâche active se termine/s'interrompt avant révision.

La réception vérifie chaque contrôle prescrit, avec la commande `argv` exacte et
l'identité d'environnement exacte. Pour un seul contrôle, `finish --proof ...`
suffit si la preuve correspond. Pour plusieurs contrôles, `finish --check-proofs
checks.json` prend un objet `{"sections":"preuves/sections.json","autre":"preuves/autre.json"}`
(chemins relatifs au projet). Tous les contrôles doivent réussir et leur union
couvrir le périmètre/les lectures ; omettre un contrôle ou présenter une autre
commande réussie refuse la réception. Leurs preuves et logs restent vérifiés après
réception. Les critères métier restent réceptionnés par l'orchestrateur.

## Preuves et candidats

`odoo_evidence.py run` refuse de réutiliser le chemin d'une preuve ou d'un log.
Une nouvelle exécution reçoit un nouveau chemin. `--environment IDENTITE` enregistre
l'environnement réel annoncé (image, jeu de données, outils), distinct du poste
Python du runner. `verify(..., expected_environment=...)` refuse une autre identité.
Une identité absente reste inconnue.

Les nouvelles réceptions hachent le résultat : contrat, sources, environnement,
critères/consolidation et résultats des dépendances. Date de réception, durée et
nouveau nom du log n'invalident pas un dépendant à résultat identique. Les anciennes
réceptions conservent leur règle conservative. Aucun hash d'une ancienne preuve
n'est réécrit pour la rendre applicable.

Une preuve peut s'appliquer à un autre worktree local du **même dépôt Git**, identifié
par son `git-common-dir`, à la même révision HEAD et au même contenu contrôlé. Les
logs relatifs sont revérifiés dans le checkout cible. Un clone autonome, une autre
révision, un log altéré ou des sources différentes demandent une nouvelle preuve.
Cette portabilité locale n'est pas une identité distribuée entre machines.

`check_scopes` peut borner les contrôles en risque normal, avec `selection_reason`
explicitant l'analyse d'impact. Les `reads` sont toujours inclus dans la couverture.
En risque élevé, le périmètre complet est obligatoire. Une inconnue reste large ;
la recette d'intégration finale demeure nécessaire.

À une borne QA sans revendication :

```bash
python3 scripts/odoo_candidate.py freeze RELEASE --task A \
  --candidate /tmp/worktree-A --resources ressources-A.json
```

Le worktree est distinct, de même dépôt/révision, avec exactement les sources à
contrôler. Les ressources ont les clés `database`, `filestore`, `port`, `container`,
`logs` et des identités physiques canoniques (par exemple
`postgresql://localhost:5432/qa_a`, `path:/tmp/filestore-a`, `port:18069`,
`container:qa-a`, `path:/tmp/logs-a`). B déclare aussi ses `resources` dans le plan.
Le projet doit déclarer `.odoo-agents/resources.json` avec le registre physique
partagé (même registre entre projets utilisant les mêmes ressources) avant de
démarrer une tâche avec `resources` ; l'absence de cette configuration est refusée.
Les tests utilisent un registre commun dans leur dossier temporaire.
Les revendications QA prennent réellement ces verrous ; chemins parents/enfants
conflictuels sont détectés. Un candidat modifié refuse la réception. Le gel ne
crée ni DB ni conteneur : leur préparation reste une action contrôlée de l'agent.
L'exemption de réservation source ne vaut que pendant la phase QA active. Un
verdict `retry` archive le candidat et rétablit les verrous de la source ; la
reprise de développement attend toute autre tâche qui réserve encore ce périmètre.

## Orchestration et hooks

```bash
python3 scripts/odoo_orchestrate.py activate --project PROJET --owner codex-orchestrator \
  --provider codex --model MODELE_PRINCIPAL --session-id SESSION
python3 scripts/odoo_orchestrate.py attach --project PROJET --owner codex-orchestrator \
  --release PROJET/changelog/RELEASE --task A --task B --phase implementation
```

État local `.odoo-agents/orchestration.json`, miroir dans `release/orchestration.json`.
L'identité et `started_at` survivent au rattachement préparation→release ; une phase
nouvelle a `phase_started_at`. Les anciens runs sont archivés par identifiant avant
activation du suivant. `progress`, `waiting-human`, `waiting-resource`, `pause`,
`interrupt`, `resume`, `complete` portent phases/statuts/motifs/révisions. Une fin
refuse les tâches autorisées encore ouvertes. Les durées d'attente ne deviennent
pas de l'effort actif ; le lecteur doit utiliser les transitions de l'historique.

Le hook `hook --project PROJET` reçoit l'événement natif par stdin et reste en
lecture seule. Pour le Stop de la session principale liée, un run actif avec des
actions autorisées prêtes reçoit un rappel de continuation (`decision:block`).
Sous-agent, autre session, StopFailure, interruption, attente et absence d'action
ne déclenchent pas ce rappel. `stop_hook_active` borne la relance sans progrès.
Le hook ne réceptionne aucune tâche et ne libère aucun verrou. La réaction effective
du CLI se qualifie séparément des tests déterministes.

Tricorder ajoute `--events JOURNAL_NATIF` : le garde lit seulement les métadonnées
collectées. Une interruption ou un échec de la session principale empêche une
continuation jusqu’à `resume`, même si le principal n’avait pas eu le temps
d’enregistrer son arrêt. Une demande de résumé après interruption ne relance donc
pas le run. Une simple mise à jour d’avancement ne vaut pas nouvelle autorisation.

Le pilote `tests/fixtures/orchestration_probe.py` utilise A→B→C et de vraies
assertions/réceptions pour tester les reprises natives. La fermeture de flow y est
synthétique, explicitement marquée ; ce pilote ne qualifie aucune chaîne Odoo ni
base client. Le test des candidats fait réellement chevaucher deux subprocess et
vérifie ensuite A+B, avec une attente artificielle contrôlée : ses durées ne
prédissent pas un gain de release Odoo.
