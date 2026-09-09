<!-- release ouverte -->
# Frais de préparation des locations

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Frais de préparation D-02 : forfait 12 EUR sur les locations de 4 jours et plus (lab_rental) | — | VALIDÉ SOUS RÉSERVE — 9/9 tests ciblés, reprise prouvée sur lab_client (3/7 repris, +36 EUR), idempotente |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->

- **2026-09-09** — Hypothèse de la revue démentie par la mesure : `-u` ne recalcule **pas**
  un champ stocké dont seul le corps du compute a changé (preuve : `preuves/copie_client_avant.txt`,
  totaux inchangés après mise à jour). Un `migrations/19.0.1.1.0/post-migrate.py` idempotent
  est ajouté au périmètre, et la version du manifest passe à **19.0.1.1.0 dès maintenant** —
  sans quoi le script ne s'exécuterait pas. À la clôture : ne pas retirer ce dossier ; un
  nouvel incrément (19.0.1.2.0) le laisse s'exécuter, une remise à 19.0.1.0.0 le tuerait.
- **2026-09-09** — La copie `lab_client` ne contenait **aucun** `lab.rental` : sept
  enregistrements représentatifs ont été créés avant la modification, avec les totaux de
  l'ancienne formule, pour que la reprise ait quelque chose à reprendre.
- **2026-09-09** — Écarté du périmètre : contrainte de positivité sur `days`/`daily_rate`
  (D-02 la pose comme hypothèse sur les données, pas comme exigence ; une contrainte SQL
  échouerait sur d'éventuelles données non conformes) et passage en `Monetary` (ajouterait
  `currency_id`, donc un changement d'écran).
