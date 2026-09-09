# Fragment QA statique renforcée — lab_dispatch

**Commande** `/bridge/labctl lint lab_dispatch` → `preuves/05_lint.log`

| Contrôle | Résultat |
|---|---|
| ruff — règles bloquantes (config Odoo 19.0) | **vert** — All checks passed |
| ruff — conseils | aucun |
| contrôles Odoo (manifest, sécurité, tests) | **1 erreur** : `__manifest__.py`, clé `author` manquante |

## Revue du diff

- `action_recalculate` filtre par `filtered(lambda dispatch: dispatch.state == 'draft')` : un dossier
  validé n'est ni lu pour écriture ni réécrit — conforme à « pas même recomputé ».
- `_get_lines_total()` exclut `cancelled` ; préfixe `_get_` et non `_compute_`, réservé aux champs
  calculés — conforme à la ligne éditoriale 19.0.
- Formes 19.0 respectées : `Command.create` dans les tests, `TransactionCase`, `@tagged`,
  aucune forme obsolète (`attrs`, `_cr`, `<tree>`) introduite.
- Aucun changement de droits : `ir.model.access.csv` intact. Aucun champ ni vue ajoutés.

## Dette antérieure (hors diff de la tâche)

`__manifest__.py` n'a jamais porté de clé `author` : l'erreur existait au commit de base
`d6b5c10`, avant la tâche. Elle n'est **pas** introduite par ce diff. Non corrigée ici pour ne pas
inventer une valeur d'éditeur ; à arbitrer à la clôture.

**Verdict de la voie : VERT sur le diff**, avec une dette antérieure signalée et non masquée.
