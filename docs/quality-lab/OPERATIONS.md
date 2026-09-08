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
