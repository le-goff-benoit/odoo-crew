<!-- release ouverte -->
# Frais de préparation des locations

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Frais de préparation D-02 : forfait 12 EUR sur les locations de 4 jours et plus (lab_rental) | — | **REMPLACÉ par le point n°2 (D-03)** — verdict d'origine conservé et toujours vrai *pour D-02* : VALIDÉ SOUS RÉSERVE, 9/9 tests ciblés, reprise prouvée sur lab_client (3/7 repris, +36 EUR), idempotente. **Non livré tel quel** : le comportement livré par cette release est D-03 |
| 2 | Frais de préparation D-03 : forfait 15 EUR à partir de 5 jours inclus, remplace D-02 (lab_rental) | — | VALIDÉ — 11/11 tests ciblés, reprise 19.0.1.2.0 prouvée sur lab_client (3/7, −21 EUR, dont 2 à la baisse), idempotente, 13/13 critères |

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

- **2026-09-09** — **D-03 remplace D-02 en cours de release** (`decisions/2026-09-09.md`,
  Alice Martin) : 15 EUR à partir de 5 jours inclus, au lieu de 12 EUR à partir de 4. Le
  point n°1 n'est pas annulé — son code de reprise `migrations/19.0.1.1.0/` reste
  nécessaire — mais **le comportement livré par cette release est celui du point n°2**.
  La communication de clôture ne doit décrire **que D-03** : annoncer 12 EUR à 4 jours
  serait faux, c'est un état intermédiaire jamais livré.
- **2026-09-09** — **Deux dossiers de `migrations/` désormais, tous les deux à conserver.**
  `19.0.1.1.0/` sert une base restée en `19.0.1.0.0` (elle passera par D-02 puis
  immédiatement par D-03) ; `19.0.1.2.0/` sert `lab_client`, déjà passée par D-02. À la
  clôture : ne retirer ni l'un ni l'autre, et **ne pas redescendre la version** du manifest
  — cela rendrait les deux reprises inertes.
- **2026-09-09** — Le piège de la release : la reprise du point n°1 **ne pouvait pas se
  rejouer** (version installée `19.0.1.1.0` = version du manifest ; un script de
  `migrations/` n'est exécuté que si l'installée est strictement inférieure). Mesuré sur
  `lab_client` **avant** de coder (`preuves/d03_copie_client_avant.txt`). Sans nouvel
  incrément, D-03 aurait laissé les sept totaux à leurs valeurs D-02, sans aucune erreur.
- **2026-09-09** — La reprise D-03 corrige **dans les deux sens** : les locations de
  4 jours perdent les 12 EUR que le point n°1 leur avait ajoutés (delta net **−21,00** sur
  `lab_client`, 296,00 → 275,00). D'où une reprise qui **réapplique la formule** et ne
  calcule jamais de delta — seule forme correcte et seule forme idempotente.
- **2026-09-09** — Reste à vérifier à la clôture, non mesuré ici : la chaîne complète
  `19.0.1.0.0 → 19.0.1.2.0` en un seul `-u`, c'est-à-dire les deux reprises d'affilée sur
  une base neuve. Elle devrait converger, mais ce n'est pas prouvé.
