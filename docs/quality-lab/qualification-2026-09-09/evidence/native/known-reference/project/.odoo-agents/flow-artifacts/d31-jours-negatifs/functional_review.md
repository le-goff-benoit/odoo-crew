# functional_review — d31-jours-negatifs (odoo-analyst)

- **Verdict** : `module_high_risk` — à développer, mais avec la primitive standard 19.0 uniquement.
- **Voie** : module custom `lab_rental` (`odoo-developer`) ; Studio ne pose pas de contrainte SQL et le champ vit déjà dans le module.
- **Forme imposée** : `_check_days_positive = models.Constraint('CHECK(days >= 0)', "<msg fr>")` — `table_objects.py:79-101`, export `odoo/models/__init__.py:25`, modèle `account_payment.py:199`. `_sql_constraints` interdit (supprimé en 19.0).
- **Risque n°1** : sur base peuplée, une contrainte violée n'est **pas** posée et l'update reste vert (`registry.py:682-717`, log `info`/`warning` seulement).
- **Preuve copie `lab_client`** (lecture seule, `labctl shell`, 2026-09-09) : `lab.rental` total = **0**, `days < 0` = **0**, `days = 0` = 0 ; `pg_constraint` ne contient que pkey + 2 FK ; module `installed` 19.0.1.0.0 ; `days` nullable.
- **Réserve honnête** : la copie est **vide**, elle ne contient pas les données synthétiques annoncées → elle ne prouve rien sur le cas violant. La QA doit fabriquer une ligne `days = -3` (A7).
- **Risque QA test** : violation CHECK → curseur aborté ; encadrer par `self.env.cr.savepoint()` (`sql_db.py:217`), attendre `psycopg2.errors.CheckViolation` + `mute_logger('odoo.sql_db')` (`hr/tests/test_hr_version.py:46`), pas `ValidationError` (traduite seulement en RPC, `service/model.py:213`).
- **Critères** : A1 create refusée, A2 write refusée + valeur intacte, A3 zéro valide, A4 total 4×12.5=50, A5 location valide survit au rejet, A6 contrainte présente dans `pg_constraint`, A7 cas données violantes, A8 message + zéro `_sql_constraints`, A9 lint.
- **Hors périmètre** : vues, droits, `daily_rate`/`amount_total`, `kind` superflu dans `@api.depends`, `NOT NULL`, production.
