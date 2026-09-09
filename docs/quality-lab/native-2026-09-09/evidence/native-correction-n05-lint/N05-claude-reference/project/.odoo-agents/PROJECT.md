# Entrepôt Silex — recalcul des demandes en cours
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique pour le banc.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
`snapshot_total` de `lab.dispatch` est un total **figé**, jamais un champ calculé stocké : un
`compute` recalculerait les dossiers validés, que D-12 gèle définitivement.
Une reprise de ces totaux se compare à l'exact, sans tolérance à 2 décimales : des écarts de
l'ordre de 0,004 existent en base et doivent être corrigés.
