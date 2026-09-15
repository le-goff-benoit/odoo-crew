# Profils QA compacts — qualification documentaire native

Campagne du 15 septembre 2026, selon le [protocole figé](protocol.md).
Les huit résultats ont reçu une revue sémantique ; le détail et les limites suivent.

## Comparaison

Référence `4c6738c60c959fd1ceac7d24d6949d96909b6ab2` contre copie figée des
sources courantes. Les profils de chaque version sont générés par leur propre
`build.sh`, puis lus depuis `.codex/skills/odoo-tester/SKILL.md` ou
`.claude/agents/odoo-tester.md` dans un environnement isolé.

Deux dossiers synthétiques sont figés avant le premier appel, avec leurs oracles
hors du sandbox :

- **Positif** : seuil inclusif, exclusion des prêts prolongés, non-régression de
  l’autre société, cinq observations locales et contribution mémoire conservée.
- **Holdout négatif** : exception perdue dans le contrat, preuve incomplète,
  déploiement affirmé sans preuve et contribution indépendante effacée.

Huit appels au maximum, séquentiels dans cette campagne : Astra et Opus, effort
medium demandé, mêmes pièces et mêmes outils avant/après. Ordre référence puis
candidat pour Codex ; candidat puis référence pour Claude. Aucun sous-agent, aucun
appel dans les tests ou la génération, aucun test Odoo dans ce mandat documentaire.
Les résultats sont des fichiers isolés ; le contrôleur vérifie aussi que les
pièces n’ont pas changé.

## Mesures et réception

Un lecteur instrumenté restitue intégralement le profil, les références demandées
et les pièces. Son journal donne chemins, empreintes, appels et caractères
retournés. Les événements natifs sont relus pour vérifier que leurs sorties
contiennent ces textes sans troncature, à la suppression de retours ligne terminaux
près. Cela mesure du texte rendu disponible, pas les caractères internes ni les
tokens réellement retenus par le modèle. Les instructions automatiques et schémas
d’outils du fournisseur ne sont pas inclus dans ce comptage ; l’usage natif est
conservé séparément lorsqu’il est fourni.

L’oracle automatique vérifie les conclusions structurées, les observations
préservées, les trois axes argumentés et l’exactitude des citations. Les témoins
positifs et leurs mutations critiques sont testés hors ligne. Une réception
sémantique distincte confronte ensuite chaque argument aux pièces ; la présence de
mots attendus ne suffit pas. Les cas ne servent pas à réécrire les profils pendant
les essais.

La durée du retour natif est mesurée. Le délai retour→réception inclut l’attente du
relecteur et n’est pas une mesure causale du modèle ; la durée propre du jugement
n’est pas instrumentée. Les résultats sans réception ne sont pas qualifiés de
livraison. Une répétition par cas ne permet pas de conclure à un gain de latence.

## Résultat reçu

**Profil compact adopté pour la réception documentaire sur les cas éprouvés.**
Les quatre candidats et les quatre références satisfont l’oracle et la réception
sémantique : huit résultats reçus, aucun incident, aucune relance ni correction.
Chaque positif est accepté et chaque dossier fautif est refusé, avec maintien des
deux succès locaux du holdout. Cette réception ne qualifie pas le développement
Odoo ni toute l’orchestration.

Le texte explicite retourné par le lecteur passe de **138 866 à 71 063 caractères** sur
les quatre paires (**−48.8 %**), pièces comprises. Tous les textes lus ont été
retrouvés intégralement dans les événements natifs, hors espaces terminaux.
Le profil d’entrée seul passe de 25 202 à 10 413 caractères pour Codex et de
25 179 à 10 390 pour Claude. Les références chargées s’ajoutent dans le tableau :
la réduction de l’entrée seule ne décrit pas toute la lecture.

**Aucun gain de latence démontré : le candidat est plus lent dans les quatre
paires.** Les volumes de jetons varient également selon les outils, sorties et
caches ; la réduction des caractères explicites ne garantit donc ni économie de
jetons ni baisse du coût. Aucune moyenne de vitesse ne compense un défaut critique.

| Cas | Fournisseur | Profil | Entrée (car.) | Références (car.) | Total avec pièces (car.) | Lectures | Retour (s) |
|---|---|---|---:|---:|---:|---:|---:|
| positive | codex | reference | 25202 | 3116 | 30525 | 7 | 63.617 |
| positive | codex | candidate | 10413 | 3393 | 16013 | 7 | 69.771 |
| positive | claude | reference | 25179 | 11874 | 39260 | 7 | 77.677 |
| positive | claude | candidate | 10390 | 11154 | 23751 | 8 | 132.354 |
| holdout | codex | reference | 25202 | 3116 | 30173 | 7 | 64.915 |
| holdout | codex | candidate | 10413 | 3393 | 15661 | 7 | 69.169 |
| holdout | claude | reference | 25179 | 11874 | 38908 | 7 | 72.869 |
| holdout | claude | candidate | 10390 | 3393 | 15638 | 7 | 77.749 |

### Usage retourné par les fournisseurs

Les colonnes sont des champs natifs, non une estimation de caractères en tokens.
Codex `input_tokens` contient le compteur d’entrée du fournisseur avec son champ
cache séparé ; Claude distingue nouvelles entrées, création et lecture du cache.
Ne pas comparer ces colonnes entre fournisseurs comme une métrique normalisée.

| Cas | Fournisseur | Profil | Input natif | Cache créé | Cache lu | Output natif |
|---|---|---|---:|---:|---:|---:|
| positive | codex | reference | 86644 | 0 | 60544 | 1718 |
| positive | codex | candidate | 73993 | 0 | 51968 | 1863 |
| positive | claude | candidate | 22 | 30885 | 260295 | 11037 |
| positive | claude | reference | 18 | 22765 | 243415 | 6220 |
| holdout | codex | reference | 86506 | 0 | 60416 | 1769 |
| holdout | codex | candidate | 92554 | 0 | 52864 | 1877 |
| holdout | claude | candidate | 12 | 12906 | 120794 | 6518 |
| holdout | claude | reference | 14 | 23552 | 179116 | 5869 |

Le modèle observé de Claude est `claude-opus-5` pour les quatre essais ; Codex
ne retourne pas son modèle effectif dans ces événements, seul `gpt-6-astra`
demandé est attesté par la commande. L’effort effectif n’est retourné par aucun
des deux transports ; `medium` est le réglage demandé, sans repli.

Deux réserves non critiques restent dans le holdout Opus candidat : une phrase
qualifie trois critères de non attestés alors que C2 est partiel, correctement
détaillé ailleurs ; une allusion à l’arbitrage du demandeur est superflue pour
cette erreur claire de transcription, alors que le rapport propose aussi la
correction fidèle à la demande. Le refus global, les observations préservées et
les quatre défauts restent correctement reçus. Aucun profil n’a été retouché
pour faire disparaître ces réserves.

### Preuves conservées

- [Résultats et réceptions](results-native/results-reviewed.json),
  [revues sémantiques](results-native/reviews.json),
  [empreintes figées avant lancement](results-native/frozen.json).
- Chaque dossier d’essai contient résultat, réception JSON, événements natifs,
  lectures instrumentées et contrôle d’intégralité des sorties.
- `sources/` contient uniquement les profils et références effectivement lus ;
  `frozen-corpus/` conserve les pièces et oracles exacts, restés hors du sandbox.
- `runner-used.py` conserve la version exécutée. Le runner courant automatise
  aussi le contrôle des sorties natives effectué après cette campagne et refuse
  les liens symboliques dans les sources retenues du snapshot ; ces durcissements
  sont éprouvés hors ligne, sans nouvel appel modèle.

Les packs complets, homes et caches des CLI ont été déplacés vers une archive
privée hors dépôt. Le dossier publiable est limité aux preuves synthétiques.
La revue statique de l’orchestration compacte et de ses procédures n’a pas relevé
de perte critique ; elle reste distincte de ces huit essais de réception QA.

## Reproduire

Choisir un **nouveau dossier privé hors dépôt** pour les snapshots, homes natifs et
traces complètes. Les authentifications sont laissées aux CLI ; aucun secret n’est
copié ni lu par le runner.

```bash
cd ~/.odoo19-agents
python3 -m unittest tests.laboratoire.test_bench_profiles -v
python3 scripts/odoo_bench_profiles.py --run \
  --baseline 4c6738c60c959fd1ceac7d24d6949d96909b6ab2 \
  --candidate ~/.odoo19-agents \
  --corpus ~/.odoo19-agents/benchmarks/qualification/profiles \
  --output /tmp/profils-qualification-neuve --timeout 600
```

Les résultats complets contiennent des duplications du référentiel et des fichiers
techniques des CLI : ils ne sont pas destinés à être publiés tels quels. Ne publier
que les dossiers synthétiques, empreintes, résultats, lectures et textes de profils
ou références effectivement lus. Ce banc ne qualifie ni le développement Odoo,
ni une release, ni l’orchestration native complète.
