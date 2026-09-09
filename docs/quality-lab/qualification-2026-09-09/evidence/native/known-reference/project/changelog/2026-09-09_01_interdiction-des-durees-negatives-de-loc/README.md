<!-- release ouverte -->
# Interdiction des durees negatives de location

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Contrainte SQL days >= 0 sur lab.rental (D-31), zéro autorisé, total inchangé | — | à faire |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->

- 2026-09-09 — Point 1 : QA renforcée consolidée (`qa.md`, contrat `cf836fabee21`). 8 critères sur 9
  prouvés sur base QA neuve et sur la copie `lab_client` ; A8 partiel (message remonté à l'utilisateur
  non traversé) → jointure en reprise, point laissé « à faire ». Aucun défaut de code constaté.
- 2026-09-09 — À porter en clôture : la mise à niveau d'une base contenant `days < 0` réussit sans
  poser la contrainte (prouvé, A7) — appliquer la procédure de reprise de la revue §7 et vérifier
  `pg_constraint`. Reste aussi la clé `author` absente du manifest (dette antérieure, lint en échec).
