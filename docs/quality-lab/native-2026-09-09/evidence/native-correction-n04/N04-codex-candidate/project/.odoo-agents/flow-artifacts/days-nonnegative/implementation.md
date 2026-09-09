# Implémentation D-31 — Odoo 19.0
4 fichiers : models/business.py (+5 lignes : models.Constraint CHECK days >= 0), tests/__init__.py, tests/common.py, tests/test_rental_days.py. Compute, manifest, sécurité inchangés. Nouveaux tests déclarés au suivi Git avec intent-to-add, aucun commit.
Reproduction avant correction : tests-red.log, 4 sous-cas refus négatif échouent (CheckViolation non levée), aucun autre échec.
Après contrainte : tests-green.log, 4 tests réussis, 0 erreur, 0 skip, install/update OK (6 s). Une docstring corrigée depuis ce passage sera revalidée par la voie runtime.
Lint : lint.log, Ruff vert après correction de la docstring ; unique erreur author absent du manifest inchangé. Même erreur reproduite depuis HEAD dans lint-baseline.log ; dette antérieure, hors périmètre. Aucun autre défaut introduit. QA doit conserver cette réserve explicite.
Source ORM : odoo/tests/common.py::_assertRaises gère un savepoint ; tests emploient aussi un savepoint explicite et flush dans le bloc CheckViolation. Après rejet, invalidate_recordset puis vérification des valeurs stockées et écriture valide ultérieure.
Contrat : revue_fonctionnelle.md C1–C5, D-31.
