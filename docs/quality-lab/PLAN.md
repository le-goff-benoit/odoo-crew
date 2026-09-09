# Plan d’exécution — laboratoire qualité Odoo

Référence initiale : `9541bba`. Branche : `feat/quality-lab`.
Conception : analyse du bureau, sections 10, 13–16 (copie locale ignorée par Git).
Périmètre initial : pilote court L00–L04. **Poursuite L05–L09 autorisée par
l’utilisateur après le pilote**, avec arbitrages autonomes et mesure des gains.
Les essais restent isolés des projets client ; les corrections validées sont désormais intégrées aux profils actifs.

## Critère directeur

Évaluer séparément réponses, développement, QA et intelligence client.
Un échec critique ne se compense pas par une moyenne ni par un gain de vitesse.
Un rapport sans jugement indépendant reste « à évaluer », jamais « réussi ».

## Suivi

| ID | Travail | Dépendance | État | Preuve / prochaine action |
|---|---|---|---|---|
| L00 | Figer la référence et inventorier les outils | — | validé | Worktree dédié ; 23 tests initiaux verts ; Codex 0.153.4, Claude 2.1.263, Python 3.10.12 |
| L01 | Génération isolée et vérification complète (R02) | L00 | validé | `build.sh --output-root`, contrôle des sorties sans régénération |
| L02 | Corpus synthétique et rubriques indépendantes | L00 | validé pour le pilote | Dix cas déclarés, trois premiers exécutables |
| L03 | Exécuteur avec état persistant, arrêt, reprise et rapport | L01 | validé par tests de contrat | Résultat d’exécution distinct du jugement qualité |
| L04 | Premier pilote réel | L02, L03 | terminé | Accord utilisateur : 3 cas × 2 outils, 600 s maximum par exécution |
| L05 | Corriger les pertes du briefing (M01–M03) | L00 | tests verts | Tests rouges puis verts, ancienne référence préservée |
| L06 | Fiabiliser les verdicts QA, preuves et protections (R03–R11) | L00 | validé sur le périmètre documenté | Cas de contrat isolés, défauts distincts |
| L07 | Organisation des tâches, mémoire et documentation | L05, L06 | livré avec options et limites explicites | Critères sections 10, 13, 14, compatibles avec l’existant |
| L08 | Variantes et comparaison contrôlée des directives | L04, L06 | terminé : 34 générations + 6 corrections | Évaluation indépendante, corpus réservé |
| L09 | Validation intégrée et livraison réversible | L07, L08 | livré et vérifié | `de0000e` publié sur main ; profils actifs conformes ; CI Python 3.10/3.12 verte |

## Pilote autorisé

Six exécutions, trois exercices sur chaque outil, une répétition.
Réglages lus localement : Codex `gpt-6-astra` / `high`, Claude `opus` / `medium`.
Le modèle réellement retourné sera relevé séparément ; un alias n’est pas une version exacte.
Cette première série vérifie le laboratoire et établit des observations exploratoires.
Elle ne prouve pas une supériorité statistique ni une amélioration générale.

## Journal du chantier

- 2026-09-08 : lancement autorisé après la tâche RubixComm ; travail isolé depuis `9541bba`.
- Validation initiale : graphe 52 nœuds / 115 arêtes ; 23 tests, aucun échec.
- Premier prérequis : génération isolée, car le build initial modifie les profils actifs.

- Arbitrage : les rôles restent inchangés pendant la mesure de référence. Les corrections métier et les variantes attendent les observations du pilote.
- Infrastructure : réseau du sandbox puis cible DNS masquée dans `/run` ont bloqué le démarrage ; incidents conservés, isolation corrigée avant la campagne exploitable.
- Génération : 20 sorties et 2 blocs vérifiés dans `/tmp/odoo-agents-quality-dist`, profils actifs inchangés.

- Pilote terminé : six réponses, 511 s cumulées. Revue exploratoire : quatre conformités v1, un cas à arbitrer, un rejet critique de provenance métier.
- Bilan et preuves : [pilote du 8 septembre](pilot-2026-09-08/README.md). 35 tests verts ; graphe et génération isolée conformes.
- Suite L05–L09 différée : aucune variante de rôle adoptée, aucune amélioration générale revendiquée. Prochaine expérience cadrée dans `NEXT-EXPERIMENT.md`.

- Poursuite : 24 réponses comparées (2 cas, 3 variantes, 2 outils, 2 répétitions), puis quatre générations de code à deux efforts, oracle Odoo et correction masquée. Les rôles expérimentaux restent séparés.
- Suivi et adaptation : `OPERATIONS.md`. Corrections, preuves et limites : `TOOLING-CHANGES.md`.

- Runs locaux (`~/odoo-quality-runs/`) : comparaison `20260908-214544-91d4d786` (24/24 réponses produites, correction à suivre) ; développement `20260908-215142-3aabc864` et `20260908-215142-4142810f` ; correction `judge-comparison-01`.
- Outillage : commits `1b1128e`, `e162992`, 90 tests sur Python 3.10 et 3.12 ; premier faux vert reproduit puis supprimé sur vrai Odoo isolé.

- Conclusion : rôle développeur enrichi par la précision RPC v2, validée sur B12 (deux outils) et B13 (Claude). Rôles analystes compacts non promus. Tous les résultats, y compris rejets et défauts de l'oracle : `experiment-2026-09-08/README.md`.
- Vérification finale : 91 tests sous Python 3.10/3.12, graphe, lint Python bloquant, syntaxe shell, génération isolée conforme.

- Livraison : intégration par avance rapide dans `main`, publication de `de0000e`, génération active de 20 fichiers et 2 blocs conforme. [CI GitHub validée](https://github.com/le-goff-benoit/odoo-skills/actions/runs/34278073993). Analyse du bureau et mémoire locale actualisées. Aucun projet client modifié.


- 9 septembre : poursuite native et corrections des profils/outils, suivies dans
  [la campagne d'adoption](native-2026-09-09/README.md). Ce plan conserve
  l'historique du premier pilote ; l'état de livraison le plus récent est dans
  le rapport de cette campagne.

- 9 septembre, complément demandé : délégation réelle Claude (5 enfants),
  interruption à 600 s et reprise (3 QA, chevauchement de 40,932 s). Verrous
  récupérés, code intact, oracle 4/4 ; verdict global refusé pour A8 non prouvé.
  Compteurs corrigés, option du banc expérimentale installée, 129 tests verts.
  Consigne de consolidation testée puis non adoptée : aucun gain démontré.
  Preuves, réserves et prochains essais : [délégation et reprise](delegation-2026-09-09/README.md).

- 9 septembre, poursuite : faux `pass` reproduit à la jointure D31 sur fichiers complets.
  Six appels Claude : deux variantes inachevées sur D31, trois cas courts conformes ;
  variantes retirées, défaut de consolidation maintenu ouvert.
  Transport RPC des modules ajouté : message réel et données vérifiés, mutation
  initiale inopérante conservée puis contre-épreuve corrigée, oracle SQL 4/4.
  Deux stacks nettoyées ; 136 tests verts. [Résultats et limites](consolidation-2026-09-09/README.md).

- 9 septembre, réception structurée : contrat QA optionnel épinglé dans le flow,
  couverture exhaustive exigée au pass ; anciens flows préservés.
  Quatre appels Claude à 360 s : D31 référence pass erroné, candidat blocked ;
  CSV complet accepté, import à invariance non prouvée bloqué. Garde et usage adoptés.
  Relecture indépendante : fraîcheur par extension corrigée avec tests rouges/verts.
  147 tests verts ; titre QA contradictoire et traçabilité suraffirmée conservés
  comme réserves. [Preuves et décision d'adoption](coverage-2026-09-09/README.md).
