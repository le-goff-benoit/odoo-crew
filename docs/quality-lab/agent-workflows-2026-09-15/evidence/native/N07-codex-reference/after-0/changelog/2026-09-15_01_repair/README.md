<!-- release ouverte -->
# Correction locale synthétique

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | N-17 : préparation, duplication, reliquat et reprise locale | /lab_preparation:TestLabPreparation | QA N-17 validée, reprise persistée ; release ouverte |

## Notes de travail

- 2026-09-16 : décision N-17 retenue ; voir revue_fonctionnelle.md et decision-N17.md.
- LAB.md impose les rôles sans sous-agent et le transport /bridge/labctl. Relecture non indépendante.
- Aucun ir.cron en base ; vérification par cron temporaire transactionnel, sans planification permanente.
- Version manifest 19.0.1.0.0 conservée : release ouverte, aucun champ ajouté ni livraison demandée.
- Analyse commencée sans prévision ; estimation du travail restant dans estimation.md. Trace native indisponible : temps actif, jetons et coût non mesurables ici.
- .base absente à l'arrivée : HEAD enregistré comme référence du correctif, sans prétendre reconstituer la base historique de release.

## Résultat de la tâche

N-17 reçu : neuf tests verts après reproduction rouge, update et reprise persistée de lab_client ; [QA et limites](qa.md), [couverture](coverage.json).
Le lint du diff est propre ; le lint global conserve la dette antérieure `author` absent. Relecture non indépendante imposée par LAB.md.
La recette complète reste à faire à la clôture ; aucun déploiement ni commit effectué.

Message de commit proposé : `[FIX] lab_preparation: préserver les saisies et distinguer duplication et reliquat`.
