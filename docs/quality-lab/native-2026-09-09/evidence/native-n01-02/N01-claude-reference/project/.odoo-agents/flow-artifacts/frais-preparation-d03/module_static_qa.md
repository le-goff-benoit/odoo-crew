# Fragment QA statique — point n°2 (D-03), module `lab_rental`, série 19.0

## Lint des fichiers touchés
`odoo-lint.sh --changed d3c9977e2f lab_rental` → **0 erreur, 0 avertissement**
(ruff bloquant : 0 ; 1 anomalie masquée sur un fichier non modifié = clé `author`
absente du manifest, dette antérieure). Preuve : `preuves/lint_changed_d03.log`.

## Relecture du diff (2 fichiers)
- `lab_rental/models/business.py` : `PREPARATION_FEE` 12,0 → **15,0** ;
  `PREPARATION_FEE_MIN_DAYS` 4 → **5** ; commentaires et docstring cités sur D-03,
  avec la mention explicite que D-02 est morte. La comparaison reste `>=` — le piège
  `> 5` (qui exclurait le 5 jours) n'a pas été introduit. Aucune autre ligne touchée :
  `_compute_amount_total` et ses `@api.depends('days', 'daily_rate', 'kind')` sont
  intacts, `_preparation_fee()` garde sa signature et son `ensure_one()`.
- `lab_rental/tests/test_preparation_fee.py` : 11 tests (9 avant), attentes réécrites
  en valeurs explicites pour D-03, plus deux ajouts utiles —
  `test_rental_at_former_threshold_pays_no_fee` (4 jours → 40,0) et
  `test_rule_constants_match_the_decision` (garde-fou contre un montant changé sans
  le seuil, ou l'inverse). `tests/common.py` inchangé.

## Conformité 19.0
Aucune forme périmée introduite : pas d'`attrs`/`states`, pas de `<tree>`, pas de
`_sql_constraints`, pas de `self._cr`, aucun XML, aucun champ nouveau, aucune ligne de
sécurité. Le diff ne contient que du Python de calcul et des tests.

## Périmètre
Conforme à la spec du point n°2 : ni plus (aucune contrainte de saisie, aucune devise,
aucun arrondi, aucun écran) ni moins. Version du manifest **non incrémentée** (19.0.1.0.0) :
release ouverte, l'incrément se fait une fois à la clôture.

**Fragment statique : VERT.**
