# QA statique — VALIDÉ
Module lab_rental · 19.0 (manifest) · mode tâche renforcée.
Relecture des cinq fichiers Python touchés et du script de reprise : compute itératif, trois dépendances complètes, forfait fixe au seuil inclusif, aucun onchange ni effet comptable.
Tests importés par tests/__init__.py, Common TransactionCase (seule dépendance base), 8 méthodes post_install ; valeurs attendues explicites, stockage relu après flush et invalidation.
Pas de nouvelle contrainte ou de nouveau groupe. Manifest : auteur complété pour corriger l'erreur préalable détectée, version et dépendances conservées.
Lint natif --changed : 0 erreur, 0 avertissement, ruff exécuté ; preuve fraîche `lint-green.json` et log associé. `git diff --check` réussi.
C1–C4 : calcul et tests relus (exécution à confirmer par la voie runtime). C5 : script ORM idempotent relu (exécution à confirmer sur copie). C6 : diff conforme.
