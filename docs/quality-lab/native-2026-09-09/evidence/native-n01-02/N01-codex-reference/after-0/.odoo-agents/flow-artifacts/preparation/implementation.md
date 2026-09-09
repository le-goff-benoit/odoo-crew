# Implémentation D-02 — Codex, rôle odoo-developer
Série 19.0. Spec : changelog/2026-09-09_01_frais-de-preparation-des-locations/revue_fonctionnelle.md.
5 fichiers module : modèle, migration 19.0.1.0.1, tests/__init__.py, tests/common.py, tests/test_preparation.py.
Compute stocké forfaitaire, deux contraintes de non-négativité, reprise ORM idempotente sans modification des entrées.
Lint --changed vert (preuves/lint.log). 8/8 tests ciblés exécutés, zéro skip (preuves/qa-final.log, 4 s).
Installation réelle : preuves/qa-install-tests.log. Les 4 erreurs initiales sont celles des sous-tests attendus en ValidationError ; les contraintes SQL lèvent CheckViolation. Assertions corrigées, dernière passe verte.
Les deux premières tentatives --quick ont exécuté 0 test : elles ne valent pas validation. Reprise par installation explicite via le même pont sans --quick, puis mise à jour rapide avec les 8 tests.
Version conservée 19.0.1.0.0, migration future documentée. Aucun écran, droit ou composant de facturation modifié.
