# Exploiter et adapter le laboratoire

Le laboratoire sépare quatre mesures : réponse utile, code exécutable, verdict
QA fiable et fidélité aux décisions client. Un succès sur une dimension ne
remplace pas les autres. Chaque amélioration doit nommer le défaut qu'elle vise,
son cas de reproduction, les fichiers changés et les preuves obtenues.

## Campagnes de directives

```bash
python3 scripts/odoo_bench.py plan \
  --config benchmarks/configs/pilot-local.example.json \
  --corpus benchmarks/cases-v2 --cases B10 B11 \
  --variants benchmarks/variants/comparison.json --repetitions 2 \
  --output /tmp/odoo-quality-runs
python3 scripts/odoo_bench.py run /tmp/odoo-quality-runs/IDENTIFIANT
python3 scripts/odoo_bench.py status /tmp/odoo-quality-runs/IDENTIFIANT
```

Trois variantes : référence, correction ciblée de fidélité, rôle compact.
Le rôle compact change aussi la structure et le contenu : un gain éventuel
ne s'attribue pas au seul nombre de mots.
Ordre ABC puis CBA par outil ; ce contrebalancement n'est pas une randomisation
complète. Modèle et effort restent constants pour comparer les directives.
Dossier, consignes et critères sont figés avec leurs empreintes dans chaque
essai. Aucun critère n'entre dans le paquet du générateur. B11 était réservé
avant la campagne initiale ; une fois ses résultats étudiés, créer un nouveau
cas réservé pour l'itération suivante.

`state.json`, `report.md`, les réponses et les journaux rendent l'avancement
observable. `stop` interrompt, `resume` reprend seulement les essais encore en
attente ; un appel interrompu reste un incident, sans relance cachée. Garder les
incidents de transport séparés des échecs métier. Les timings incluent le CLI,
le réseau et le fournisseur ; ils ne mesurent pas seulement le raisonnement.
Les efforts demandés de deux fournisseurs ne sont pas une échelle commune.

## Correction masquée et arbitrage

```bash
python3 scripts/odoo_bench_judge.py /tmp/odoo-quality-runs/IDENTIFIANT \
  --output /tmp/odoo-quality-judge \
  --calibration benchmarks/judge/calibration.json
```

Le correcteur reçoit dossier, grille et réponses sous identités opaques. Il ne
voit ni modèle, ni variante, ni consignes de génération. Son contexte est neuf
et sans outils. Une calibration contient une passation correcte puis sa version
contradictoire qui clôt abusivement les questions : si cette distinction échoue,
la correction s'arrête. Chaque citation doit exister dans la réponse. Cette
validation mécanique n'atteste pas la justesse de l'interprétation.

Le correcteur est lui-même un LLM : relire les échecs critiques et les désaccords,
conserver son avis initial et l'arbitrage séparément. Un modèle peut reconnaître
un style malgré le masquage. Une réponse qui ignore sa rubrique ne doit pas être
récompensée pour sa longueur. Une absence de dimension reste « non mesurée ».
La promotion des instructions n'est jamais automatique.

## Code et oracle Odoo

B12 fournit un contrat entièrement arbitré et un squelette de modèle ; le LLM
renvoie un fichier Python dans un objet JSON. Le code produit est conservé sans
correction. Cette phase est une génération sur dossier, pas l'exécution native
d'un agent développeur avec ses outils. L'oracle indépendant est ensuite exécuté :

```bash
python3 scripts/odoo_bench_runtime.py --output /tmp/odoo-oracle-reference --mutations
python3 scripts/odoo_bench_runtime.py --output /tmp/odoo-oracle-candidates \
  --candidate essai=/tmp/candidat.py
python3 scripts/odoo_bench_runtime.py --output /tmp/odoo-oracle-studio --studio
```

Prérequis : Docker, images locales `odoo-qa:19.0` et `postgres:16` ; option Studio :
sources Enterprise autorisées dans `~/odoo-sources/19.0-enterprise`. Le runner
crée un réseau interne, un PostgreSQL propre et un gabarit pour la campagne.
Chaque candidat reçoit un clone séparé ; les conteneurs et le réseau sont
nettoyés. Aucun port hôte, aucune base client. Les sources, empreintes, logs et
l'identité de l'image sont conservés. `quality_oracle` reçoit une copie du
transport de packs au lancement : utiliser ce runner pour préparer les addons.

Les trois mutations étalonnent la sensibilité aux défauts choisis. Elles ne
prouvent pas une couverture exhaustive. Le temps de création du gabarit doit
être compté séparément du temps d'un essai. Tester une nouvelle série exige son
image, ses sources, son oracle adapté et un nouveau contrat ; ne pas extrapoler
les résultats 19.0 aux autres séries.

## De l'analyse à une modification adoptée

1. Transformer un axe du document en hypothèse falsifiable et cas de reproduction.
2. Figer la référence et la rubrique ; préserver un cas inédit.
3. Modifier une dimension des directives, ou un défaut outillé identifiable.
4. Rejouer tests de contrat, oracle et comparaison concernés.
5. Consigner : adopté, expérimental, rejeté ou non mesuré, avec preuve et limite.
6. Reconstruire les profils dans un répertoire isolé, puis intégrer la version
   retenue. Garder l'ancienne version pour revenir en arrière.

Une batterie courte sert à chaque changement ; une campagne plus large précède
une livraison du dispositif. Adapter les cas aux métiers visés sans y copier
secrets, tickets identifiants ou données client. Le mécanisme améliore les
instructions et les outils ; il ne réentraîne pas les poids des modèles.

Pour matérialiser et évaluer directement des campagnes B12 terminées :

```bash
python3 scripts/odoo_bench_development.py /tmp/campagne-effort-A /tmp/campagne-effort-B \
  --output /tmp/odoo-oracle-developpement
```

Le JSON et la syntaxe sont vérifiés sans exécuter le code sur l'hôte ; une réponse
invalide échoue sans réparation. Les résultats de l'oracle reviennent dans les
rapports des générations avec les empreintes des réponses et des logs. Une revue
du code reste requise : ce banc vise des erreurs de développement, pas un modèle
malveillant qui chercherait activement à falsifier le processus de test.

## GitHub

`.github/workflows/quality-lab.yml` lance graphe, tests de contrat et génération
isolée sur Python 3.10/3.12 à chaque push/PR ou lancement manuel. Aucune clé ni
requête LLM n'est nécessaire. GitHub affiche les étapes et le verdict du job.
Les campagnes payantes et les oracles Odoo/Enterprise restent des lancements
explicites dans un environnement équipé ; leur suivi est assuré par les états
et rapports du laboratoire. Le workflow est livré dans le dépôt ; son exécution
sur GitHub ne peut être attestée qu'après publication et retour du service.

Le correcteur accepte `--resume` : les lots déjà corrigés sont relus et vérifiés
sans nouvel appel au fournisseur. Une réponse, une grille ou une configuration
modifiée invalide cette reprise. Un lot commencé mais incomplet reste un incident
conservé ; utiliser un nouveau dossier pour une nouvelle tentative explicite.

L'itération de développement conserve trois états des instructions : référence,
`dev_guard` (règle générale) et `dev_guard_v2` (ordre d'application des défauts
explicitement expliqué). B12 mesure la correction et la non-régression ; B13
sert au transfert vers les notes de frais. Le runner accepte `--case B13
--fixtures benchmarks/odoo-expense --implementation quality_case/models/expense.py`.
Le [rapport de l'expérience](experiment-2026-09-08/README.md) conserve aussi les
échecs des variantes et les corrections de l'oracle. Un échec du modèle ne doit
jamais être effacé en remplaçant son code par une version corrigée manuellement.


## Parcours natifs et adoption des profils

`/odoo-improve` pilote la boucle jusqu'à la décision d'adoption. Les résultats
seuls ne constituent pas une amélioration des agents. Modifier les sources
canoniques, reconstruire les profils, exécuter un contre-exemple puis un cas
inédit, conserver les échecs et installer seulement les changements justifiés.

```bash
python3 scripts/odoo_bench_native.py run --output /tmp/native-campaign \
  --cases N01 N02 N03 N04 --reference <commit-avant> --candidate <commit-apres> \
  --providers codex claude --timeout 900 --workers 2
python3 scripts/odoo_bench_native.py status --output /tmp/native-campaign
```

Ce runner utilise les CLI natives et les skills générés dans un home isolé par
bubblewrap. Les sources Odoo restent en lecture seule ; seul le projet synthétique
est modifiable. Le pont autorise lint (`/bridge/labctl lint MODULE`, Ruff dans l’image QA),
QA, mise à jour de la copie et scripts ORM dans
les conteneurs du banc. Aucun socket Docker ni dossier client n'est transmis au
modèle. Les cas, correcteurs et rapports du dépôt sont masqués pendant ses appels.
Studio emploie un proxy HTTP de boucle locale vers sa seule copie synthétique.
Pour les modules, `labctl rpc FICHIER.json` ouvre un serveur temporaire neuf et
appelle le vrai XML-RPC sous l'administrateur synthétique. Le fichier doit porter
exactement `model` (celui du cas), `method` (publique), `args` (liste), `kwargs`
(objet) ; aucune URL, base ou identité externe n'est acceptée. Exemple :

```json
{"model":"lab.rental","method":"create","args":[{"name":"Essai RPC","days":-1}],"kwargs":{}}
```

Un Fault est conservé intégralement et renvoie le code **1**. Pour un scénario
négatif, vérifier son message et les postconditions ; ce code seul n'est pas un
verdict de test. Le service est arrêté après l'appel ; les commandes restent
sérialisées et le module est synchronisé avant chaque commande. Ce transport
ne prouve pas le rendu navigateur ni les droits d'un utilisateur ordinaire.
L'oracle SQL reste séparé de la preuve RPC. En 19.0, le message enregistré dans
`ir.model.constraint` peut primer sur le texte Python : la [contre-épreuve RPC](consolidation-2026-09-09/README.md)
conserve l'essai de mutation inopérant puis sa correction.

Par défaut, les rôles sont appliqués par l'orchestrateur et la délégation est
désactivée. Le mode expérimental `--delegate-claude` expose les sous-agents
Claude et ajoute un relevé `delegation` à chaque tour : identifiants, rôle,
progression observée, notification de fin et résumé natif du fournisseur.
Un événement `local_bash` ne compte pas comme sous-agent. Codex reste sans
délégation dans ce runner ; aucune extrapolation entre moteurs.

```bash
python3 scripts/odoo_bench_native.py run --output /tmp/native-delegation \
  --cases N04 --reference <commit-avant> --candidate <commit-apres> \
  --providers claude --timeout 900 --workers 1 --delegate-claude
```

Comme en mode normal, cette commande exécute les **deux révisions** par cas.
`--workers` règle le nombre de campagnes simultanées, pas le nombre d'enfants
d'un orchestrateur. Les profils bornent celui-ci à trois. Le compteur atteste
les événements reçus ; il ne juge pas la qualité de la passation, ne mesure pas
le chevauchement et ne suffit pas à annoncer un gain de vitesse. Le pont Odoo
reste sérialisé. Pour mesurer le chevauchement, conserver une chronologie
horodatée des événements comme dans l'[essai de délégation et reprise](delegation-2026-09-09/README.md).

Les états distinguent préparation, exécution, résultat et incident. Ce runner
natif ne possède pas encore de reprise automatique : conserver le dossier d'un
essai interrompu et relancer dans un nouveau dossier. Un timeout ou un défaut
d'archivage n'est pas une erreur métier du modèle. Les appels sont payants et
exigent les CLI authentifiées localement ; GitHub CI ne les lance pas.

N01 teste une nouvelle décision dans un contexte neuf, N02 une reprise et le gel
des dossiers validés, N03 un pack Studio, N04 les contraintes SQL. Les oracles
sont étalonnés avec une réalisation correcte et une mutation fautive. Ajouter
un métier exige son contrat, ses données synthétiques, sa rubrique et son oracle ;
ne pas réutiliser les attendus produits par l'agent comme unique correcteur.
