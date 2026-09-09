# Fragment QA statique renforcée — tâche 1 (D-31)

**Série** 19.0 (annoncée par le script : « Série cible : 19.0 (__manifest__.py) ») · **module** `lab_rental`
**Périmètre `--changed`** depuis 324da2b26465cdb0ff7ac24f577b70b81038c25f : 3 fichiers (`models/business.py`, `tests/__init__.py`, `tests/test_rental_days.py`).

## Sortie du lint
`odoo-lint.sh --changed` → **1 erreur, 0 avertissement** (preuve : `preuve_lint.json` + `preuve_lint.log`, `lint_tache1.txt`).
L'unique erreur porte sur `lab_rental/__manifest__.py` : clé obligatoire `author` manquante. Ce fichier **n'est pas dans le diff** (`git status` : seul `models/business.py` est modifié). C'est une **dette antérieure**, non reprise conformément au rôle ; elle est signalée, pas corrigée. Aucune erreur sur les fichiers livrés.

## Revue humaine du diff
- **Forme de la série** : `models.Constraint('CHECK(days >= 0)', "<message>")` — forme 19.0, conforme à `odoo/orm/table_objects.py:79` et aux précédents `addons/mass_mailing/models/mailing.py:239`. Pas de `_sql_constraints` (mort en 19.0). ✅
- **Ordre des membres** : l'objet de table est placé après `_description` et avant les champs, comme l'exige la ligne éditoriale. ✅
- **Nom SQL réel** : attribut `_check_days_positive` → `full_name` = `lab_rental_check_days_positive` (30 caractères, pas de troncature par `make_identifier`). C'est ce nom que le test interroge dans `pg_constraint`. ✅
- **Message** : français, cohérent avec le module (`_description = 'Location synthétique'`) ; c'est le 2ᵉ argument, celui rendu à l'utilisateur par `get_error_message`. ✅
- **Périmètre** : aucun champ ajouté/modifié/supprimé, `_compute_amount_total` et son `@api.depends` intacts, aucune vue, aucun droit. `security/ir.model.access.csv` non touché — conforme à « aucun écran ni droit à modifier ». ✅
- **Tests** : `tests/__init__.py` importe bien `test_rental_days` ; `@tagged('post_install', '-at_install')` ; la contrainte est testée ; aucun attribut de classe nommé `run`. ✅
- **Manifest** : `version` `19.0.1.0.0` non incrémentée — correct, la release est ouverte, l'incrément se fait à la clôture.

## Angle mort de cette voie
`ruff` est introuvable sur l'hôte comme dans l'image `odoo-qa:19.0` : l'étape 1/3 du lint est **ignorée**, pas verte. La conformité de style Python n'a donc été vérifiée que par la revue humaine du diff ci-dessus.

## Verdict de la voie
**VERT** sur le code livré. 1 anomalie antérieure hors diff (manifest `author`), 0 anomalie introduite, 1 contrôle statique indisponible (ruff).
