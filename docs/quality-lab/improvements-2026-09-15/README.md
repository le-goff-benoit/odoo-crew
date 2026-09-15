# Améliorations livrées — 15 septembre 2026

Référence du dispositif avant intervention : `4c6738c`. Les sources clients
ont été consultées localement en lecture seule ; aucune donnée client ne figure
dans ce dossier. Le [suivi](../../IMPROVEMENTS.md) relie chaque levier à son contrat.

| Levier | Mise en place | Preuve et portée |
|---|---|---|
| Livrer le bon code et constater le déploiement | Garde du commit, imports, versions, plage de migration, build prescrit, versions avant/après et effets relus | [Contrat](../../DELIVERY_GUARD.md), tests synthétiques ; aucune collecte distante ni déploiement automatique |
| Réfuter tôt les mauvaises hypothèses | Cohortes courante/historique/contradictoire dans analyste et plan | Consignes intégrées ; pas de gain global client chiffré |
| QA liée au parcours réel | État, acteur, canal et contre-exemple ; résultats indépendants du code testé | [Stock, PDF18/19 et Chrome](../workflows-2026-09-15/README.md) |
| Préserver ce qui est déjà reçu | Plan/flow/intention, reprise et conflit réels sur mini-release | [W05](../workflows-2026-09-15/mini-release/result.json), graphe minimal synthétique |
| Réduire le contexte sans couper une exception | Briefing daté, sections complètes, décisions obligatoires et index | [Sélection](../../CONTEXT.md), [dates](../briefing-recency-2026-09-15/README.md) |
| Profils plus courts | Entrées orchestration/QA, procédures conditionnelles, communication commune | [Comparaison native](../profiles-2026-09-15/README.md), qualité et latence distinguées |
| Choisir les modèles sur preuves | Deux tâches d'implémentation avec outils et reçu, deux fournisseurs | [Essais](../implementation-2026-09-15/README.md), Python local ; modèles toujours expérimentaux pour Odoo |

## Relecture indépendante et correction

Deux défauts du premier candidat ont été reproduits :

1. Une migration déjà présente au commit de base, mais dans la plage de versions
   réellement exécutée, échappait à l'exigence de preuve. Le contrat conserve
   maintenant `expected_migrations` indépendamment de `changed_migrations`.
2. Une exception sous titre numéroté pouvait être séparée de sa règle. La sélection
   normalise numérotation décimale/romaine/lettres et emphase avant de regrouper.

Un défaut CLI supplémentaire est corrigé : `module/` et `./module` désignent
maintenant le même périmètre. [Avant](review-before.log) → [après](review-after.log).
Les régressions vivent dans les tests du garde et du contexte, sur répertoires
synthétiques temporaires. La vérification porte aussi sur un budget insuffisant,
la provenance des sections et les décisions qui ne doivent pas être tronquées.

## Interpréter les résultats

Les calibrations Odoo éprouvent les défauts injectés, pas toutes les variantes
métier ni toutes les séries. Les tests de modèles distinguent retour, réception,
incidents et reprises. Une lecture plus courte ne signifie pas une latence plus
faible ; une réussite sur outil Python n'autorise pas le routage automatique d'un
agent de développement Odoo. L'orchestrateur conserve son modèle principal.

Les comparaisons et les archives sont figées avant leurs appels ; la CI ne fait
aucun appel payant. Les snapshots complets des homes/outils restent locaux ; seules
les preuves synthétiques nécessaires sont publiées.

## Validation et installation

- Suite complète : **355 tests**, un contrôle de parsing TOML ignoré sur Python
  3.10 (`tomllib` absent), exercé par la matrice GitHub Python 3.12.
- Graphe : 59 nœuds, 129 arêtes ; validation réussie.
- Génération isolée puis active : **35 fichiers**, deux blocs d'aiguillage et
  pointeur personnel conformes sur Claude/Codex. Skills orchestration/QA validés.
- **16 appels natifs**, aucun appel de réserve utilisé : huit réceptions documentaires
  et huit implémentations Python. Candidats légers toujours expérimentaux.
- Témoins et mutations Odoo 18/19 : [résultats séparés](../workflows-2026-09-15/README.md).

Les corrections d'intégration du garde et du contexte ont leurs tests propres
après les snapshots natifs ; les snapshots historiques ne sont pas réécrits.

Bilan des lectures documentaires natives : **−48,83 % de caractères retournés**
(profils, références et pièces ensemble), mais candidat plus lent dans les quatre
paires. Le profil compact est reçu pour le mode documentaire ; l'orchestration
raccourcie conserve ses invariants après relecture, sans qualification native
complète de son exécution dans cette campagne.
