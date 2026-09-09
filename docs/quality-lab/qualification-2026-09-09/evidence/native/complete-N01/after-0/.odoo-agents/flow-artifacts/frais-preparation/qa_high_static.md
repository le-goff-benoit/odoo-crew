# Fragment QA statique renforcée — frais de préparation (D-02)

## Lint
`/bridge/labctl lint lab_rental` → **0 erreur, 0 avertissement** (`lint.txt`).
Conseils non bloquants : 9 × `no-space-after-block-comment`, tous imputables aux marqueurs
`#=== SECTION ===#` du diff. C'est la forme d'Odoo lui-même
(`~/odoo-sources/19.0/addons/sale/models/sale_order.py:52`) et celle que prescrit le rôle : conservée.

## Revue du diff
- `models/business.py` : `_compute_amount_total` inchangé dans sa structure, le forfait est isolé dans
  `_preparation_fee()`. Le compute itère sur `self` et assigne sur tous les chemins. `@api.depends`
  couvre déjà `days`, `daily_rate` et `kind` : aucune dépendance manquante.
- Constantes nommées `PREPARATION_FEE` / `PREPARATION_FEE_MIN_DAYS` : le 12 et le 4 ne sont pas des
  nombres nus. Conforme à l'hypothèse 4 de la revue (pas de paramètre de configuration).
- La docstring de `_preparation_fee` porte la source (D-02, 2026-09-08) et le fait que D-01 est
  remplacée : la règle est traçable depuis le code.
- `migrations/19.0.1.1.0/post-migrate.py` : forme standard `def migrate(cr, version)`, comparable à
  `~/odoo-sources/19.0/addons/l10n_at/migrations/3.2/post-migrate.py`. Utilise
  `env.add_to_compute` (`~/odoo-sources/19.0/odoo/orm/environments.py:453`), pas de SQL brut.
- `tests/test_preparation_fee.py` : non importé depuis `__init__.py`, conforme au standard
  (`~/odoo-sources/19.0/addons/sale/__init__.py`). Les montants attendus sont écrits en dur d'après
  D-02, jamais recalculés par la méthode testée.
- Périmètre respecté : aucune vue, aucun droit, aucune dépendance, aucune contrainte, aucun champ.

## Écarts de conformité
Aucun introduit par le diff.

## Dette antérieure corrigée en passant
`__manifest__.py` n'avait pas de clé `author` — erreur bloquante du lint, antérieure à cette tâche
(elle apparaît aussi comme WARNING dans tous les logs de démarrage). Corrigée (`'author': 'Camptocamp'`)
parce que le diff touchait déjà le manifest et que le lint ne pouvait pas passer sinon. À signaler.

**Verdict de la voie : VERT.**
