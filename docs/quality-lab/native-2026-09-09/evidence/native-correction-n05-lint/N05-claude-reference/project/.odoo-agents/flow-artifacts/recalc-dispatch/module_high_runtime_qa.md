# Fragment QA d'exécution renforcée — lab_dispatch

| Contrôle | Commande | Résultat | Preuve |
|---|---|---|---|
| Test rouge avant correction | `qa --quick --tags /lab_dispatch:TestDispatchRecalculate` | **4 échecs / 5** (110.0 ≠ 20.0 ; 110.0 ≠ 777.0 ; 90.0 ≠ 0.0) | `preuves/01_test_rouge.log` |
| Tests après correction, base neuve | `qa --quick --fresh --tags …` | **0 failed, 0 error(s) of 5 tests** | `preuves/06_tests_verts.log` |
| Installation + mise à jour | `qa --quick --update` | `install=ok update=ok` | `preuves/07_install_update.log` |

Le test `test_recalculate_is_idempotent` passait déjà avant la correction : c'est un garde-fou de
non-régression, pas un test du défaut. Les quatre autres prouvent bien les deux défauts (A : lignes
annulées comptées ; B : dossiers validés écrasés).

**Verdict de la voie : VERT.**
