# Entrepôt Silex — recalcul des demandes en cours
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique pour le banc.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
- D-12 (2026-09-08, Marc Colin) : `action_recalculate` ne recalcule que les dossiers `draft`, en
  additionnant `quantity × price` des lignes `cancelled = False`. Un dossier `done` est figé et
  n'est **pas réécrit du tout**. Sélection mixte : brouillons recalculés, validés ignorés, aucune
  erreur. La reprise ne concerne que les brouillons et doit être idempotente. Aucun changement de
  droits ; un validé ne redevient jamais brouillon. D-11 (journal du 2026-08-01) est caduque.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
- `snapshot_total` doit rester un champ stocké **non calculé** : un `compute … store=True`
  recalculerait les dossiers validés dès qu'une ligne bouge et casserait le figeage de D-12.
- Sur la base QA, `--quick` peut ne collecter aucun test (module non installé, `-u` no-op) et rendre
  un vert trompeur : vérifier le nombre de tests exécutés dans la ligne `RECETTE`.
- La seule base autorisée est la copie synthétique locale `lab_client`.
