# QA runtime — lab_rental 19.0 — tâche D-31
Commande : /bridge/labctl qa lab_rental --quick --tags /lab_rental:TestRentalDays
État final du code, preuve tests-final.log : install=ok update=ok ; 0 failed, 0 errors of 4 tests ; 0 skip ; 7 s (quick 6 s). Les 3 warnings author absent sont antérieurs (tests-red.log et lint-baseline.log).
C1 création négative refusée (location/prêt), C2 modification négative refusée et état valide conservé après relecture, C3 zéro à la création et modification, C4 total et tarifs existants : PASS.
La contre-épreuve sur code d'origine a 4 sous-cas rouges pour CheckViolation non levée (tests-red.log). Aucun résultat rouge final.
Point de contrôle sensible : QA sur copie dans qa-client.md ; pas de suite élargie supplémentaire, tous les tests du module appartiennent à cette classe.
