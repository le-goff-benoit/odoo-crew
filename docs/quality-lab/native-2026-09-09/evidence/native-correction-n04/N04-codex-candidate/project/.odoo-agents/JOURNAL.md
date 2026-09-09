# Journal
## 2026-08-01 — Historique
**Appris** : Les durées négatives étaient anciennement permises pour des essais ; D-31 remplace cette tolérance.

## 2026-09-09 — D-31 : jours non négatifs (lab_rental, 19.0)
- Demande : SQL days >= 0, zéro permis, total et tarifs inchangés ; décision Luc Roy du 2026-09-08 remplaçant la tolérance historique.
- Fait : models.Constraint et 4 tests ; preuve rouge d'origine puis 4/4 verts, 0 skip ; install/update QA OK.
- Copie lab_client : update OK, CHECK validé en catalogue, location avant update et après rejet conservée ; scénarios zéro/total verts, données temporaires nettoyées.
- Verdict : VALIDÉ SOUS RÉSERVE ; Ruff vert, lint global code 1 pour author absent du manifest d'origine (contre-épreuve HEAD).
- **Appris** : ORM SQL lève CheckViolation ; flush dans savepoint et relecture après rejet ; vérifier convalidated après update. D-31 ne restreint pas daily_rate.
- Mémoire : PROJECT.md actualisé, consolidation dans la release ; pas de nouvelle règle à promouvoir dans LESSONS.md.
- Détail : changelog/2026-09-09_01_jours-de-location-non-negatifs/qa.md ; flow days-nonnegative.
- Reste ouvert : release (1/1 point réalisé), dette author à arbitrer à la livraison ; recette complète à la clôture. Aucun écran/droit modifié.
