# Journal
## 2026-08-01 — Historique
**Appris** : Les durées négatives étaient anciennement permises pour des essais ; D-31 remplace cette tolérance.

## 2026-09-09 — D-31 : jours non négatifs
- Demande : contrainte SQL days >= 0, zéro valide, calcul conservé (decisions/2026-09-08.md).
- Fait : models.Constraint Odoo 19.0 ; 4 tests create/write, rollback, zéro et calcul rental/loan.
- Preuve rouge avant correction : 4 sous-tests négatifs échouent ; après : 4 méthodes vertes, 0 erreur/skip.
- QA copie lab_client : update OK, CHECK validé, témoin conservé après rejet, écritures valides possibles, nettoyage commité.
- Verdict : VALIDÉ SOUS RÉSERVE de la dette antérieure author manquant ; Ruff vert, lint global rouge sur cette seule dette.
- **Appris** : D-31 remplace la tolérance historique ; vérifier convalidated et relire après rollback. Copie initialement vide.
- Reste ouvert : release 2026-09-09_01_jours-de-location-non-negatifs, point 1 réalisé ; author et recette de clôture restent à traiter.
- Détail : changelog/2026-09-09_01_jours-de-location-non-negatifs/qa.md ; graphe days-nonnegative.
