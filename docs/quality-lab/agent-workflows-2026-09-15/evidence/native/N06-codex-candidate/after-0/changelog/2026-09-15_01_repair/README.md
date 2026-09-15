<!-- release ouverte -->
# Correction locale synthétique

## Points suivis

| # | Point | Test ciblé | État |
| --- | --- | --- | --- |
| 1 | B-42 : action_repair et reprise société initiale | TestRepair + copie historique | reçu — 6 tests verts, copie reprise, dette antérieure documentée |

## Notes de travail

2026-09-16 — B-42 tranche 100/200, société ACTIVE seulement, issued préservés. Revue et QA publiées dans cette release. Correction locale du module et reprise des deux brouillons de lab_client ; aucun déploiement distant.
Version lue : lab_register 19.0.1.0.0 ; aucun schéma ajouté, incrément réservé à la clôture. Dette author du manifest conservée. Relecture non indépendante imposée par LAB.md.
Sources originales : demande.md et ../../decisions/current.md ; preuves détaillées dans proofs/, qa-client.md, qa-runtime.md, qa-static.md. Ancienne QA archivée, non réutilisée comme réception.
Message de commit proposé : `[FIX] lab_register: scope draft repair to the active company`.
Release ouverte : recette de clôture et incrément restent à effectuer lors d’une demande de clôture.
