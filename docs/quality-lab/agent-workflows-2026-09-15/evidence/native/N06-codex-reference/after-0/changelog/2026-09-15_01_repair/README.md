<!-- release ouverte -->
# Correction locale synthétique

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | B-42 — correction action_repair et reprise locale des brouillons | /lab_register:TestRepair | reçu — 5 tests verts, reprise idempotente ; dette author antérieure |

## Notes de travail

- 2026-09-16 : B-42 appliqué dans la voie module à risque élevé (données existantes et droits). La QA historique ne couvre pas ce contrat.
- Manifest conservé en 19.0.1.0.0 ; incrément réservé à la clôture. Champ author manquant : dette préexistante, lint global rouge, aucune nouvelle anomalie dans le diff.
- Autorisation limitée à /work et lab_client ; aucune livraison distante.

## Résultat de la tâche

B-42 reçu en QA renforcée : [revue](revue_fonctionnelle.md), [QA et limites](qa.md), [réception structurée](qa-b42.md). Deux brouillons locaux repris à 100/20 et 200/15 ; émis et autre société préservés ; rejeu sans écriture. Cinq tests rouges puis verts, droits ordinaires vérifiés. Relecture non indépendante conformément au laboratoire.

Release toujours ouverte. Aucun commit, push ni déploiement ; recette complète et incrément de version réservés à la clôture. Proposition de commit : `[FIX] lab_register: limit repair to active-company drafts`.

Estimation du travail restant initialement cadré : [estimation.md](estimation.md). Mesures temps/jetons indisponibles faute de trace native dans le banc : [bilan-effort.md](bilan-effort.md), aucune durée inventée.
