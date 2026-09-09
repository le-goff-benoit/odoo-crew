# QA statique — VALIDÉ
Série 19.0, origine manifest ; mode tâche renforcée, rôle appliqué par Codex.
Commande : PATH=/work/.tools/lint/bin:$PATH ~/.odoo19-agents/scripts/odoo-lint.sh --changed ace91a8b8126a559073aebe72fa091d30a47f1e9 /work/lab_rental.
Preuve : changelog/2026-09-09_01_frais-de-preparation-des-locations/preuves/lint.log et code.diff.
Ruff et contrôles Odoo : zéro erreur/avertissement sur cinq fichiers touchés. git diff --check vert. Nouveaux fichiers du module inscrits dans l'index Git en intention d'ajout et inclus au diff ; aucun commit.
Relecture : depends complet (days, daily_rate, kind), compute assigné pour tous, store préservé, pas d'arrondi ajouté ; models.Constraint conforme à 19.0 ; pas de CRUD ou requête en boucle dans le code métier ; migration ORM idempotente. SUPERUSER_ID en migration sert au recalcul intégral du modèle pendant l'upgrade.
Tests importés via tests/__init__.py ; TransactionCase adapté à la seule dépendance base. Tests SQL de rejet conformes à addons/hr_holidays/tests/test_holidays_flow.py (assertRaises d'une erreur d'intégrité et mute_logger).
C7 couvert : aucun changement vue/sécurité/facturation/manifest. Migration au prochain incrément, non déclenchée automatiquement avant clôture.
Dette préexistante : 1 anomalie hors fichiers modifiés (author absent du manifest), sans dépendance fonctionnelle du calcul à cette métadonnée.
