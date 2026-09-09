# QA statique renforcée — VALIDÉ
Odoo 19.0, module lab_dispatch, revue du diff et des trois fichiers de tests nouveaux.
`preuves/lint.log` dans la release : lint --changed complet (ruff bloquant et conseils, contrôles Odoo), 0 erreur et 0 avertissement dans les fichiers touchés. `git diff --check` : succès.
Le filtre draft précède tout accès aux lignes ; aucun calcul ni write des validés. Aucun sudo, SQL ou changement de droits. Champs, schéma et version inchangés.
Critères 1–4 : couverts dans le code et les tests ; critère 6 : garde contre les écritures redondantes.
Dette préexistante unique : manifest sans author, hors diff ; avertissement Odoo conservé.
Tests nouveaux à inclure au futur commit ; aucun commit demandé ni créé.
