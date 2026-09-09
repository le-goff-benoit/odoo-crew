# Fragment QA d'exécution renforcée — point 1

Base QA `lab_qa`, série 19.0, base neuve (`--fresh`), chemin complet (installation, mise à jour,
tests ciblés). Journal brut : `.odoo-agents/flow-artifacts/recalcul-dispatch/qa-runtime-brut.txt`.

| Contrôle | Résultat |
|---|---|
| Installation (`-i lab_dispatch`) | ok |
| Mise à jour (`-u lab_dispatch`) | ok |
| Tests ciblés `/lab_dispatch:TestDispatchRecalculate` | **7/7 verts**, 0 erreur |
| ERROR/CRITICAL dans le log | 0 |
| Durées | base 1 s · install 18 s · update 6 s · tests 6 s |

`RECETTE module=lab_dispatch db=lab_qa install=ok update=ok tests="0 failed, 0 error(s) of 7 tests"`

## Test rouge avant correction (preuve du défaut)
Même commande sur le code d'origine : **6 échecs sur 7**
(`.odoo-agents/flow-artifacts/recalcul-dispatch/test-rouge-avant-correction.txt`) —
`110.0 != 20.0` (lignes annulées comptées), `110.0 != 777.0` (validé écrasé),
`write_date` ramenée à l'horodatage de la transaction (validé réécrit).
Seul `test_empty_selection` passait, ce qui est attendu.

## Anomalie d'outillage rencontrée (majeure, hors code du module)
`labctl qa lab_dispatch --quick` a rendu **un faux vert** : `odoo-test.sh` choisit `-u` dès que la
base existe, or `lab_dispatch` n'était pas installé sur `lab_qa` (base clonée du gabarit de
dépendances). `-u` sur un module non installé ne fait rien, `registry.updated_modules` est vide,
donc `make_suite` ne collecte aucun test — et le script conclut « installation, tests et logs
propres » avec `tests="0 failed, 0 error(s) of 0 tests"`. Détecté en lisant le compte de tests, pas
le verdict. Contournement retenu : chemin complet (sans `--quick`), qui installe avant de tester.
Leçon candidate pour `/odoo-feedback`.

**Verdict de la voie** : VERT (7/7), avec une anomalie majeure d'outillage signalée.
