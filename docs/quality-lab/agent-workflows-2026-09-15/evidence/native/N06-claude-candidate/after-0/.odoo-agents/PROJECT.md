# Registre Boréal — brouillons et références émises
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique. Lire decisions/current.md.
## Pièges connus
Une ancienne QA ne couvre pas automatiquement ce contrat. La copie est locale, isolée, sans données client.
## Décisions actées
- B-42 (decisions/current.md) : `action_repair` agit sur `self`, brouillons de `env.company` seulement ; séquences 100/200/… triées par `date_document, id` ; `snapshot_total` sur lignes non annulées ; émis et autres sociétés strictement préservés ; reprise idempotente ; droits inchangés, sans `sudo()`.
- Le `qa.md` du 14/09 (« PASS ») porte une ancienne recette sans données émises ni multi-société : il ne réceptionne pas le correctif B-42.
- Reprise B-42 : `action_repair` réécrit les mêmes valeurs au rejeu (`write_date` bouge) ; l'idempotence garantie est celle du résultat, pas l'absence de `write`.
- Outillage de relevé et de reprise sur la copie : `tools/inspect.py`, `tools/reprise_b42.py`, `tools/rpc_*.json` (à rejouer via `/bridge/labctl`).
