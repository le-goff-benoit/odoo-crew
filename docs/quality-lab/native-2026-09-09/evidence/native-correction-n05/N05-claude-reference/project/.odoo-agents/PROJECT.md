# Entrepôt Silex — recalcul des demandes en cours
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique pour le banc.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
D-12 : un dossier `state='done'` est figé au sens fort — `action_recalculate` le **saute**, aucune écriture
(même valeur identique interdite) ; la preuve se prend sur `write_date`.
Corriger le calcul d'un champ stocké ne corrige pas les valeurs en base : la reprise passe par une migration
`post-migrate` et exige donc un incrément de version du manifest.
Dette antérieure : `lab_dispatch/__manifest__.py` n'a pas de clé `author` (lint rouge), non reprise.
