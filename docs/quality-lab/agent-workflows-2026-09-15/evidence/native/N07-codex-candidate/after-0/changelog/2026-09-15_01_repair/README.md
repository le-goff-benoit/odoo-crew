<!-- release ouverte -->
# Correction locale synthétique

## Points

| # | Point | Test ciblé | État |
|---|-------|------------|------|
| 1 | N-17 : préparation périodique, duplication, reliquat et reprise locale | /lab_preparation:TestPreparation | reçu — 9 tests verts, reprise et rejeu OK ; dette lint antérieure |

## Notes de travail

- 16 septembre 2026 : décision N-17 appliquée au modèle synthétique, sans analogie stock.picking. QA renforcée sur les données existantes. LAB.md impose les rôles dans la même conversation.
- Version actuelle du manifest : 19.0.1.0.0 ; incrément reporté à la clôture (aucun nouveau champ stocké, aucune livraison demandée).
- Le README initial ne comportait pas de tableau de suivi ; ajout du tableau pour le point N-17. Aucun commit ni déploiement demandé.

## Résultat de tâche N-17

Correction reçue selon la [revue](revue_fonctionnelle.md) et la [QA de tâche](qa.md), avec [réception structurée](qa-n17.md). Preuves rouges/vertes, update, reprise et rejeu dans `preuves/`. Les brouillons automatiques de lab_client sont repris ; le reste de la cohorte est préservé.

Dette antérieure : author absent du manifest, unique erreur du lint global ; Ruff et fichiers touchés sans anomalie. Relecture non indépendante, conformément à LAB.md. Recette complète différée à la clôture, release ouverte et aucun déploiement.

Prévision restante et limites de mesure : [estimation](estimation.md), [bilan](bilan-effort.md). Aucune trace native accessible pour mesurer les rôles ; les durées et jetons manquants ne sont pas zéro.

Message de commit proposé : `[FIX] lab_preparation: préserver les saisies et réinitialiser les nouvelles demandes`.
