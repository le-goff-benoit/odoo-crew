# Atelier Nacre — préparation périodique et saisies explicites
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique. Lire decisions/current.md.
## Pièges connus
Une ancienne QA ne couvre pas automatiquement ce contrat. La copie est locale, isolée, sans données client.

## Décisions actées — N-17
- Source : decisions/current.md ; lab.preparation est distinct de stock.picking.
- Cron : seulement draft automatique, solde positif ou zéro. Toute saisie explicite, dont zéro, reste manuelle ; done inchangé par le cron.
- Duplication : nouvelle demande conservant ordered_qty ; quantités livrée/préparée nulles, manual=False, draft.
- Reliquat singleton positif : nouveau draft pour le solde, parent source ; source done sans écraser prepared_qty. Aucun reste positif : recordset vide.

## Résultat reçu — N-17, 2026-09-16
- Correctif et neuf tests de régression dans lab_preparation, QA de tâche renforcée validée ; rouge métier puis vert, installation/update ciblés et copie existante contrôlés.
- lab_client repris et relu après commit : id 1 préparé 999 → 7 ; ids 2/3/4 conservés à 0/2/88, métadonnées incluses. Rejeu sans write.
- Preuves : changelog/2026-09-15_01_repair/qa.md et preuves/. Aucun cron permanent n'existe sur ce modèle ; méthode testée via un ir.cron temporaire en QA.
- Dette antérieure : author absent du manifest ; Ruff et diff propres, lint global rouge pour ce seul point. Relecture non indépendante imposée par LAB.md.
- Release ouverte, version 19.0.1.0.0 conservée. Ni recette complète, ni déploiement ; temps/jetons natifs indisponibles.
