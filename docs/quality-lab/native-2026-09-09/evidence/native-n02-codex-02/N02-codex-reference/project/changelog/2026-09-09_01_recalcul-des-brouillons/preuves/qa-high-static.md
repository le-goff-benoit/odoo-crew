# QA statique renforcée — VALIDÉ

19.0 (manifest), module lab_dispatch, mode tâche, rôle appliqué par Codex sans délégation.

- `odoo-lint.sh --changed 53a30a8ad58ecfec84b35359809f18611e54c0da /work/lab_dispatch` avec ruff 0.16.6 dans PATH : 4 fichiers, 0 erreur, 0 avertissement, 0 conseil. Preuve : `changelog/2026-09-09_01_recalcul-des-brouillons/preuves/lint.log`.
- `git diff --check` : vert.
- Relecture : sélection des brouillons avant accès aux lignes et calcul ; aucune écriture ni recomputation des validés. Exclusion des annulées, somme vide à zéro, retour True conservé ; aucune élévation de droits ni changement des ACL.
- Comparaison exacte du Float avant affectation : un second calcul identique ne modifie pas write_date. Aucun arrondi métier ajouté.
- Tests chargés depuis tests/__init__.py, BaseCommon du module base, sept cas dont sélection mixte et surveillance de write. Pas de nouvelles contraintes/groupes/vues.
- Reprise shell : garde lab_client, ORM, domaine draft, assertions sur tous les dossiers et lignes, commit explicite après validation. `F821` exclu du lint des deux scripts shell car `env` est fourni par Odoo ; les impressions JSON sont leur sortie de preuve. Petits conseils de format corrigés automatiquement, lint vert (`preuves/lint-scripts.log`).
- 1 anomalie préexistante hors diff masquée : manifest sans auteur, également visible dans les logs. Aucune anomalie bloquante dans la tâche.
- Critères couverts : C1–C4 par revue et tests, C7 par absence d'écriture si égal, C8 pour le lint. La validation persistante relève des deux autres voies.
