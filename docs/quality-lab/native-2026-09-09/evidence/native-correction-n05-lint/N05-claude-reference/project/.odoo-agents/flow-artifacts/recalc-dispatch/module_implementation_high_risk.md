# Implémentation sensible — action_recalculate + reprise

- `lab_dispatch/models/business.py` : `action_recalculate` ne traite plus que `state == 'draft'` ;
  le total passe par `_get_lines_total()` qui exclut les lignes `cancelled`.
- `lab_dispatch/tests/test_dispatch_recalculate.py` (nouveau, 5 tests) : exclusion des annulées,
  validé jamais recalculé (write_date inchangée), sélection mixte, idempotence, brouillon vidé.
- `changelog/2026-09-09_01_.../reprise/reprise_brouillons.py` : reprise idempotente des brouillons.

Preuves : `preuves/01_test_rouge.log` (4/5 rouges avant correction), `preuves/02_update_copie.log`,
`preuves/03_reprise_passe1.log` (2 modifiés), `preuves/04_reprise_passe2.log` (0 modifié).
