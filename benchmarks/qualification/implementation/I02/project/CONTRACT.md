# I02 — Fenêtres de quota (cas tenu à l'écart)

Implémente `quotas.snapshot(events, now, ttl=300)` sans modifier les entrées.
Chaque événement est un dict provider (openai/anthropic), window (5h/week),
observed_at (nombre), used_percent (nombre 0..100 inclus), reset_at (nombre ou None).
Retour : chaque fournisseur et les deux fenêtres toujours présents ; valeur None
si pas d'observation valide, sinon dict used_percent, reset_at, observed_at, stale.

L'observation valide la plus récente gagne, même si le reset est différent.
À égalité observed_at, le dernier événement dans la liste gagne. Ne jamais additionner
les fournisseurs ou fenêtres. stale est vrai si now-observed_at > ttl (égalité fraîche).

Ignorer chaque événement de fournisseur/fenêtre inconnu, temps manquant/None,
NaN/infini, temps futur, pourcentage hors 0..100 ou non numérique, booléen à la place
d'un nombre, reset_at non numérique hors None ou booléen. reset_at fini antérieur à
observed_at rend également l'événement invalide. Les timestamps négatifs sont invalides.
Les événements invalides ne doivent pas masquer une observation précédente valide.
now et ttl sont garantis numériques finis non négatifs. Les valeurs inutiles ne
créent aucune observation : une fenêtre absente n'est jamais un quota à zéro.

Ajoute des tests et exécute `python3 -m unittest discover -s . -p 'test_*.py' -v`.
Conserve test_public.py. Livrable : quotas.py, tests et evidence.json obtenu par
odoo_evidence.py run sur `--scope quotas.py --scope test_public.py` (et chaque fichier
test ajouté), environnement implementation-bench-v1, sortie /work/evidence.json,
avec cette commande unittest. Termine par un bilan court des tests.
