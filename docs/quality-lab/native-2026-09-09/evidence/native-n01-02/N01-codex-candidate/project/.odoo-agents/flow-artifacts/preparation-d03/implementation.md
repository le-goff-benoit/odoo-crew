# Implémentation D-03
Série 19.0, point 2 de la release existante.
- Code : lab_rental/models/business.py, seuil 5 inclus et forfait 15, dépendances et stockage inchangés.
- Tests : 8 méthodes adaptées, limites 4/5/6, prêts, zéros, décimales, changements isolés et lot ; persistance vérifiée.
- Preuve rouge avant correction : runtime-red.json/log, 11 assertions en échec dans 8 tests sous compute D-02, dont 52 != 40 et 62 != 65.
- Reprise active : changelog/2026-09-09_01_frais-de-preparation-des-locations/recompute_totals.py, D-03 ; ancienne version sauvegardée dans recompute-d02.py.
- 7 témoins persistés avant correction (seed-before.json/log), copie initialement vide.
- Lint : lint-green.json/log, 5 fichiers, ruff et contrôles Odoo verts. Premier lint partiel conservé ; venv temporaire absent dans cette nouvelle session, ruff 0.16.6 réinstallé (ruff-install.log).
- Version, écran, droits, facturation inchangés. QA renforcée à exécuter sur ce code.
