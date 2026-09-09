# Fragment QA statique — contrainte days >= 0

- **Diff** : `lab_rental/models/business.py` (+5, la seule contrainte), `lab_rental/tests/__init__.py` et
  `lab_rental/tests/test_days_constraint.py` (nouveaux). Aucune vue, aucun `ir.model.access.csv`,
  aucun `ir.rule`, aucun champ touché → C7 respecté.
- **Forme 19.0** : `models.Constraint('CHECK (days >= 0)', "<message>")` en attribut de classe.
  `_sql_constraints` n'existe plus en 19.0 (SERIES_MATRIX ; `odoo/orm/table_objects.py:79`). ✅
- **Compute inchangé** : `_compute_amount_total` et ses `@api.depends` sont identiques au commit de base. ✅
- **Version du manifest** : non incrémentée — c'est la clôture de release qui le fait.
- **Lint `--changed`** (`preuves/lint.txt`) : **1 erreur**, `__manifest__.py` sans clé `author`.
  Fichier non modifié par cette tâche, erreur présente sur le commit de base
  (Odoo l'émet aussi en WARNING au chargement). **Dette antérieure, laissée à l'arbitrage.**
  Zéro erreur sur les trois fichiers réellement touchés. `ruff` absent de l'environnement : voie non jouée.

**Verdict fragment : VERT sur le périmètre de la tâche**, avec une dette antérieure signalée.
