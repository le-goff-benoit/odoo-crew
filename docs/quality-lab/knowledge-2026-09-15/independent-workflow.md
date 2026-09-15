# Réévaluation indépendante : impacts explicites et passation seule

Date : 2026-09-15. Nouvelle fixture isolée, aucune modification des dépôts, aucun appel modèle ni serveur Odoo. Documentation actuelle lue, copie dans `KNOWLEDGE-evaluated.md`. Les contrôles portent sur un parcours fonctionnel documentaire, pas sur une implémentation Odoo.

## Verdict

Le parcours fonctionne avec les nouveaux `affects_tasks` / `impact_reason`. L’écart du premier essai est corrigé : publier la décision UTC retire immédiatement l’ancien acquis Europe/Zurich de T02 et bloque le démarrage de sa dépendante T03, sans invalider T01. La reprise de T02, sa preuve documentaire et sa nouvelle réception rétablissent le droit de démarrer T03.

La distinction chemin de release / identifiant court est maintenant explicitée dans la documentation. Les commandes ont été exécutées en conséquence, sans erreur de chemin.

## Sources métier brutes et comparaison

Les originaux sont dans `project/changelog/shared-test/pieces/`.

- `regles.csv` : regroupement client oui, inter-société non. La découverte K01 et l’acquis T01 conservent cette exclusion à toutes les étapes.
- `precision.md` : ambiguïté initiale UTC / Europe/Zurich. K02 reste une question jusqu’à l’arbitrage K03.
- `decision-v1.md` : Europe/Zurich pour T02 ; T01 ne définit que les exclusions et reste indépendante du fuseau. K03 accepté déclare explicitement `affects_tasks: ["T02"]` et motive l’indépendance de T01. Les deux réceptions initiales correspondent à ces règles.
- `decision-v2.md` : pour T02 remplacer Europe/Zurich par UTC ; reporter puis reprendre et réceptionner T02 ; exclusions T01 inchangées ; T03 attend les acquis courants T01 et T02. K04 remplace K03 et conserve le même lien d’impact. Les états ci-dessous et la nouvelle mémoire UTC suivent cet arbitrage brut.

## États réellement affichés

Les sorties intégrales sont conservées dans `states/` et les lectures correspondantes dans `project/changelog/shared-test/knowledge-readings/`.

| Étape | T01 | T02 | T03 |
|---|---|---|---|
| 01 — réceptions initiales | validated | validated | pending · PRÊT |
| 02 — publication K04 | validated | stale · décision partagée affectant cette tâche changée : nouvelle réception requise | pending · dépendances : T02 |
| 03 — report T02 | validated | deferred · motif d’arbitrage v2 | pending · dépendances : T02 |
| 04 — reopen T02 | validated | pending · PRÊT | pending · dépendances : T02 |
| 05 — start T02 | validated | running | pending · dépendances : T02 |
| 06 — nouvelle réception T02 | validated | validated | pending · PRÊT |
| 07 — start T03 | validated | validated | running |

À l’étape 02, le briefing affiche K04/UTC, l’acquis T01 validé et T02 `[stale]` avec la cause, sans présenter le texte Europe/Zurich comme acquis. `start T03` est effectivement refusé (code 1). La lecture antérieure est refusée par `verify` (code 2).

Après `reopen`, T02 n’a plus de réception active : elle disparaît de la liste des acquis, tandis que `status` l’annonce prête. Après sa nouvelle réception, son fragment mémoire UTC réapparaît. T01 n’a été ni rouverte, ni réexécutée, ni reréceptionnée. Les quatre étapes de chacun des flows documentaires ont été réalisées via les commandes réelles : briefing, functional_review/answer, journal_task, task_done.

Les contributions sont des arbitrages immuables : le texte de K04 « T02 doit être reprise » reste visible après la reprise. L’état courant de T02 se lit dans la réception et le plan, pas dans cette phrase historique d’arbitrage. Les sorties distinguent bien ces deux informations.

## Passation seule, sans plan

Projet distinct `handoff-only/`, release `handoff`, aucun `plan.json`, aucun flow, aucune réception.

Sources brutes :

- `demande.md` : D01 a préparé les exclusions ; D02 doit vérifier la fenêtre UTC avant toute application ; aucun ordre de démarrage ni compte rendu d’exécution D02 transmis.
- `decision.md` : UTC retenu, exclusion inter-sociétés conservée ; aucune affirmation d’exécution, réception, disponibilité dans un planning ou déploiement de D02.
- `passation.md` : D02 est la prochaine tâche nommée ; son état d’exécution n’a pas été transmis.

J’ai publié uniquement l’arbitrage sourcé H01, catalogué demande/passation, puis exécuté `brief --task D02`, `verify` et `odoo_context.py --task D02 --query 'fenêtre UTC'`. Les trois commandes réussissent. Le briefing affiche « Tâche : D02 », l’arbitrage et les pièces ; aucune ligne d’acquis ni état de tâche n’est inventée. Le contexte expose le texte des sources qui précise l’absence de statut transmis.

**Ce qu’on sait :** D02 est nommée comme prochaine tâche, doit vérifier UTC, conserver l’exception inter-sociétés et précéder toute application.

**Ce qu’on ne sait pas :** son état d’exécution ou de planification. D02 ne peut être déclarée prête, en cours, bloquée, réceptionnée ou déployée d’après ces seules sources. Le paramètre `--task D02` étiquette la lecture ; il n’atteste pas que D02 existe dans un plan. Aucun statut manquant n’a été remplacé par une supposition.

## Preuves et commandes

- `commands.json` : argv, stdout, stderr et codes de toutes les commandes.
- `commands.sh` : trace shell lisible, comprenant les refus attendus.
- `reproduce.py` : script exact exécuté ; `python3 reproduce.py` crée une nouvelle fixture sous `/tmp`.
- `source-hashes.json` : empreintes des sources évaluées.
- `states/01-...txt` à `states/07-...txt` : états successifs.
- `project/changelog/shared-test/plan.json` : réceptions courantes, reprise et historique.
- `project/changelog/shared-test/knowledge/` : K01 à K04.
- `project/changelog/shared-test/proofs/T02-v2.json` : exécution réelle du contrôle documentaire UTC et exception.
- `handoff-D02-reading.json` : lecture sans plan ; dernière sortie de `commands.json` : contexte intégrant les sources de passation.

Aucun échec restant dans le parcours testé. La qualification ne couvre pas un module Odoo, une exécution native d’agent ou une livraison.
