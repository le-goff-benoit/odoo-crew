# Association Aster — indicateur Studio de revue
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique pour le banc.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
D-22 : revue si x_studio_days >= 7 et x_studio_kind = rental ; prêts exclus. Indicateur calculé stocké x_studio_needs_review en Studio, sans écran, droit ni envoi supplémentaire.
Validé uniquement sur copie locale 19.0 ; pack limité au champ, modèle et champs lab_seed existants requis.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.

Le modèle synthétique x_lab_request ne possède aucune ACL : les scénarios RPC utilisent une action temporaire supportée par ir.model avec sudo documenté, nettoyée ensuite ; accès métier non prouvé.
Sources Studio 19.0 : ir.model.data.create marque studio mais noupdate est forcé seulement dans write ; ne pas supposer noupdate=True dès création.
