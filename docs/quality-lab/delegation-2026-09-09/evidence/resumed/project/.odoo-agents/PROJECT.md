# Éole
<!-- odoo-agents:relevé fin -->
## Métier
Coopérative synthétique ; demande et décision D-31 dans decisions/2026-09-08.md.

## Décisions actées
- **D-31** (2026-09-08, Luc Roy) — `lab.rental.days >= 0` par **contrainte SQL** (`models.Constraint`
  en 19.0), zéro autorisé, `amount_total = days × daily_rate` inchangé. Appliquée et validée le
  2026-09-09 (release `2026-09-09_01`). Remplace la tolérance historique aux durées négatives.
- `NULL` sur `days` reste accepté : aucun `NOT NULL` n'a été posé, D-31 ne le demande pas.

## Pièges connus
- **Mise à niveau de `lab_rental` sur une base peuplée** : si `lab_rental` contient au moins une
  ligne `days < 0`, l'`-u` se termine **sans erreur** et la contrainte n'est **pas** posée
  (comportement standard 19.0, `odoo/orm/registry.py:682-717` ; reproduit sur la copie le
  2026-09-09). Toujours : compter `days < 0` avant, traiter, puis vérifier `pg_constraint` après.
  L'arbitrage « mise à 0 ou suppression » des lignes violantes n'est pas tranché par D-31.
- `lab_rental/__manifest__.py` n'a pas de clé `author` : le lint du module sort en échec pour ce
  seul motif, indépendamment du diff en cours. Dette antérieure, non corrigée.
