# QA statique finale — reprise 1

Odoo 19.0, lab_rental, Codex rôle testeur.
Relecture initiale `qa_static.md` maintenue ; seul delta : les tests de contraintes attendent maintenant `CheckViolation` et vérifient le nom exact de la contrainte. `mute_logger('odoo.sql_db')` limité à ces deux tests de refus, conformément à `odoo/addons/base/tests/test_sql.py` en 19.0.
`lint_final.json/log` : Ruff et lint Odoo sur les cinq fichiers touchés, zéro erreur/avertissement, code final lié par empreinte.
Les tests nouveaux et modifiés sont dans l'index. Aucun changement de calcul ni de dépendances pendant la reprise.
Verdict statique : VALIDÉ, C5 et couverture C1–C6 vérifiés.
