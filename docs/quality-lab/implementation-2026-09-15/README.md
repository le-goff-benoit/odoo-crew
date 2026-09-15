# Qualification d'implémentation Python — 15 septembre 2026

## Protocole figé avant appels

Huit appels natifs maximum, aucun retry caché ; un appel à la fois ici pour partager
le plafond global de deux avec la comparaison des profils. Effort demandé medium,
modèles Codex Astra/Terra et Claude Opus/Sonnet, aucune substitution. Cas I01 puis
I02, ordre des modèles inversé sur I02. I02 est la contre-épreuve inédite, figée
avant toute réponse. Les deux cas et le rôle développeur Python sont identiques
entre modèles. Ce rôle est adapté au domaine hors Odoo ; aucun /odoo-new simulé.

- I01 : calcul des candidats prêts dans un graphe, preuves transitives et verrous.
- I02 : quotas par fournisseur/fenêtre, tri temporel, inconnus, données invalides.

L'agent modifie de vrais fichiers, ajoute des tests, les exécute, et enregistre
un reçu `odoo-evidence/1` lié aux sources et au log. Après sa sortie, le principal
reçoit avec un oracle indépendant hors du montage de l'agent et vérifie le reçu.
La réception est un sous-processus isolé, sans accès client, Docker ou credentials.

Calibration avant appel : références positives I01/I02 passent ; cinq mutations
(verrous oubliés, dépendances ignorées, résultat vide, seuil TTL, ordre temporel)
sont refusées. Les trois tests unitaires passent sans appel de modèle.
Les empreintes de tous les cas, oracle, corrigé et protocole sont dans
[frozen-hashes.json](frozen-hashes.json). Le runner en prend aussi une copie immuable
par campagne avant le premier appel.

Commande explicite (jamais appelée par CI) :

```bash
python3 scripts/odoo_bench_implementation.py --run \
  --output /tmp/implementation-native-20260915 --pack "$PWD"
```

## Décision prévue

Tout échec interdit l'adoption. Mesurer le temps jusqu'à réception, le nombre
réel d'outils, les jetons/cache et modèle observés lorsqu'ils sont retournés.
Une sortie rejetée n'est pas corrigée silencieusement ; si aucune reprise n'est
faite, son temps de reprise principal reste inconnu, pas zéro. Même huit réussites
sur ces deux exercices ne qualifient ni le développement Odoo ni un routage
automatique : les modèles candidats restent expérimentaux.

## Résultats

Huit appels, huit réceptions acceptées. Aucun retry, aucune correction des sorties des agents.

| Cas | Modèle demandé | Modèle observé | Secondes jusqu’à réception automatisée | Outils | Tests exécutés |
|---|---|---|---:|---:|---:|
| [I01](trials/I01-codex-principal/result.json) | gpt-6-astra | non retourné | 100.017 | 8 | 11 |
| [I01](trials/I01-codex-candidate/result.json) | gpt-5.6-terra | non retourné | 76.399 | 7 | 9 |
| [I01](trials/I01-claude-candidate/result.json) | sonnet | claude-sonnet-5 | 50.118 | 13 | 22 |
| [I01](trials/I01-claude-principal/result.json) | opus | claude-opus-5 | 110.382 | 9 | 43 |
| [I02](trials/I02-claude-principal/result.json) | opus | claude-opus-5 | 105.793 | 7 | 48 |
| [I02](trials/I02-claude-candidate/result.json) | sonnet | claude-sonnet-5 | 63.039 | 9 | 23 |
| [I02](trials/I02-codex-candidate/result.json) | gpt-5.6-terra | non retourné | 66.757 | 6 | 4 |
| [I02](trials/I02-codex-principal/result.json) | gpt-6-astra | non retourné | 108.311 | 8 | 9 |

Les jetons, cache et coûts éventuellement retournés sont conservés dans [results.json](results.json).
Le modèle effectif et l’effort effectif ne sont pas inventés : Codex ne retourne pas le modèle dans ce flux ; l’effort effectif reste inconnu pour les deux fournisseurs.
Les temps additionnent l’appel et la réception automatique (~0,1 s), sans file d’attente ni temps de lecture humaine. Aucune reprise de code par le principal n’a été nécessaire.
Le nombre de méthodes de test ne mesure pas la couverture : certaines regroupent leurs cas par sous-tests.

### Correction de la réception, sans changement du contrat

Une relecture d’intégration a relevé que la conservation de `test_public.py` et du contrat, déjà prescrite, n’était pas contrôlée automatiquement. Le runner et un test de mutation ont été renforcés ; les huit archives ont ensuite été comparées aux fixtures figées : toutes inchangées. La commande native de création du reçu a également été retrouvée dans les huit flux. Aucun appel supplémentaire, aucune modification de l’oracle métier ou des sorties.

### Décision

Les candidats demandés sont plus rapides sur ces deux tâches locales : Terra environ 24 % puis 38 % ; Sonnet environ 55 % puis 40 %. Cela justifie de poursuivre les essais en tâche Python locale bornée et réception indépendante. **Ils restent expérimentaux ; aucun routage automatique ni qualification de développement Odoo.**
Les oracles couvrent des graphes courts et des quotas représentés par des valeurs JSON usuelles ; ils ne constituent ni un test de charge, ni une preuve pour les droits Odoo, les factures, les migrations ou la livraison client.
Les sources, tests et reçus produits sont archivés par essai. Les flux natifs complets restent dans le dossier local `/tmp/implementation-native-20260915`, leurs empreintes figurent dans les résultats.
