# Fragment QA renforcée — voie statique (relecture du diff + lint)

**Série** 19.0 (origine : `__manifest__.py`) · **module** `lab_rental` · 09/09/2026

## Lint des fichiers touchés

`odoo-lint.sh --changed 93525dd lab_rental` — **6 fichiers dans le périmètre**.

| Contrôle | Résultat |
|---|---|
| ruff, règles bloquantes (config Odoo 19.0) | ✅ All checks passed |
| ruff, conseils (config complète) | ✅ aucun |
| Contrôles Odoo (manifest, XML, sécurité, tests) | ✅ 0 erreur, 0 avertissement, 0 info |

Deux points relevés puis corrigés avant de rendre : `×` ambigu dans une docstring
(`ambiguous-unicode-character-docstring`) et bloc d'imports non trié dans le fichier de
tests. Le premier passage était **rouge** — ruff manquait sur l'hôte et le lint s'annonçait
« partiel » ; ruff 0.16.6 a été installé pour que le contrôle soit réel, pas ignoré.

## Relecture du diff

| Fichier | Nature | Jugement |
|---|---|---|
| `models/business.py` | formule + méthode `_preparation_fee()` + deux constantes | conforme |
| `tests/{__init__,common}.py`, `tests/test_preparation_fee.py` | 9 tests métier | conforme |
| `migrations/19.0.1.1.0/post-migrate.py` | reprise des données existantes | conforme |
| `__manifest__.py` | version 19.0.1.0.0 → 19.0.1.1.0, clé `author` | conforme, voir R1 |

Conformité 19.0 vérifiée :
- le compute itère sur `self` et **assigne sur tous les chemins** (`_preparation_fee()`
  renvoie `0.0` dans la branche « pas de frais », jamais `None`) ;
- `@api.depends('days', 'daily_rate', 'kind')` couvre les trois entrées de la formule —
  aucune dépendance manquante, donc pas de valeur périmée en base ;
- `_preparation_fee()` porte un `ensure_one()` cohérent avec son usage par enregistrement ;
- forme de migration conforme au standard 19.0 : `def migrate(cr, version)` +
  `api.Environment(cr, SUPERUSER_ID, {})`, comme
  `~/odoo-sources/19.0/addons/l10n_at/migrations/3.2/post-migrate.py` ;
- aucune f-string dans un `_()`, aucun `print`, aucune requête en boucle, aucun SQL brut
  (le seul `cr.execute` est dans un test, pour lire la valeur **stockée** — c'est son objet) ;
- pas de `models.Constraint` ajoutée : conforme au périmètre (la positivité des entrées est
  une hypothèse de D-02, pas une exigence).

Périmètre : le diff **ne touche ni vue, ni droit, ni champ**. `security/ir.model.access.csv`
est inchangé (`git diff` vide), `data` du manifest inchangé, aucun fichier XML dans le
module. « Sans changer les écrans » est tenu au sens strict.

Régression D-01 : `grep -rn "0.07\|7 %\|percent\|0,07" lab_rental` ne renvoie **qu'une
seule** occurrence, le commentaire de `business.py:6` qui rappelle que D-02 remplace D-01.
Aucun calcul proportionnel dans le code.

## Remarques mineures

- **R1 — clé `author` ajoutée au manifest.** C'était de la dette antérieure : le lint la
  refusait et Odoo la signalait au chargement (`Missing 'author' key in manifest`). Elle est
  sur un fichier que la tâche modifiait déjà, donc corrigée plutôt que contournée. La valeur
  retenue, `Camptocamp`, est une **hypothèse** : à confirmer par l'humain.
- **R2 — version incrémentée pendant la release** (19.0.1.1.0), au lieu de la clôture. Ce
  n'est pas un écart de confort : un script de `migrations/` ne s'exécute que si la version
  installée est strictement inférieure à celle du manifest
  (`~/odoo-sources/19.0/odoo/modules/migration.py:192-208`). Sans l'incrément, la reprise
  serait morte. À la clôture, un incrément supplémentaire est sans danger ; **revenir** à
  19.0.1.0.0 tuerait la reprise.

**Verdict de la voie : vert.**
