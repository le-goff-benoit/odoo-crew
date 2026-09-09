# Association Aster — indicateur Studio de revue
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique pour le banc.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
D-22 est implémentée depuis le 2026-09-09 par un champ Studio calculé stocké
`x_lab_request.x_studio_needs_review` (release 2026-09-09_01) : revue requise si
`x_studio_kind == 'rental'` et `x_studio_days >= 7`. Voie Studio, pas de module.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
`x_lab_request` n'a aucun `ir.model.access` ni `ir.rule` : hors superutilisateur,
aucun accès n'est possible (`ir_model.py:2134-2167`). Conséquences : les scénarios
au niveau enregistrement se jouent en ORM superutilisateur, et rien de ce modèle
n'est visible par un utilisateur réel tant que les droits ne sont pas tranchés.
Un identifiant externe créé en contexte `studio` sort en `noupdate=False` ; Studio
ne le protège qu'au `write` suivant. Le script de construction rejoue cet appel.
