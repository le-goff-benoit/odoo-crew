# I01 — Ordonnancer sans exécuter

Implémente `scheduler.ready(tasks, active_locks)` sans modifier ses entrées.
Chaque tâche est un dict avec `id` chaîne unique, `status` parmi pending/running/received,
`proof_current` booléen, `deps` liste d'identifiants, `reads` et `writes` listes de
ressources. active_locks = {resource: 'read'|'write'}.

Retourne les identifiants pending triés lexicalement dont TOUTES les dépendances
transitives sont received avec proof_current=True. Une dépendance directe reçue
mais fondée sur une dépendance périmée ne libère donc pas sa descendante.
Une tâche qui écrit une ressource verrouillée est bloquée ; lire n'est bloqué que
par un verrou write. Les autres tâches pending proposées ne se verrouillent pas
entre elles : la fonction expose les candidats, pas une vague déjà revendiquée.

Tout identifiant dupliqué, dépendance absente, cycle (même dans une composante qui
n'est pas pending), statut inconnu ou mode de verrou inconnu lève ValueError.
Les clés et types décrits sont garantis ; aucune validation supplémentaire n'est demandée.

Ajoute des tests et exécute `python3 -m unittest discover -s . -p 'test_*.py' -v`.
Conserve test_public.py. Écris implementation.py seulement si nécessaire : l'API
publique doit rester scheduler.ready. Livrable : code, tests et evidence.json obtenu
par odoo_evidence.py run sur `--scope scheduler.py --scope test_public.py` (et chaque
fichier test ajouté), environnement implementation-bench-v1, sortie /work/evidence.json,
avec cette commande unittest. Termine par un bilan court des tests.
