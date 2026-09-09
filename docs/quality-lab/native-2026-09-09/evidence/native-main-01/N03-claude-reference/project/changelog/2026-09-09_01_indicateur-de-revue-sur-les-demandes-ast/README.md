<!-- release ouverte -->
# Indicateur de revue sur les demandes Aster

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | [studio] Indicateur booléen stocké x_studio_needs_review sur x_lab_request (D-22) | scénarios RPC studio/test_needs_review.py | VALIDÉ — pack idempotent, scénario RPC 17/17, contre-épreuve rouge |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->

- 2026-09-09 — `x_lab_request` n'a aucun droit d'accès (constaté, non déduit) : l'indicateur est livré mais reste inexploitable par un utilisateur tant que ce point n'est pas arbitré. D-22 interdisait d'y toucher dans cette tâche.
- 2026-09-09 — aucun écran ne change dans cette release à ce stade : pas de capture attendue à la clôture pour le point 1.
