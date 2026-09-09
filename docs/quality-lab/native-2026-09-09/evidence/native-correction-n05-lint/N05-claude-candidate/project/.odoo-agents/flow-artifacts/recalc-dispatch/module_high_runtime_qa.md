# Fragment QA — voie exécution (installation, mise à jour, tests)

Base QA `lab_qa`, séparée de la copie `lab_client`.

| Contrôle | Commande | Résultat |
|---|---|---|
| Tests ciblés avant correction (preuve du défaut) | `labctl qa lab_dispatch --quick --tags /lab_dispatch:TestRecalculate,/lab_dispatch:TestReprise` | **ROUGE — 3 failed, 3 error(s) / 7** ⏱ 14s |
| Installation + mise à jour + tests ciblés après correction | idem | **VERT — 0 failed, 0 error(s) / 7**, `install=ok update=ok` ⏱ 6s |
| Suite complète du module, base neuve (point de contrôle) | `labctl qa lab_dispatch --fresh` | **VERT — 0 failed, 0 error(s) / 7**, `install=ok`, ERROR/CRITICAL = 0 ⏱ 19s |

Journaux : `preuves/01_test_rouge_complet.log`, `preuves/03_tests_verts.log`,
`preuves/05_suite_complete_base_neuve.log`.

## Ce que le rouge prouve

- `AssertionError: 110.0 != 20.0` — le total incluait les lignes `cancelled = True`.
- `AssertionError: 110.0 != 777.0` — l'action écrasait le total d'un dossier validé.
- `AttributeError: 'lab.dispatch' object has no attribute '_reprise_snapshot_brouillons'` —
  la reprise n'existait pas.

Les six tests rouges sont les mêmes que les six tests verts après correction : aucun test n'a
été réécrit pour s'adapter au code.

## Avertissements

3 warnings au run ciblé, 6 au run base neuve, tous `Missing 'author' key in manifest` —
dette antérieure, hors diff. Aucun autre avertissement lié au module.

**Fragment : VERT.**
