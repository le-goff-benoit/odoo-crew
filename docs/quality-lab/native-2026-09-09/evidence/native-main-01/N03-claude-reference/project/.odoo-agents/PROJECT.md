# Association Aster — indicateur Studio de revue
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique pour le banc.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
D-22 est réalisée : `x_lab_request.x_studio_needs_review` (booléen calculé stocké,
vrai si location d'au moins 7 jours ; prêts exclus). La règle vit en base, dans le
calcul du champ — pas dans un module.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
`x_lab_request` ne porte aucun droit d'accès ni règle : toute recette sur ce modèle
doit poser un droit temporaire, puis vider les caches
(`ir.model.access.call_cache_clearing_methods`), et le retirer derrière elle.
Un identifiant externe créé par Studio n'est marqué `noupdate` qu'au premier write :
vérifier ce drapeau avant d'exporter un pack.
