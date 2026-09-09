# QA d'exécution — VALIDÉ
Série 19.0, mode tâche renforcée, rôle appliqué par Codex.
Preuves dans changelog/2026-09-09_01_frais-de-preparation-des-locations/preuves/.
Installation réelle : /bridge/labctl qa lab_rental --tags /lab_rental:TestPreparation (qa-install-tests.log, installation 2 s).
Validation finale : /bridge/labctl qa lab_rental --quick --tags /lab_rental:TestPreparation (qa-final.log, update + 8 tests en 4 s).
Résultat final : 0 failed, 0 error(s) of 8 tests ; aucun skip, aucune erreur de log. C1 à C6 couverts par les méthodes de TestPreparation et leurs assertions SQL / ORM.
Les tentatives rapides initiales (qa-runtime.log et qa-install.log) ont exécuté zéro test ; leurs annonces install=ok ne valent pas preuve. L'installation sans --quick a résolu ce défaut du script natif. Les quatre erreurs de sous-tests à l'installation ont ensuite été corrigées : mauvaise exception attendue pour des contraintes SQL, et non défaut du calcul.
L'absence d'author dans le manifest produit trois warnings répétés préexistants ; les warnings --without-demo=all et http-interface viennent de l'outillage.
Pas de contrôle supplémentaire de suite : cette classe constitue toute la suite existante du module ; la reprise sensible est contrôlée dans la voie copie.
