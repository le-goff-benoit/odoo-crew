# Plan d’exécution — laboratoire qualité Odoo

Référence initiale : `9541bba`. Branche : `feat/quality-lab`.
Conception : analyse du bureau, sections 10, 13–16 (copie locale ignorée par Git).
Périmètre initial : pilote court L00–L04. **Poursuite L05–L09 autorisée par
l’utilisateur après le pilote**, avec arbitrages autonomes et mesure des gains.
Les profils actifs et les projets client ne sont pas la cible de cette branche.

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
| L06 | Fiabiliser les verdicts QA, preuves et protections (R03–R11) | L00 | implémenté, revue intégrée en cours | Cas de contrat isolés, défauts distincts |
| L07 | Organisation des tâches, mémoire et documentation | L05, L06 | implémenté, documentation en cours | Critères sections 10, 13, 14, compatibles avec l’existant |
| L08 | Variantes et comparaison contrôlée des directives | L04, L06 | campagne réelle en cours | Évaluation indépendante, corpus réservé |
| L09 | Validation intégrée et livraison réversible | L07, L08 | en cours | Aucun gain annoncé sans résultat mesuré |

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
