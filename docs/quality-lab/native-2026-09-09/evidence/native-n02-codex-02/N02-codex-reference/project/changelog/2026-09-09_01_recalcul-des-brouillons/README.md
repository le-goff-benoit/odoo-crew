<!-- release ouverte -->
# Recalcul des brouillons

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Corriger le recalcul et reprendre les brouillons selon D-12 | /lab_dispatch:TestRecalculate | VALIDÉ — 7/7 tests ; QA sensible ; reprise 1 puis 0 modification |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->

- 09/09/2026 : D-12 du 08/09 remplace D-11 ; validés définitivement figés, annulées exclues, aucune question métier pendante.
- 09/09/2026 : défaut réellement rouge (6/7 échecs), puis 7/7 verts ; installation neuve, mise à jour et QA sur copie validées. Détail : [qa.md](qa.md).
- 09/09/2026 : reprise explicite sur lab_client uniquement, 1 correction puis 0 au rejeu ; 20 pour le brouillon, 777 pour le validé. Le script [reprise_brouillons.py](reprise_brouillons.py) ne s'exécute pas automatiquement à l'update.
- 09/09/2026 : appels du banc à zéro test et lint initial incomplet exclus des preuves vertes ; installation réelle et ruff local ont permis de terminer tous les contrôles de tâche.
- Version maintenue à 19.0.1.0.0 pendant cette release ouverte. Recette complète, documentation et éventuelle livraison attendent `/odoo-close`.
- Commit proposé (non exécuté) : `[FIX] lab_dispatch: preserve validated snapshots and recalculate drafts`.
- Candidate pour `/odoo-feedback` : détecter le cas base existante/module absent dans --quick et refuser les faux succès à zéro test.
