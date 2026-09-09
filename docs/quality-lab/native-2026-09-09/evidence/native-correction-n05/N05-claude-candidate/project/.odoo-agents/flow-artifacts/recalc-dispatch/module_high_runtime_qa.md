# Fragment QA — voie exécution (installation, mise à jour, tests ciblés)

**Stack** `labctl qa` (odoo-test.sh, base `lab_qa` neuve) · **série** 19.0

## Test rouge, avant correction
`preuves/01_test_rouge.log` — `RECETTE … install=ko … "4 failed, 3 error(s) of 7 tests"`

| Test | Échec observé | Ce qu'il prouve |
|---|---|---|
| `test_draft_excludes_cancelled_lines` | `AssertionError: 110.0 != 20.0` | les lignes annulées (3 × 30 = 90) étaient bien additionnées |
| `test_done_is_never_written` | `AssertionError: 110.0 != 777.0` | le dossier validé était bien écrasé |
| `test_mixed_selection` | `AssertionError: 110.0 != 20.0` | les deux défauts sur une sélection mixte |
| `test_draft_fully_cancelled_is_zero` | `AssertionError: 90.0 != 0.0` | un brouillon tout annulé ne tombait pas à zéro |
| 3 tests de reprise | `AttributeError: … no attribute '_repair_draft_snapshots'` | la reprise n'existait pas |

Le test rouge n'est pas décoratif : il reproduit les **deux** défauts de la demande,
avec les valeurs exactes du contrat.

## Test vert, après correction
`preuves/02_test_vert.log` —
`RECETTE module=lab_dispatch db=lab_qa install=ok update=ok tests="0 failed, 0 error(s) of 7 tests" errors=0 failed=0 skipped=0 warnings=3` ⏱ 5 s

- installation sur base neuve : **ok**
- mise à jour du module : **ok**
- tests ciblés `TestLabDispatchRecalculate` + `TestLabDispatchRepair` : **7/7**
- 3 WARNING, tous `Missing 'author' key in manifest` — même dette antérieure que le lint,
  aucun autre avertissement lié au module.

## Non joué à ce stade (par contrat de la chaîne)
Suite complète du module, désinstallation, tours navigateur : ils appartiennent à la
recette de clôture (`/odoo-close`). Le module n'a aucune vue ni JS : aucun tour n'était
pertinent pour cette tâche.

**Verdict de la voie exécution : VERT.**
