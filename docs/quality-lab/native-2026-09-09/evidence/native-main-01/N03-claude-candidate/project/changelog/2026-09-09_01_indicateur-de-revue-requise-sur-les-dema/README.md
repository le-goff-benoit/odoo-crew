<!-- release ouverte -->
# Indicateur de revue requise sur les demandes

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | [studio] Indicateur calculé stocké x_studio_needs_review sur x_lab_request (D-22) | — | VALIDÉ — 12/12 RPC, 16/16 ORM, pack appliqué 2× sans doublon |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->

- 2026-09-09 — D-22 (7 jours, locations seules) remplace D-21 (5 jours, tous types) : c'est D-22 qui est implémentée.
- 2026-09-09 — `x_lab_request` n'a aucun `ir.model.access` : l'indicateur est invisible pour tout utilisateur réel tant que ce point n'est pas tranché. Hors périmètre de D-22, à arbitrer avant mise en service.
- 2026-09-09 — Un identifiant externe créé en contexte `studio` sort en `noupdate=False` ; Studio ne le protège qu'au `write` suivant. Le script de construction rejoue cet appel.
- 2026-09-09 — Aucun déploiement : le pack n'a été appliqué que sur la copie locale `lab_client`.
