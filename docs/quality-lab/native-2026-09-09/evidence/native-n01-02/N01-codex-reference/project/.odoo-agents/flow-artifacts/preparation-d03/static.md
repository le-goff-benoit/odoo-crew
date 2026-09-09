# QA statique D-03 — VALIDÉ
Relecture code-d03.diff : forfait fixe 15, seuil inclusif 5, prêts exclus, base inchangée. Dépendances et contraintes conservées ; migration appelle le compute courant, idempotente. Tests couvrent C1–C6 ; C7 vérifié par history-check.log et diff.
Lint --changed depuis la base de release : 5 fichiers, Ruff et contrôles Odoo 19.0 verts (preuves/d03/lint.log). git diff --check : succès.
Une dette préexistante de manifest masquée par --changed (author absent), non modifiée. Aucun bloquant.
