# Arrêt de publication A après interruption

Réception antérieure : deux contextes distincts attestés par author-A/native-provenance.json ; module_task_gate pass déjà enregistré. Aucune nouvelle réception ni QA Odoo exécutée pendant cette reprise.

La commande publique publish-memory sous claim journal_task a retourné exit 2 :
`publication mémoire refusée : fichier modifié depuis préparation : changelog/ordered/author-A/review-A.json`.

Empreinte du reçu acceptée et attestée par la provenance : 0881ab569cdfcfacd40d5d62dad7a24e2f729fbaacef5f343f2bf740fa88aed5
Empreinte du reçu présent : 739b62deb04b0fa0af62f8a097321dd538add592b68f09b17a57cbedd949fb5c

Le bundle conserve son empreinte acceptée : 14ffd9c0caeb87c641a61d6b8093aa0e5e2624fa7d3ef4ef08f6c593f1774da1

État mémoire après refus :
- .odoo-agents/PROJECT.md : SHA-256 0c72c616ca2c18c0d64bb8ca5fdc34173047ffe852d9d0b842d9d9e048e347d6, identique à la base : True ; draft publié : False.
- .odoo-agents/JOURNAL.md : SHA-256 3f2c11e9461ff58ed3dd75a8f265ac6dc3cf1078e0ee91259e24164f0e6b9f1f, identique à la base : True ; draft publié : False.

Aucune restauration ni modification des pièces anciennes. L’origine exacte de la différence du reçu n’est pas établie par les pièces disponibles.

Le code public accepted_bundle contrôle le reçu épinglé ; journal_task retry et la préparation de reprise le requièrent aussi. Une nouvelle réception dans ce flow ne répare donc pas cette intégrité rompue. L’issue publique blocked reste explicitement permise, puis memory_task_blocked done rend le terminal et nettoie les claims.

Voie publique ultérieure : conserver ce run, puis ouvrir explicitement une nouvelle tentative via odoo_flow.py start avec un nouvel identifiant (tâche directe sans plan). Vérifier les pièces et la preuve documentaire sur le périmètre autorisé, préparer des fichiers neufs via prepare-reception, faire réellement réceptionner le nouveau bundle par un contexte indépendant et publier via les API après pass. Pour une tâche de plan, utiliser plutôt odoo_plan.py reopen --reason. Aucun ancien reçu ne doit être réécrit ni renommé pour le faire accepter.
