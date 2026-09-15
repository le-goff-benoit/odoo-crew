# QA statique de tâche — N-17, 19.0

Diff relu contre HEAD initial (.base documentée), nouvelles dépendances de tests indexées, imports vérifiés ; git diff HEAD --check sans erreur.
Lint complet imposé par LAB.md : preuves/lint.log et lint.json. Ruff bloquant et conseils : aucun écart. Contrôles Odoo : une erreur, author absent dans __manifest__.py.
Dette antérieure isolée : manifest-before.txt reproduit exactement le manifest courant, non modifié ; ni schéma, ni dépendance, ni droit ajouté. Le seul diagnostic Odoo concerne ce fichier inchangé. Le diff modèle/tests ne porte aucun défaut de lint.
Revue : ensure_one précède les mutations ; recordset vide en absence de reste ; source figée après création réussie ; prepared_qty source jamais écrasée ; filtre cron draft/manual ; aucun sudo ajouté, aucun arrondi artificiel. copy_data délègue à l'ORM 19.0, avec remise à zéro par défaut.
Les tests couvrent des valeurs indépendantes N-17 et les transitions après duplication/reliquat. Aucun écran ajouté : pas de contrôle navigateur requis pour cette tâche.
Verdict du diff : VALIDÉ. Lint global reste rouge pour la dette author, distincte du correctif. Relecture par l'orchestrateur, non indépendante (LAB.md).
