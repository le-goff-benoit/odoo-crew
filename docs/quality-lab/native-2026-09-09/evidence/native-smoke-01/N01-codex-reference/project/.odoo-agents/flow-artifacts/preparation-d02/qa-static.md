# QA statique — VALIDÉ

Codex testeur · lab_rental · Odoo 19.0 (manifest) · mode tâche renforcé.
Relecture du compute et des trois fichiers tests : dépendances complètes, calcul pour chaque ligne, aucun cumul, zéro requête dans la boucle, forfait uniquement rental >= 4.
Tests ORM : 7 méthodes, cas 3/4/5 jours, prêts, zéro, décimales, écritures indépendantes et lot mixte, flush/invalidation et recherche SQL via ORM.
`lint.log` : Ruff et règles Odoo verts, 4 fichiers, zéro erreur/avertissement/conseil.
`git diff --check` et `python3 -m compileall -q lab_rental` : succès.
Pas de nouvelle vue, droit, modèle, dépendance ou facturation. Manifest inchangé : 19.0.1.0.0.
Une anomalie antérieure masquée hors diff par le lint ; ne concerne pas le nouveau calcul.
C1 à C5 relus ; C7 conforme. C6 attendu de la voie copie.
