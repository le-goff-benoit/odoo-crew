# QA statique — 09/09/2026

Codex, rôle odoo-tester, mode graph-lane-static, Odoo 19.0 (manifest).
Preuve exécutable liée au code : `lint.json` et `lint.log` dans ce dossier.

- `odoo-lint.sh --changed c1c4140043900664943b1d6c2c58f9d28d432272 /work/lab_rental` : cinq fichiers, Ruff bloquant et conseils exécutés, contrôles Odoo, zéro erreur/avertissement.
- `git diff --check` : succès ; relecture du calcul et des dix tests : chaque record reçoit son total, toutes les dépendances sont déclarées, forfait fixe inclusif et exclusion explicite du prêt.
- Contraintes 19.0 `models.Constraint`, tests de création et d'écriture avec savepoint ; zéro accepté.
- Le helper teste store=True, flush et relecture hors cache ; création multiple et écritures de chaque dépendance couvertes.
- Aucune modification de vue, accès, dépendance, version ou facturation. `author` absent du manifest initial (preuve `git show HEAD:lab_rental/__manifest__.py`) ajouté pour satisfaire le lint obligatoire.
- Code nouveau ajouté à l'index, aucun commit créé. Script de reprise ORM relu : toutes les données sont des essais autorisés, calcul depuis les entrées, commit explicite.
- C1–C6 : couverture statique présente ; résultats d'exécution attendus dans la voie runtime. C5 (périmètre sans interface ni facturation) confirmé par le diff.

Verdict de cette voie : VALIDÉ. Pas d'anomalie restante.
