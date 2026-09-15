# Livraison : commit contrôlé et déploiement observé

`odoo_delivery_guard.py` est un lecteur de Git et de preuves locales. Il ne
lance ni build, ni script du projet, ni connexion distante, ni déploiement. Un
push ne produit jamais le statut `deployed_verified`.

## États et responsabilités

| État | Ce que les preuves permettent de conclure |
|---|---|
| `blocked` | Le commit ne satisfait pas les contrôles statiques. |
| `prepared` | Contrat créé depuis les objets Git ; aucun build encore validé. |
| `ready_to_deliver` | Build convenu réussi, lié au commit et à tous les fichiers des modules. |
| `deployed_verified` | Identité cible, build, versions installées, migrations et effets attendus relus dans des captures liées par empreintes. |

L'orchestrateur choisit **avant le contrôle** le commit de base, le commit cible,
les modules, l'argv réellement pertinent du build, l'identité de l'environnement
de contrôle et de la destination, et les valeurs attendues des lectures.
La base est la révision correspondant aux versions réellement installées avant
la mise à jour ; une capture liée des versions avant/après est exigée pour le
statut de déploiement vérifié.
Un changement de contrat appelle une nouvelle préparation, pas la modification
d'un résultat pour le rendre vert.

## Préparer, puis contrôler le build

Exemple fictif (les variables désignent des chemins/révisions propres au projet) :

```bash
python3 ~/.odoo19-agents/scripts/odoo_delivery_guard.py prepare \
  --repo "$PROJECT" --base "$BASE_COMMIT" --target "$TARGET_COMMIT" \
  --module addons/example \
  --build-command-json '["./ci/build-example.sh"]' \
  --build-environment 'local:odoo19:image-sha:data-snapshot-id' \
  --target-environment 'staging:project:database-id' \
  --effects-json '{"example_column_present":true,"legacy_rows_remaining":0}' \
  --output "$PROOFS/delivery-contract.json"
```

Exécuter le build autorisé séparément avec `odoo_evidence.py run` dans un checkout
au commit cible, en couvrant chaque module déclaré. Le script de garde ne décide
pas quelle commande constitue un build suffisant. Les périmètres supplémentaires
hors modules sont acceptés ; des fichiers supplémentaires dans les modules sont
refusés. Les liens symboliques et sous-modules ne constituent pas des fichiers
réguliers pris en charge par ce contrôle.

```bash
python3 ~/.odoo19-agents/scripts/odoo_evidence.py run \
  --project "$PROJECT" --scope addons/example \
  --environment 'local:odoo19:image-sha:data-snapshot-id' \
  --output "$PROOFS/build.json" -- ./ci/build-example.sh
sha256sum "$PROOFS/build.json"
python3 ~/.odoo19-agents/scripts/odoo_delivery_guard.py verify \
  "$PROOFS/delivery-contract.json" \
  --build-proof "$PROOFS/build.json" --build-sha256 "$BUILD_SHA256" \
  --output "$PROOFS/ready.json"
```

Le fichier de preuve `odoo-evidence/1`, son log et les sources de contrôle sont
revérifiés. Préserver le checkout candidat tant que la preuve doit être relue.
Chaque sortie de la garde est créée exclusivement : un chemin déjà existant est
refusé. Les empreintes détectent une modification ultérieure ; elles ne sont pas
une signature ni une attestation émise par un tiers de confiance.

## Lire l'état effectivement déployé

Une collecte autorisée et adaptée à la plateforme fournit un fichier JSON
`odoo-deployment-observation/1`. La garde **ne réalise pas cette collecte**.
Utiliser les protections habituelles de `odoo_instance.py` pour la production,
et ne mettre aucun secret ni donnée client dans ces preuves.

```json
{
  "format": "odoo-deployment-observation/1",
  "commit": "SHA_COMPLET_CIBLE",
  "target_environment": "staging:project:database-id",
  "build_id": "identifiant-du-build-observe",
  "before": {"path": "/preuves/before.json", "sha256": "EMPREINTE"},
  "build_status": "success",
  "observed_at": "2026-09-15T18:00:00+00:00",
  "installed_modules": {
    "example": {"state": "installed", "version": "19.0.1.1.0"}
  },
  "effects": {
    "example_column_present": {
      "passed": true,
      "read_command": ["identifiant-de-la-lecture-autorisee"],
      "actual": true,
      "source": {"path": "/preuves/column-read.json", "sha256": "EMPREINTE"}
    },
    "legacy_rows_remaining": {
      "passed": true,
      "read_command": ["identifiant-de-la-lecture-autorisee"],
      "actual": 0,
      "source": {"path": "/preuves/rows-read.json", "sha256": "EMPREINTE"}
    }
  },
  "migrations": {
    "addons/example/migrations/19.0.1.1.0/post-cleanup.py": {
      "path": "/preuves/migration-run.json", "sha256": "EMPREINTE"
    }
  }
}
```

La référence `before` contient une capture `odoo-deployment-baseline/1` :
`commit` de base, `target_environment`, `observed_at` et `installed_modules`
(même structure que ci-dessus, avec les versions de départ). Elle est recueillie
après préparation du contrat et avant la lecture finale ; sa date est contrôlée.
Une installation initiale indique explicitement `state: "uninstalled"` et
`version: null`. Une version de départ différente bloque : réviser la base et
le contrat, puis refaire les contrôles affectés. La seule version dans Git
ne prouve jamais ce qui était installé.

Chaque source de lecture contient `commit`, `target_environment`, `effect`
(l'identifiant convenu) et `actual`. Chaque source de migration contient
`commit`, `target_environment`, `migration` (chemin complet du script) et
`executed: true`. Conserver les captures de sortie ayant servi à produire ces
relevés ; ne pas reconstruire des « preuves » à partir de la seule intention.
Toute migration située dans la plage des versions installée et cible requiert
cette preuve d'exécution, même si son fichier n'a pas changé entre les commits. Une version
installée correcte ou un fichier présent ne suffit pas à démontrer la migration.

```bash
python3 ~/.odoo19-agents/scripts/odoo_delivery_guard.py verify \
  "$PROOFS/delivery-contract.json" \
  --build-proof "$PROOFS/build.json" --build-sha256 "$BUILD_SHA256" \
  --deployment "$PROOFS/deployment.json" --deployment-sha256 "$DEPLOYMENT_SHA256" \
  --output "$PROOFS/deployed.json"
```

Une capture antérieure au contrat, sans fuseau, future, visant une autre cible,
avec une ancienne version, un build en échec ou un effet différent de la valeur
contractuelle est refusée. L'outil ne prouve pas l'authenticité d'un relevé fabriqué
par son auteur ; l'examen de la collecte et des sorties sources reste nécessaire.

## Contrôles statiques et limites

- Lecture des objets Git exacts, jamais import Python du module. Chaque fichier
  reçoit une empreinte ; fichiers `data`/`demo`, assets locaux et imports relatifs
  doivent être présents. Les fichiers locaux non suivis ne réparent pas le commit.
- Manifests littéraux et versions numériques explicites. Les versions abrégées,
  manifests dynamiques et installations initiales comportant des migrations
  demandent une revue dédiée : pas d'inférence silencieuse.
- AST prudent : compare les déclarations directes `fields.*` de classes. Toute
  différence déclenche un signal de schéma potentiel et exige une hausse de
  version, y compris pour des changements purement descriptifs. Cela ne prouve
  ni le schéma réel ni la nécessité d'une migration : SQL manuel, champs ajoutés
  dynamiquement, alias et changements hérités demandent une revue spécifique.
- Les imports absolus, imports dynamiques et attributs exportés depuis un package
  ne sont pas résolus complètement. Un import relatif ambigu peut bloquer à tort ;
  examiner le cas et améliorer le contrôle plutôt que masquer le résultat.
- Scripts nouveaux/modifiés sous `migrations/` ou `upgrades/` : nom
  `pre|post|end-*.py`, fonction `migrate`, version dans l'intervalle
  `base < migration <= cible`. Les anciens scripts inchangés sont conservés.
  Tous les scripts dans cette plage requièrent une preuve d’exécution, y compris
  ceux déjà présents au commit de base. Cette plage suit la [documentation officielle Odoo 19.0](https://www.odoo.com/documentation/19.0/developer/reference/upgrades/upgrade_scripts.html),
  consultée le 15 septembre 2026. Les conventions particulières de la série
  restent à vérifier dans ses sources ; aucun moteur de migration n'est exécuté.
- Aucun résultat ne garantit à lui seul les droits, la comptabilité, le rendu PDF
  ou le comportement métier. Ils appartiennent aux critères et parcours de QA.

Validation synthétique : `python3 -m unittest discover -s tests/pilotage -p
 'test_odoo_delivery_guard.py' -v`. Elle couvre notamment imports non suivis,
fichiers manquants, schéma sans version, migrations hors plage/non exécutées,
build rouge, preuve altérée, ancienne version installée et lecture non sourcée.
