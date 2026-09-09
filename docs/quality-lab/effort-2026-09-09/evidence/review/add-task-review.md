# Contre-épreuve CLI de add-task

Verdict initial : **rouge — titre différent accepté silencieusement**.

Sur un nouveau projet synthétique sans plan, les commandes `init`, `add-task --task PAST --title "Past synthetic execution"`, `import-usage` d'une trace native passée et `report` fonctionnent : aucune estimation créée, réel de 0,1 minute, prévisions initiale/révisée et écarts inconnus. Sur un nouveau projet avec plan, un identifiant hors plan est refusé.

En revanche, répéter `add-task` pour PAST avec `--title "Unexpected different title"` renvoie 0. Le titre original est conservé mais `updated_at` est modifié. Dans `scripts/odoo_effort.py:add_task`, la ligne 137 écrase le titre fourni avec celui de `contracts()` avant la comparaison censée refuser un titre différent. Le refus attendu n'a donc jamais lieu pour une tâche déjà connue.

Reproduction : `/tmp/odoo-effort-review-20260909/add-task-check.py`. Commandes, sorties et empreinte exacte du script testées : `add-task-review-before-fix.json`. Aucun fichier du dépôt modifié ; sources JSONL et projets entièrement synthétiques. La suite des 16 contrôles précédents n'a pas été rejouée.

## Contre-épreuve après correction

Verdict final : **vert — 7 contrôles réussis**. Après restriction du remplacement du titre aux contrats de plan, le titre différent est refusé et `effort.json` reste strictement inchangé. Le script CLI étroit a été rejoué ; les autres conditions restent conformes. Résultat et empreinte finaux dans `add-task-review.json` ; résultat rouge conservé séparément.
