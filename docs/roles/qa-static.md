# Procédure — qa-static

Chargement conditionnel depuis le profil canonique. Les chemins `docs/…` et
`roles/…` sont relatifs à `~/.odoo19-agents/`.

## Étape 1 — Conformité statique

```bash
# Release ouverte : ne juger que ce qui a été touché depuis l'ouverture.
~/.odoo19-agents/scripts/odoo-lint.sh --changed "$(cat changelog/<release>/.base)" <chemin_du_module>
# Module entier (module neuf, ou demande explicite).
~/.odoo19-agents/scripts/odoo-lint.sh <chemin_du_module>
```

Sur un module existant, **commence par `--changed`** : les anomalies
antérieures ne sont pas ton sujet. Tu ne remontes une anomalie préexistante
que si le code livré s'appuie dessus. Mentionne leur nombre, sans les détailler.

Le script enchaîne compilation, `ruff` (config Odoo), XML, manifest, CSV de
sécurité, motifs interdits **dans la série du module**. Il annonce la série en
tête : si elle est fausse, tout ce qui suit l'est aussi — corrige
`.odoo-agents/config` ou passe `--series` avant de continuer.

Lis sa sortie, puis complète par une revue humaine **du diff** :

**Manifest** — `name`, `author`, `license` ; `version` préfixée par la série ;
chaque fichier de `data` existe, ordre sécurité → report → data → wizard →
views → menus ; aucune dépendance vers un module absent de la série (sur un
projet 18.0, `hr_contract` est légitime : ne le remonte pas) ; bundles d'assets
valides.

**Python** — ordre des membres, `_description`, `@api.model_create_multi`,
`super()` nu, `@api.ondelete` ; computes avec `@api.depends` complet et
assignation sur tous les chemins ; `models.Constraint` (19.0+) ou
`_sql_constraints` (avant) — jamais l'inverse ; `Command` ; `_()` sans
f-string ; pas de `search`/`write` en boucle, pas de SQL brut évitable, pas de
`sudo()` non justifié ; `self.env.cr` (bloquant en 19.0, remarque avant).

**XML** — pas d'`attrs`/`states` (17.0+) ; `<list>` et `<chatter/>` (18.0+) ;
héritages ancrés sur un nom ; `noupdate="1"` sur les données modifiables.

**Sécurité — bloquant** — chaque modèle non transient a une ligne d'accès
(`ir.model.access.csv` jusqu'en 19.1, `ir.access.csv` dès 19.4) ; pas de droit
de suppression gratuit ; règle multi-société sur tout `company_id` ; groupes
via `privilege` (19.0+) ou `category_id` ; `group_ids`/`user_ids` en 19.0+.

**Tests** — `tests/__init__.py` importe chaque `test_*.py` ; les contraintes
sont testées ; les droits le sont s'il y a des groupes ; aucun attribut `run`
sur une classe de test.

---
