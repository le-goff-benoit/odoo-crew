# Atelier Nacre — préparation périodique et saisies explicites
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique. Lire decisions/current.md.
## Pièges connus
Une ancienne QA ne couvre pas automatiquement ce contrat. La copie est locale, isolée, sans données client.

## Décisions actées — N-17
- Source : decisions/current.md. lab.preparation est synthétique, distinct de stock.picking.
- Cron : drafts automatiques seulement, max(ordered_qty-delivered_qty, 0) ; toute saisie manuelle, zéro compris, et les done sont préservés.
- Saisie : manual=True quelle que soit la quantité. Duplication : ordered_qty conservé, delivered_qty/prepared_qty=0, manual=False, draft.
- Reliquat singleton positif : nouvelle demande au restant exact avec parent source, quantités de progression à zéro, manual=False, draft ; source done sans écraser prepared_qty. Reste non positif : recordset vide, aucune création.
- Reprise autorisée exclusivement sur lab_client synthétique, aucun déploiement. Aucun cron planifié n'est livré dans ce modèle.

## Résultat reçu — 16 septembre 2026
- Tâche N-17 : 9 tests métier verts après rouge (14 assertions), installation/update QA et update copie exécutés.
- Copie : ID 1 repris de 999 à 7 ; IDs 2/3/4 conservés à 0/2/88, tous leurs champs inchangés. Rejeu dans un nouveau shell stable, write_date compris.
- QA de tâche renforcée, relecture non indépendante imposée par LAB.md. Release 2026-09-15_01_repair ouverte, recette complète différée.
- Dette antérieure distincte : manifest sans author, lint global rouge sur ce seul défaut ; Ruff et diff sans défaut introduit. Version 19.0.1.0.0 conservée jusqu'à clôture.
- Preuves : changelog/2026-09-15_01_repair/qa.md, coverage.json et preuves/. update.json est mal classé faute de bilan tests (--module inadapté), update.log et exit_code=0 attestent l'update ; ne pas le traiter comme test vert.
