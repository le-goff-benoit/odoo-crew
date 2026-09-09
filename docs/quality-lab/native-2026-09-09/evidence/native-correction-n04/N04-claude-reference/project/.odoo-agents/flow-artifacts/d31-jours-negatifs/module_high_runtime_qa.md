# Fragment QA d'exécution renforcée — tâche 1 (D-31)

**Série** 19.0 · **module** `lab_rental` · base QA `lab_qa` (séparée de la copie client)

## Contrôles exécutés
| Contrôle | Commande | Résultat |
|---|---|---|
| Installation base neuve + tests ciblés | `labctl qa lab_rental --quick --fresh --tags /lab_rental:TestRentalDaysConstraint` | `install=ok` · **6/6 tests, 0 failed, 0 error** · 15 s (preuve : `preuve_tests.json`, `preuve_tests.log`, `qa_tache1_tests.log`) |
| Mise à niveau sur base déjà installée | `labctl qa lab_rental --quick --update --tags …` | `install=ok update=ok` · **6/6 tests** · 6 s (`qa_tache1_update.log`) |
| Logs | analyse du script | `ERROR/CRITICAL : 0` · `tests échoués : 0` · `tests ignorés : 0` · 3 WARNING, tous « Missing `author` key in manifest » (dette antérieure) |

## Les tests prouvent-ils quelque chose ?
Contrôle de non-vacuité : la contrainte a été **retirée du modèle** et la suite rejouée sur base neuve →
`4 failed of 6 tests`, `install=ko` (`qa_tache1_sans_contrainte.log`). Les quatre tests rouges sont
ceux qui portent la règle (présence en base, création refusée, modification refusée, survie de la location valide) ;
les deux restés verts sont les gardes de non-régression (zéro valide, total calculé), qui doivent
justement passer dans les deux états. La contrainte a ensuite été remise et la suite repassée au vert.

## Détail des 6 tests
`test_constraint_is_in_database`, `test_create_negative_days_refused`, `test_write_negative_days_refused`,
`test_valid_rental_survives_refusal`, `test_zero_days_allowed`, `test_total_still_computed`.

## Angle mort de cette voie
Pas de désinstallation ni de suite complète du module : c'est la recette de clôture (`/odoo-close`) qui les joue.
Aucun parcours navigateur — le module n'a aucune vue.

## Verdict de la voie
**VERT** — installation, mise à niveau, 6/6 tests ciblés, logs sans erreur, non-vacuité des tests prouvée.
