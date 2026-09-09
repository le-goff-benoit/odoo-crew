# Association Aster — indicateur Studio de revue
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique pour le banc.
Les locations et prêts sont distingués par x_studio_kind ; la durée est le champ existant x_studio_days.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
D-22 (Nora Petit) : x_studio_needs_review est vrai si x_studio_days >= 7 ET x_studio_kind = 'rental'. Les prêts 'loan' sont exclus même à 7 jours ou plus ; à 6 jours aucune revue. D-21 (5 jours pour tous) est remplacée.
Indicateur booléen calculé stocké dépendant des deux champs existants ; x_name, x_studio_days et x_studio_kind sont conservés. Aucun écran, droit ou envoi modifié. Voie Studio sans module.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
La validation porte uniquement sur lab_client, copie synthétique locale 19.0 ; aucun déploiement effectué, release ouverte.
Studio crée bien son XML-ID automatiquement en contexte studio=True. Dans cette série, noupdate est false à la création, puis true après écriture ; ne pas confondre ce détail avec l'absence du marquage studio.
