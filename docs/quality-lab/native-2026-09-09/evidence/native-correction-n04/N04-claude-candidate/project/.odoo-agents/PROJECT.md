# Éole
<!-- odoo-agents:relevé fin -->
## Métier
Coopérative synthétique ; demande et décision D-31 dans decisions/2026-09-08.md.

## Décisions actées
- **D-31** (2026-09-08, Luc Roy) — `lab.rental.days >= 0`, **contrainte SQL**, zéro autorisé.
  Remplace la tolérance historique aux durées négatives (essais). `daily_rate` et `amount_total`
  gardent leur règle : total = jours × tarif. Posée le 2026-09-09 (`lab_rental_days_positive`).

## Pièges connus
- Toute nouvelle contrainte SQL sur `lab.rental` doit être précédée d'un comptage des lignes
  fautives : les données d'essai historiques admettaient des jours négatifs et feraient échouer
  la mise à niveau.
- `lab_rental/__manifest__.py` n'a pas de clé `author` : erreur de lint et WARNING Odoo au
  chargement, dette antérieure non arbitrée.
