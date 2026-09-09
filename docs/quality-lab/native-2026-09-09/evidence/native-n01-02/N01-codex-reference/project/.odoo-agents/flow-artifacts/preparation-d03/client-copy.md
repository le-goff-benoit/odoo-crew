# QA copie D-03 — REFUSÉ au premier passage
Update lab_client OK (4,891 s), 8 totaux sous D-02 conservés après update seul. Migration donne les montants D-03 attendus mais check_inputs échoue sur write_date. Aucune transaction de reprise commitée : rollback du shell en échec, essais D-02 conservés.
Preuve : preuves/d03/copy-validation.log. Cause : critère de cadrage trop strict, write_date est une métadonnée d'audit, actualisée par Odoo 19.0/odoo/orm/models.py:4536 (_write_multi) y compris pour les champs calculés. Les entrées name/kind/days/daily_rate sont identiques.
Reprise nécessaire : corriger ce critère et son test, puis nouvelle QA. Ne pas restaurer artificiellement les métadonnées d'audit.
