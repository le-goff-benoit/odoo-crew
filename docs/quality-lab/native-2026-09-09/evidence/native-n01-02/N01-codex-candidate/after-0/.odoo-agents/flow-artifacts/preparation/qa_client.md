# QA copie synthétique — VALIDÉ
Copie lab_client, autorisation locale LAB.md, aucun accès production. Inventaire initial : 0 location ; quatre témoins créés sous l'ancien code (`seed_before.log`) pour éprouver la reprise réelle.
`/bridge/labctl update` réussi (`client-update.json`, 5 s environ). Avertissement du transport : --without-demo=all est interprété True par Odoo 19.0 ; non bloquant, aucune erreur module. Dispositif en lecture seule, pas de modification du pont.
Reprise versionnée exécutée après update (`recompute-1.json`) : 4 essais recalculés, 2 totaux changés. Totaux 30/40/50/40 → 30/52/62/40.
Nouvelle session shell (`copy-check-1.json`) : 4/4 valeurs persistées conformes, sans modification des données d'entrée.
Second passage (`recompute-2.json`) : 4 essais recalculés, 0 total changé ; nouvelle session (`copy-check-2.json`) : 4/4 conformes. Idempotence et persistance prouvées.
Nettoyage (`cleanup.json`) : quatre témoins supprimés et transaction validée ; copie revenue à 0 location, comme au départ.
Critère C5 couvert ; C1/C2 également éprouvés sur l'installation antérieure. Pas de documents historiques, factures ou droits modifiés. La preuve porte sur des témoins synthétiques, aucun enregistrement client réel disponible.
