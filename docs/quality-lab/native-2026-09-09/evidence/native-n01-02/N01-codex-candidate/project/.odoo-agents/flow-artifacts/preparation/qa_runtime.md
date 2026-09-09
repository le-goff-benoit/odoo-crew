# QA d'exécution — VALIDÉ
Module lab_rental · Odoo 19.0 (manifest) · QA de tâche renforcée.
Commande via preuve `runtime.json` : `/bridge/labctl qa lab_rental --quick --tags /lab_rental:TestPreparationFee`.
Installation réelle sur base séparée lab_qa réussie ; 8 méthodes métier exécutées, 0 échec, 0 erreur, 0 ignoré, 0 warning. Bilan natif RECETTE : total 19 s, quick 18 s. Le compteur stats 10 inclut les phases techniques ; le bilan métier est bien 8 tests.
C1 : test_rental_threshold ; C2 : test_loans_have_no_fee ; C3 : test_zero_values/test_decimal_rate ; C4 : test_days_changes/test_daily_rate_changes/test_kind_changes/test_mixed_batch ; C5 stockage : assertStoredTotals dans tous les tests.
Mise à jour de l'installation existante couverte séparément par la voie copie (`client-update.json`). Pas de suite supplémentaire : les huit tests constituent toute la suite du module et la tâche sensible reçoit aussi la validation sur copie.
