# Preuve rouge — avant correction (2026-09-09T03:36:36+02:00)

Commande : /bridge/labctl qa lab_dispatch --quick --tags /lab_dispatch:TestRecalculate,/lab_dispatch:TestReprise

```
2026-09-09 01:36:25,475 1 ERROR lab_qa odoo.addons.lab_dispatch.tests.test_recalculate: FAIL: TestRecalculate.test_brouillon_exclut_les_lignes_annulees
AssertionError: 110.0 != 20.0
2026-09-09 01:36:25,488 1 ERROR lab_qa odoo.addons.lab_dispatch.tests.test_recalculate: FAIL: TestRecalculate.test_selection_mixte
AssertionError: 110.0 != 20.0
2026-09-09 01:36:25,495 1 ERROR lab_qa odoo.addons.lab_dispatch.tests.test_recalculate: FAIL: TestRecalculate.test_valide_reste_strictement_inchange
AssertionError: 110.0 != 777.0
2026-09-09 01:36:25,504 1 ERROR lab_qa odoo.addons.lab_dispatch.tests.test_recalculate: ERROR: TestReprise.test_reprise_corrige_les_brouillons
AttributeError: 'lab.dispatch' object has no attribute '_reprise_snapshot_brouillons'
2026-09-09 01:36:25,509 1 ERROR lab_qa odoo.addons.lab_dispatch.tests.test_recalculate: ERROR: TestReprise.test_reprise_idempotente
AttributeError: 'lab.dispatch' object has no attribute '_reprise_snapshot_brouillons'
2026-09-09 01:36:25,513 1 ERROR lab_qa odoo.addons.lab_dispatch.tests.test_recalculate: ERROR: TestReprise.test_reprise_ignore_les_valides
AttributeError: 'lab.dispatch' object has no attribute '_reprise_snapshot_brouillons'
2026-09-09 01:36:25,515 1 ERROR lab_qa odoo.tests.result: 3 failed, 3 error(s) of 7 tests when loading database 'lab_qa' 
222:2026-09-09 01:36:25,475 1 ERROR lab_qa odoo.addons.lab_dispatch.tests.test_recalculate: FAIL: TestRecalculate.test_brouillon_exclut_les_lignes_annulees
231:2026-09-09 01:36:25,488 1 ERROR lab_qa odoo.addons.lab_dispatch.tests.test_recalculate: FAIL: TestRecalculate.test_selection_mixte
239:2026-09-09 01:36:25,495 1 ERROR lab_qa odoo.addons.lab_dispatch.tests.test_recalculate: FAIL: TestRecalculate.test_valide_reste_strictement_inchange
248:2026-09-09 01:36:25,504 1 ERROR lab_qa odoo.addons.lab_dispatch.tests.test_recalculate: ERROR: TestReprise.test_reprise_corrige_les_brouillons
257:2026-09-09 01:36:25,509 1 ERROR lab_qa odoo.addons.lab_dispatch.tests.test_recalculate: ERROR: TestReprise.test_reprise_idempotente
266:2026-09-09 01:36:25,513 1 ERROR lab_qa odoo.addons.lab_dispatch.tests.test_recalculate: ERROR: TestReprise.test_reprise_ignore_les_valides
276:2026-09-09 01:36:25,515 1 ERROR lab_qa odoo.tests.result: 3 failed, 3 error(s) of 7 tests when loading database 'lab_qa' 
RECETTE module=lab_dispatch db=lab_qa install=ko update=n.a. uninstall=n.a. tests="3 failed, 3 error(s) of 7 tests" errors=7 failed=6 skipped=0 warnings=3 total=14s quick=14s
```

Log complet   : /home/blegoff/odoo-quality-runs/native-correction-n05-lint/N05-claude-candidate/backend/stack/artifacts/lab_dispatch-20260909-033612.lBEf8I.log
