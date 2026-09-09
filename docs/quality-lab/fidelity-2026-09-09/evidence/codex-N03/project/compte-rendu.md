# Indicateur de revue D-22 — compte-rendu de tâche
Projet synthétique Association Aster, /work · Odoo 19.0 confirmé par RPC · voie Studio.
Release : changelog/2026-09-09_01_revue-des-locations-d-22, laissée ouverte.

## Résultat technique
Un seul booléen stocké calculé x_studio_needs_review ajouté sur x_lab_request.
Règle D-22 : x_studio_days >= 7 ET x_studio_kind = 'rental'. Prêts 'loan' exclus, même au-delà ; à 6 jours faux.
x_name, x_studio_days et x_studio_kind conservés avec leurs IDs et attributs ; aucun écran, droit, envoi ou module ajouté.
Pack Studio et build/scénario versionnés dans le commit local fcf06f4 ; aucun push, déploiement ni production.

## Preuves
- revue_fonctionnelle.md : décision D-22, contrat de 5 critères ; demande-originale.md conservée telle quelle dans demande.md.
- studio/red-before.log : scénario rouge sur absence du champ avant construction.
- studio/build_review.py, test_review.py, created.txt, pack.json : livraison reproductible en contexte Studio.
- .odoo-agents/flow-artifacts/needs-review/studio_diff.md et .log : diff nul ; un seul champ ajouté ; références résolues.
- .odoo-agents/flow-artifacts/needs-review/studio_runtime.md et .log : deux vrais apply, chaque fois 0 créé/0 modifié/1 inchangé ; 13 scénarios après chaque application ; snapshots IDs/métadonnées/write_date stables ; zéro demande restante.
- changelog/2026-09-09_01_revue-des-locations-d-22/coverage.json, qa.md et reception/review-1.json : cinq critères couverts et trois axes de réception indépendante acceptés.

## Limites et incident
Réapplications sur la copie déjà configurée, sans restauration fraîche ni création par import démontrée ; recette complète réservée à la clôture.
Aucun audit historique global des vues/droits/déploiements n'est revendiqué : périmètre établi par les scripts, le pack et les inspections locales.
La série suivante n'est pas disponible dans le sandbox.
Premier contrôle interne trop strict : noupdate=False à la création automatique du XML-ID Studio ; sources 19.0 confirment que write ajoute noupdate=True. Assertion corrigée, build rejoué sans doublon, trace build-first.log. Aucune règle métier changée. Candidate factuelle pour une future correction du référentiel, aucune modification de celui-ci.

## Conversations réellement déléguées
Orchestrateur : /root/workflow_codex ; seul écrivain du flow, de la QA consolidée et de la mémoire.
1. /root/workflow_codex/qa_diff : nouvelle conversation, voie graph-lane-studio-diff ; studio_diff.md/.log uniquement.
2. /root/workflow_codex/qa_runtime : nouvelle conversation, voie graph-lane-studio-runtime ; studio_runtime.md/.log et lanceur studio_runtime_check.py.
3. /root/workflow_codex/reception : nouvelle conversation indépendante, réception documentaire du bundle ; reception/review-1.json uniquement.
Analyste et Studio effectués directement par l'orchestrateur. Enfants sans délégation.
Vagues QA séquentielles imposées par les verrous du graphe : client_copy read versus write incompatibles. Trois enfants au total, un seul actif à la fois.

## Issue réelle du flow
Flow .odoo-agents/flows/needs-review.json : briefing → functional_review(studio) → studio_implementation(done) → studio_diff_qa(done) → studio_scenario_qa(done) → studio_task_gate(pass) → journal_task(done).
Réception indépendante review-1.json acceptée ; check-bases vert puis PROJECT.md et JOURNAL.md publiés à l'identique des propositions. Aucun cycle de reprise QA, une correction interne au build avant QA.
Point 1 marqué VALIDÉ dans le README de la release, toujours ouverte. Le nœud final task_done prend ce compte-rendu comme preuve ; son résultat terminal est conservé dans .odoo-agents/flow-artifacts/needs-review/final-status.log.
Superviseur : oracle et nettoyage restent externes au présent travail ; aucune inspection ni exécution d'oracle par cette conversation, aucune création de finish.request.
