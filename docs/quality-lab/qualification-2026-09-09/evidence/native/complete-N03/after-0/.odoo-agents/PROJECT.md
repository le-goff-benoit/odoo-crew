# Association Aster — indicateur Studio de revue
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique pour le banc.
Une **demande** (`x_lab_request`) porte une durée en jours (`x_studio_days`) et une nature
(`x_studio_kind` : `rental` = location, `loan` = prêt). Une location longue exige une revue
de la coordinatrice ; un prêt jamais, quelle que soit sa durée.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
- D-22 : revue requise si `x_studio_days >= 7` **et** `x_studio_kind = 'rental'`. Seuil 7 inclus ;
  prêts exclus. Porté par le champ calculé stocké `x_studio_needs_review` (2026-09-09).
- Voie retenue pour ce projet : **Studio**, pack versionné dans la release. Aucun module custom.
- Hors D-22, et donc non fait : droits, vue, automatisation d'envoi.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
- `x_lab_request` n'a **aucun `ir.model.access`** ni aucune vue. Conséquence pratique : tout
  `create`/`read` d'un enregistrement échoue en XML-RPC, même pour `admin`. Une recette de
  comportement sur ce modèle passe par l'ORM superuser (`labctl shell`), pas par RPC.
- Ne pas recréer `x_studio_days` : le brouillon de conception initial le demandait à tort.
