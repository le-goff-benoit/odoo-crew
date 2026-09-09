# Éole
<!-- odoo-agents:relevé fin -->
## Métier
Coopérative synthétique ; demande et décision D-31 dans decisions/2026-09-08.md.

## Décisions actées
- **D-31** (2026-09-08, Luc Roy) — `lab.rental.days >= 0`, **zéro valide**, contrainte de type **SQL** explicitement
  demandée. `daily_rate` et `amount_total` gardent leur règle (jours × tarif) et restent hors périmètre.
  Appliquée le 2026-09-09 (`lab_rental_check_days_positive`).

## Pièges connus
- `lab_rental/__manifest__.py` n'a pas de clé `author` : `odoo-lint.sh` sort en échec sur ce seul point,
  même quand le code livré est propre, et chaque chargement produit un WARNING. Dette antérieure, à traiter
  sur mandat — ne pas la confondre avec une anomalie introduite.
- Une contrainte SQL déclarée dans le code n'est pas forcément posée : PostgreSQL refuse l'`ALTER TABLE`
  si des lignes la violent, et Odoo n'émet qu'un WARNING. Après tout ajout de `models.Constraint`,
  vérifier `pg_constraint` sur la base cible.
- La copie `lab_client` contient **0 ligne** `lab.rental` : elle ne permet pas d'observer un comportement
  sur données existantes. Le tester exige un jeu de données créé pour l'occasion, puis nettoyé.
