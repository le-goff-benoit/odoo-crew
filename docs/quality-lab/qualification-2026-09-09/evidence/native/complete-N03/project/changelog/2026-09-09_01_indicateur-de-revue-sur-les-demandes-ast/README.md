<!-- release ouverte -->
# Indicateur de revue sur les demandes Aster

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | [studio] Indicateur booléen calculé x_studio_needs_review sur x_lab_request (D-22) | `studio/test_point1_rpc.py`, `test_point1_orm.py`, `test_point1_idempotence.py` | VALIDÉ — scénarios RPC + ORM verts, diff 0, deux applications sans doublon |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->

- 2026-09-09 — D-22 (decisions/2026-09-08.md) remplace D-21 : seuil **7 jours inclus** et
  **location seule** ; les prêts sont exclus même au-delà de 7 jours. D-21 (5 jours pour tous)
  est historique et ne doit pas être appliquée.
- 2026-09-09 — `x_lab_request` n'a **aucun `ir.model.access`** en base. Conséquence : le champ
  livré n'est visible par aucun utilisateur, et la recette au niveau enregistrement n'est pas
  jouable en XML-RPC. D-22 interdisant tout changement de droits, aucune ACL n'a été créée —
  **arbitrage attendu de l'humain**, hors de ce point.
- 2026-09-09 — Écarté : le brouillon de conception qui demandait un nouveau champ « durée ».
  `x_studio_days` existe et est réutilisé tel quel.
