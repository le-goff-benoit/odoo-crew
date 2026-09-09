# Délégation réellement effectuée
Orchestrateur : conversation /root/workflow_codex, seul écrivain flow, QA consolidée et mémoire.
- /root/workflow_codex/qa_diff : nouvelle conversation fork_turns=none, rôle odoo-tester graph-lane-studio-diff, fichiers studio_diff.md/.log uniquement. Voie terminée.
- /root/workflow_codex/qa_runtime : nouvelle conversation fork_turns=none, rôle odoo-tester graph-lane-studio-runtime, fichiers studio_runtime.md/.log et éventuel script studio_runtime_*.py. Voie terminée.
Le graphe figé impose une vague séquentielle par voie : client_copy read pour diff et write pour runtime sont incompatibles. Aucune fausse parallélisation ni partage de verrou.
Analyste et Studio appliqués directement par l'orchestrateur, sans délégation artificielle.
/root/workflow_codex/reception : nouvelle conversation indépendante fork_turns=none ; bundle documentaire reçu sur trois axes, review-1.json rendu seul, pass accepté par le garde.
