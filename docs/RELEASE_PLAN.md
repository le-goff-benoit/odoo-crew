# Préparer, exécuter, reprendre, clôturer

`/odoo-new demande` conserve sa chaîne directe. Pour préparer plusieurs demandes :
`/odoo-plan`, puis `/odoo-start`. Les commandes courtes `/new` et `/start` ne sont
pas installées : le préfixe évite les collisions avec les outils hôtes.

Définition minimale, stockée dans la release :

```json
{"schema":1,"tasks":[{"id":"T01","title":"Résultat métier",
 "request":"changelog/RELEASE/demande.md","route":"module","risk":"normal",
 "acceptance":["L’acteur obtient le résultat convenu à la borne incluse"],
 "scopes":["module_custom"],"depends_on":[]}]}
```

Les périmètres peuvent désigner un futur module. Pour Studio, utiliser le dossier
versionné du pack et de ses scénarios. Ne pas employer tout le projet comme
périmètre : le plan et les journaux évoluent pendant la tâche.

```bash
python3 scripts/odoo_plan.py init PROJET/changelog/RELEASE --file definition.json
python3 scripts/odoo_plan.py status PROJET/changelog/RELEASE
python3 scripts/odoo_plan.py start PROJET/changelog/RELEASE --task T01
# Piloter le flow rendu avec odoo_flow.py, appliquer les rôles et la QA.
python3 scripts/odoo_plan.py finish PROJET/changelog/RELEASE --task T01 \
  --proof changelog/RELEASE/preuves/T01.json \
  --acceptance changelog/RELEASE/reception-T01.md \
  --memory changelog/RELEASE/consolidation-T01.md
```

Les chemins des preuves sont relatifs au projet. `plan.json` est versionné ; les
étapes du flow sont locales. Une réception durable valide survit à un checkout
synchronisé si le code et les preuves sont présents et vérifiables. Les anciennes
preuves contenant des chemins absolus d’un autre poste demandent une nouvelle
vérification locale : le plan ne les transforme pas silencieusement en vert.

`reopen --task T01 --reason "décision D-03 remplace D-02"` garde l’historique.
`defer --task T01 --reason "décision de périmètre et sa source"` retire la tâche
de la livraison, mais ne satisfait pas les dépendances d’une autre tâche.
Ne pas différer un critère obligatoire pour faire passer la clôture.

La disponibilité tient compte des dépendances et des périmètres des tâches actives.
Les étapes du graphe conservent leurs propres verrous : certains travaux restent
sérialisés. Le plan n’est pas un ordonnanceur distribué ni une allocation automatique
de machines. Les ressources partagées entre projets se déclarent via
`.odoo-agents/resources.json`.

À la clôture, préparer les versions **avant** la recette :

```bash
python3 scripts/odoo_release_guard.py prepare PROJET/changelog/RELEASE --module module_custom
```

Le manifeste déjà différent de la base de release conserve sa version. La préparation
est idempotente grâce à `versions.json`. Produire ensuite les preuves sur l’état final,
`doc.md` métier, `consolidation.md`, les autres livrables et le sceau :

```bash
python3 scripts/odoo_release_guard.py seal PROJET/changelog/RELEASE \
  --scope module_custom --proof changelog/RELEASE/preuves/recette.json
python3 scripts/odoo-release.sh close PROJET/changelog/RELEASE
```

Le sceau refuse code, documents ou preuves modifiés après contrôle. La fermeture
retire ensuite le marqueur d’ouverture ; le sceau conserve l’empreinte du README
final fermé. DOCX/PDF et communication ne sont pas des prérequis : ils sont générés
sur demande pour la release identifiée, sans refaire le développement ni déployer.

`controls.json` liste les contrôles attendus et leurs preuves, par exemple :

```json
{"schema":1,"risk":"high","route":"module","controls":[
 {"id":"installation","status":"passed","proof":"changelog/RELEASE/preuves/recette.json"},
 {"id":"update","status":"passed","proof":"changelog/RELEASE/preuves/recette.json"},
 {"id":"tests","status":"passed","proof":"changelog/RELEASE/preuves/recette.json"},
 {"id":"client_copy","status":"passed","proof":"changelog/RELEASE/preuves/copie.json"},
 {"id":"browser","status":"not_applicable","reason":"Aucun écran/parcours modifié"},
 {"id":"uninstall","status":"passed","proof":"changelog/RELEASE/preuves/recette.json"}]}
```

Les états rouge, absent, incomplet ou une dispense de copie en risque élevé
bloquent le sceau. En voie module, le contrôle `tests` doit pointer vers une preuve
Odoo avec module et nombre de tests positif. En voie Studio, les contrôles
installation/update/uninstall peuvent être non applicables avec justification ;
les scénarios RPC et la copie restent obligatoires. Un `passed` exige une preuve
vérifiée. La relecture du log et de ses critères est nécessaire : une commande
réussie ne prouve pas à elle seule toutes les affirmations du déclarant.


## Nouvelle demande dans une release préparée

Conserver le plan et ses réceptions ; ajouter les nouvelles tâches avec un fichier
`{"schema": 1, "tasks": [...]}` de même format que la définition initiale :

```bash
python3 ~/.odoo19-agents/scripts/odoo_plan.py add changelog/<release> --file nouvelles-demandes.json
```

Les identifiants existants ne sont pas remplaçables. Les dépendances peuvent viser
les tâches existantes ou les nouvelles ; cycles, références inconnues et état
validé importé sont refusés. Une modification du contrat d'une tâche existante
exige une réconciliation explicite et une nouvelle réception. Un module futur ou
encore vide peut démarrer ; sa preuve de réception doit couvrir des fichiers réels.
