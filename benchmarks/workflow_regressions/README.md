# Parcours représentatifs W01–W06

Six cas **synthétiques**, issus de mécanismes de régression récurrents. Aucun nom,
ticket, source de module privé, capture ni base client n’est distribué.
`cases/*/public/` est le seul dossier transmissible à un agent. Les `oracle.json`,
`dossier_oracle.py` et `addons/workflow_oracle` restent hors de son contexte.

| Cas | Contrat | Contrôle indépendant |
|---|---|---|
| W01 | Commit livrable, fichier requis non suivi, migration | [Garde de livraison](../../docs/DELIVERY_GUARD.md), `tests/pilotage/test_odoo_delivery_guard.py` ; build et observation distincts. |
| W02 | Préparation 5 → correction 2 → reliquat 3 → cron | Odoo 19, `stock.picking` réel, cron déclenché par `method_direct_trigger`, utilisateur magasinier et refus portail. Mutant : remet 5. |
| W03 | Facture actuelle, historique 2020 et avoir : forfait 42, prestation 7, explication 0 et technique 0 | PDF QWeb rendu par wkhtmltopdf, trois lignes visibles, technique zéro masquée, total 49, langue du destinataire sous utilisateur facturation ordinaire et absence d’écriture comptable. Odoo 18 et 19 séparés. Mutant : supprime la ligne zéro. |
| W04 | Champ explicite 7 préservé quand la suggestion devient 9 | Chrome réel, onchange, clic de confirmation puis lecture serveur. Mutant : écrase systématiquement le champ. |
| W05 | Intention ajoutée, interruption, T01 réceptionnée préservée | Intégration réelle plan/flow/intentions/orchestration et preuves exécutées, graphe synthétique minimal ; ajout tardif, conflit de périmètre, reprise, reçu conservé et mutation rejetée. |
| W06 | Ticket/journal 19, config et manifest 18 | Oracle de contrat distinguant série des sources et version réellement déployée ; forme `_sql_constraints` attendue pour 18. |

## Exécuter

```bash
# Sans modèle ni Docker : contrats et sensibilité de l'analyseur
python3 -m unittest tests.laboratoire.test_workflow_regressions -v

# W05 sans Docker : moteurs réels, graphe minimal synthétique
python3 scripts/odoo_bench_workflows.py run --mini-release --output /tmp/workflow-mini-new

# Images locales odoo-qa:19.0 et postgres:16 : W02–W04, témoins puis mutations
python3 scripts/odoo_bench_workflows.py run --output /tmp/workflow-new-run
python3 scripts/odoo_bench_workflows.py status --output /tmp/workflow-new-run

# Image locale odoo-qa:18.0 : W03 seulement, témoin puis mutation
python3 scripts/odoo_bench_workflows.py run --invoice18 --output /tmp/workflow-invoice18-new
```

Le dossier de sortie doit être neuf. Le runner conserve images, sources copiées,
briefing de la série, logs, PDF, résultats, durées et empreintes. Son réseau Docker
est interne ; aucun port hôte ni base client. Les conteneurs et le réseau sont
nettoyés avec vérification. Un témoin rouge arrête la calibration. Un crash, un
navigateur sauté ou un message attendu simplement inclus dans le code journalisé
ne suffit pas à déclarer le témoin réussi. Les mutations ne changent jamais
l’oracle Odoo. Les durées englobent installation, assets et outils ; le compteur
`runner_command_calls` compte seulement les commandes du helper du runner.

## Évaluer les agents

Les témoins qualifient le banc ; **ils ne prouvent pas que l’agent conçoit le bon
correctif**. Comparer référence et candidat sur le même dossier public, budget,
modèle et effort ; archiver leurs modifications avant d’appliquer l’oracle.
Les appels natifs restent explicites et hors CI. Les grilles W05/W06 sont des
contrôles structurés partiels : une relecture sémantique avec citations reste
nécessaire, notamment pour juger la pertinence des tests et l’absence de demande
oubliée. Aucune promotion de modèle ne découle des calibrations sans LLM.

Le cas W03 qualifie une facture synthétique antérieure ; il ne représente ni une
migration d’une ancienne version d’Odoo ni toutes les factures historiques d’un
client. W04 ne qualifie que son formulaire. Les résultats 18 et 19 restent séparés.

[Résultats et incidents conservés](../../docs/quality-lab/workflows-2026-09-15/README.md)

[Extension PDF et nouveaux correctifs natifs N06/N07](../../docs/quality-lab/agent-workflows-2026-09-15/README.md).
