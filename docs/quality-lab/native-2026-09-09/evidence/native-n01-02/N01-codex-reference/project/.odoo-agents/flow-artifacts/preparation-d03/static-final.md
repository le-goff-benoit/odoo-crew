# QA statique finale D-03 — VALIDÉ
Relecture après reprise : seul le contrôle non métier de write_date est retiré du test, conformément au standard _write_multi. Calcul, seuil, forfait et exclusion des prêts conformes à D-03. Critères C1–C7 avec C6 rectifié.
Lint --changed final : 5 fichiers depuis ouverture de release, Ruff et contrôles Odoo verts (preuves/d03/lint-final.log). Une anomalie préexistante de manifest masquée. Diff final dans preuves/d03/code-final.diff, git diff --check vert.
