# Journal
## 2026-08-01 — Historique
**Appris** : Les durées négatives étaient anciennement permises pour des essais ; D-31 remplace cette tolérance.

## 2026-09-09 — Durées de location négatives interdites (D-31)
**Demande** : interdire `lab.rental.days < 0` par une contrainte SQL, zéro autorisé, total inchangé.
**Fait** : `models.Constraint('CHECK (days >= 0)', …)` dans `lab_rental/models/business.py` (forme 19.0)
et 7 tests dans `lab_rental/tests/test_days_constraint.py`. Aucune vue, aucun droit touché.
**Verdict** : VALIDÉ — 7/7 tests verts sur base neuve, mise à niveau de `lab_client` sans perte,
`lab_rental_days_positive` vérifiée dans `pg_constraint`, rejets create/write rejoués à la main.
**Appris** :
- Une contrainte SQL ne se teste pas sans `env.cr.savepoint()` : l'`IntegrityError` avorte sinon la
  transaction et le test « la location valide subsiste » devient intestable.
- Sur ce modèle, `write` ne flushe pas tout seul : sans `flush_all()` explicite dans le bloc attendu
  en échec, le test de modification refusée passerait au vert sans rien prouver.
- Avant un `ADD CONSTRAINT`, compter les lignes fautives : ici 0 sur `lab_client`, la mise à niveau
  passe. Sur une base réelle avec les essais négatifs historiques, elle aurait échoué.
**Reste ouvert** : `__manifest__.py` sans clé `author` (erreur de lint + WARNING Odoo, antérieure) ;
release `2026-09-09_01` ouverte, 1 point sur 1 réalisé, clôture et recette complète à jouer.
