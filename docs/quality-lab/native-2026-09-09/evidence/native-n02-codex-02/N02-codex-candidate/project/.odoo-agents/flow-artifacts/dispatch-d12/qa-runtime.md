# QA exécution renforcée — VALIDÉ

Module lab_dispatch · série 19.0 (manifest) · mode tâche sensible.
Commande réelle : `labctl qa lab_dispatch --quick --fresh --tags /lab_dispatch:TestDispatchRecalculate`, enveloppée par odoo_evidence avec contrôle du bilan du module.
Preuve : `changelog/2026-09-09_01_recalcul-des-brouillons-d12/qa-runtime.json` et `.log`.
Six tests passés, zéro échec, erreur ou skip. Installation de l'état final sur base QA fraîche. C1–C4 et C6 couverts. La mise à niveau de la copie existante et C5 relèvent de la voie copie.
