# Implémentation D-12 — 19.0
Correction dans lab_dispatch/models/business.py : filtrage des seuls draft, exclusion cancelled, écriture seulement si total différent. 7 tests dans tests/test_recalculate.py, importés par tests/__init__.py. Aucun changement de version, droits ou vues.
Reprise explicite dans changelog/2026-09-09_01_recalcul-fiable-des-brouillons/reprise/recalculate_drafts.py, garde lab_client, assertions et commit contrôlé.
Preuves de défaut : preuves/test-rouge.json et test-rouge.log : 7 échecs métier, aucune erreur technique. Sur la copie : preuves/defaut-copie.log, 999/777 → 110/110 puis rollback vérifié.
Lint : preuves/lint-developer.log, Ruff entièrement vert. Lint Odoo code 1 pour une unique dette du manifest non modifié (author absent), reproduite sur HEAD dans preuves/lint-base.log. Aucune anomalie nouvelle. Cette dette sera distinguée explicitement du verdict fonctionnel.
Suite : trois voies de QA sensible, exécutées sans sous-agent conformément à LAB.md.
