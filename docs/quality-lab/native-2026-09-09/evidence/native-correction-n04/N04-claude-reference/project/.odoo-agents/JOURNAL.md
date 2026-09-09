# Journal

## 2026-09-09 — Durées de location négatives interdites (D-31)

**Demande** : interdire `lab.rental.days < 0` par une contrainte SQL, zéro toujours valide, calcul du total inchangé.
**Fait** : `models.Constraint('CHECK(days >= 0)', …)` sur `lab.rental` (forme 19.0, pas `_sql_constraints`) + 6 tests
dans `lab_rental/tests/test_rental_days.py`. Aucun champ, aucune vue, aucun droit touché.
**Verdict** : VALIDÉ (QA renforcée, 3 voies). 6/6 tests ciblés ; install et update OK ; contrainte vérifiée dans
`pg_constraint` après mise à niveau de la copie `lab_client` ; refus de création et d'écriture reproduits sur la copie,
location valide intacte après rejet ; copie rendue à son état initial. Détail : `2026-09-09_01_interdiction-des-durees-de-location-nega/qa.md`.
**Appris** :
- La tolérance historique aux durées négatives n'a laissé **aucune ligne** dans la copie (`lab_rental` vide) : la
  contrainte a pu être posée sans reprise de données.
- Une contrainte SQL présente dans le code n'est pas une contrainte posée : si des lignes la violent, PostgreSQL
  refuse l'`ALTER TABLE` et Odoo ne laisse qu'un WARNING. Lire `pg_constraint` après update est le seul contrôle qui prouve.
- Un test de refus ne prouve rien tant qu'il n'a pas été vu rouge : contrainte retirée → 4/6 rouges, remise → 6/6 verts.
**Reste ouvert** : `__manifest__.py` sans clé `author` (dette antérieure, fait échouer le lint, non corrigée faute de
mandat) ; `daily_rate` négatif toujours possible, non arbitré par D-31 ; release ouverte, recette complète à la clôture.

## 2026-08-01 — Historique
**Appris** : Les durées négatives étaient anciennement permises pour des essais ; D-31 remplace cette tolérance.

