# Fragment QA — voie statique (relecture du diff + lint ciblé)

**Module** `lab_rental` · **série** 19.0 · **base du diff** `d3c9977`

## Lint des fichiers touchés
`odoo-lint.sh --changed d3c9977 lab_rental` → **ruff bloquant : All checks passed** ;
ruff conseils : aucun ; contrôles Odoo : **0 erreur, 0 avertissement, 0 info**.
Preuve : `preuves/lint_changed.log`.

Note : ruff était absent au premier passage (« lint partiel »), il a été installé
(`pip install --user ruff`, ruff 0.16.6) et le lint rejoué complètement. Le premier
verdict partiel n'a pas été retenu.

## Relecture du diff
- `lab_rental/models/business.py` — le calcul reste un `@api.depends('days','daily_rate','kind')`
  sur un champ stocké ; les trois dépendances de la règle sont bien déclarées, `kind` compris.
  Le compute assigne chaque enregistrement sur tous les chemins (une seule branche).
- Seuil écrit `>=` et non `>` : borne inclusive, conforme à Q1. Constante nommée
  `PREPARATION_FEE_MIN_DAYS = 4`, montant `PREPARATION_FEE = 12.0`, tous deux commentés
  avec la référence de la décision.
- Le forfait est isolé dans `_preparation_fee()` avec `ensure_one()` et une docstring qui
  cite Q1 et Q2 : la règle métier est lisible sans dérouler le compute.
- Aucune contrainte, aucun champ, aucune vue, aucune ligne de sécurité ajoutés : le
  périmètre de la revue est tenu, ni plus ni moins.
- `Float` conservé, pas de `float_round`, pas de `currency_id` : conforme à « une seule
  monnaie EUR, aucun arrondi supplémentaire ».
- Formes 19.0 vérifiées dans les sources : `TransactionCase` (`odoo/tests/common.py:990`),
  `env.flush_all()` (`odoo/orm/environments.py:380`). Aucune forme dépréciée employée.

## Dette antérieure signalée, non corrigée
`lab_rental/__manifest__.py` n'a pas de clé `author` : erreur de lint sur fichier non
modifié (masquée par `--changed`) et 3 WARNING à chaque chargement Odoo. Antérieure à la
tâche, hors périmètre — à traiter à la clôture de la release.

**Verdict de la voie statique : VERT.**
