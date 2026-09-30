# Matrice des séries — ce qui change d'une version d'Odoo à l'autre

> Le guide `ODOO19_STYLE_GUIDE.md` décrit la **19.0**. Ce fichier dit ce qui
> vaut sur les autres séries. Un module ne s'écrit ni ne se relit avec les
> règles d'une série qui n'est pas la sienne : `_sql_constraints` est la forme
> **correcte** en 18.0 et une **erreur** en 19.0, `models.Constraint` l'inverse.
>
> Chiffres établis par comptage direct dans `~/odoo-sources/`.

## Série cible : comment elle est déterminée

`scripts/odoo_series.py`, dans cet ordre :

1. `--series` sur la ligne de commande, ou `$ODOO_SERIES` ;
2. `.odoo-agents/config` à la racine du projet (`series = 18.0`) ;
3. le préfixe de `version` dans le `__manifest__.py` (`18.0.3.13.1` → `18.0`) ;
4. `19.0` par défaut.

**Le premier réflexe d'un agent, avant de lire ou d'écrire une ligne, est de
connaître la série du module.** Tous les scripts l'affichent en tête de sortie.

## Matrice des formes attendues

| Sujet | 17.0 | 18.0 | 19.0 | 19.4 (saas~19.4) | 20.0 |
|---|---|---|---|---|---|
| Vue liste | `<tree>` | `<list>` | `<list>` | `<list>` | `<list>` |
| Conditions de vue | `invisible="expr"` | idem | idem | idem | idem |
| `attrs=` / `states=` | supprimés | supprimés | supprimés | supprimés | supprimés |
| Chatter | `<div class="oe_chatter">` | `<chatter/>` | `<chatter/>` | `<chatter/>` | `<chatter/>` |
| Nom affiché | `_compute_display_name` | idem | idem | idem | idem |
| Contrainte SQL | `_sql_constraints` | `_sql_constraints` | `models.Constraint` | `models.Constraint` | `models.Constraint` |
| Index | `index=` sur le champ | idem | `models.Index` / `models.UniqueIndex` | idem | idem |
| Domaines | listes polonaises | listes | objet `Domain` | objet `Domain` | objet `Domain` |
| Commandes x2many | `Command.*` | `Command.*` | `Command.*` | `Command.*` | `Command.*` |
| Traduction contextuelle | `_()` | `_()` / `self.env._()` | idem | idem | idem |
| RPC lecture seule | — | `@api.readonly` | `@api.readonly` | `@api.readonly` | `@api.readonly` |
| Curseur / contexte | `self._cr`, `self._context` tolérés | tolérés | `self.env.cr`, `self.env.context` | idem | idem |
| Catégorie de groupe | `category_id` | `category_id` | `res.groups.privilege` | idem | idem |
| Groupes d'un utilisateur | `groups_id` | `groups_id` | `group_ids` | `group_ids` | `group_ids` |
| Utilisateurs d'un groupe | `users` | `users` | `user_ids` | `user_ids` | `user_ids` |
| Droits d'accès | `ir.model.access.csv` | idem | idem | **`ir.access.csv`** | `ir.access.csv` |
| Règles d'enregistrement | `ir.rule` | `ir.rule` | `ir.rule` | **fusionnées dans `ir.access`** | fusionnées dans `ir.access` |
| Contrat RH | `hr.contract` | `hr.contract` | **`hr.version`** | `hr.version` | `hr.version` |
| Éditeur HTML | `web_editor` | `web_editor` | **`html_builder`** | `html_builder` | `html_builder` |
| Frontend public | `publicWidget` | `publicWidget` | **`Interaction`** | `Interaction` | `Interaction` |
| Cache ORM | `@tools.ormcache` | idem | idem | **`@api.ormcache`** | `@api.ormcache` |
| Vider le cache ORM | `registry.clear_cache()` | idem | idem | **`env.transaction.invalidate_ormcache()`** | idem |
| Binaire depuis un fichier XML | `type="base64"` | idem | idem | **`type="bytes"`** (19.3) | `type="bytes"` |
| `_rec_names_search` | liste | liste | liste | liste | **tuple** |
| `Query.add_where` / `select` / `order` | chaîne ou `SQL` | idem | idem | idem | **`SQL` seulement** |
| Python / PostgreSQL minimum (`MIN_PY_VERSION` / `MIN_PG_VERSION`) | 3.10 / non fixé | 3.10 / non fixé | 3.10 / 13 | **3.12 / 16** | 3.12 / 16 |

Preuves de datation — **nombre de fichiers d'`addons/` contenant le motif**,
relevé le 2026-09-02, colonne 20.0 le 2026-09-30 (les colonnes antérieures,
recomptées ce jour-là, sont inchangées). Unité homogène sur toute la table, reproductible par :

```bash
cd ~/odoo-sources
grep -rl "<motif>" <série>/addons --include="*.xml" | wc -l    # motifs de vue
grep -rl "<motif>" <série>/addons --include="*.py"  | wc -l    # motifs Python
```

⚠️ Ne pas écrire `grep -rl -- "<motif>" … --include=…` : après `--`, l'option
`--include` devient un nom de fichier et le filtre saute (tous les fichiers sont
comptés — 489 `<tree` au lieu de 389 en 17.0).

| Motif | 17.0 | 18.0 | 19.0 | 19.4 | 20.0 |
|---|---|---|---|---|---|
| `<tree` (`*.xml`) | 389 | 0 | 0 | 0 | 0 |
| `oe_chatter` (`*.xml`) | 71 | 1 | 0 | 0 | 0 |
| `<chatter/>` (`*.xml`) | 0 | 64 | 68 | 69 | 69 |
| `_sql_constraints` (`*.py`) | 158 | 172 | 1 | 1 | 1 |
| `models.Constraint(` (`*.py`) | 0 | 0 | 176 | 195 | 201 |
| `self.env._(` (`*.py`) | 1 | 116 | 263 | 523 | 622 |
| `security/ir.model.access.csv` | 205 | 224 | 219 | **0** | 0 |
| `security/ir.access.csv` | 0 | 0 | 0 | **223** | 226 |
| `static/src/public/interaction.js` | absent | absent | présent | présent | présent |
| `registry\.clear_cache\(` (`*.py`) | 31 | 33 | 33 | **0** | 0 |
| `transaction\.invalidate_ormcache\(` (`*.py`) | 0 | 0 | 0 | **30** | 34 |
| `@tools\.ormcache` ou import `ormcache` depuis `odoo.tools` (`*.py`) | 18 | 15 | 18 | **0** | 0 |
| `@api\.ormcache` (`*.py`) | 0 | 0 | 0 | **16** | 15 |
| `type="base64"` (`*.xml`) | 79 | 80 | 89 | **0** | 0 |
| `type="bytes"` (`*.xml`) | 0 | 0 | 0 | **118** | 122 |
| `_rec_names_search = [` (`*.py`) | 24 | 28 | 29 | 31 | **2** |
| `_rec_names_search = (` (`*.py`) | 0 | 0 | 0 | 0 | **32** |

La bascule des droits d'accès en 19.4 est la plus nette de la table : 219 → 0
d'un côté, 0 → 223 de l'autre. Elle est confirmée par le script de migration
officiel `19.4/odoo/upgrade_code/19.4-00-ir-access.py`.

## 19.0 n'est pas figée : les séries saas~19.x

Le poste héberge aussi `19.1` (`saas~19.1`) et `19.4` (`saas~19.4`). Elles ne
sont pas de simples correctifs : elles déplacent des règles du guide.

| Changement | Série | Effet sur un module custom |
|---|---|---|
| **`ir.access` unifie ACL et record rules** | 19.4 | `security/ir.model.access.csv` → `security/ir.access.csv`, colonnes `id,name,model_id,group_id/id,operation,domain` où `operation` est un sous-ensemble de `crud` et `domain` remplace l'`ir.rule`. 223 modules 19.4 en portent un ; plus aucun `ir.model.access.csv` dans le standard. Migration : `odoo/upgrade_code/19.4-00-ir-access.py`. |
| `registry.clear_cache` → `transaction.invalidate_ormcache` | 19.4 | tout appel de vidage de cache est à renommer. |
| `type="base64"` → `type="bytes"` dans les données XML | 19.3 | champs binaires chargés depuis un fichier. |
| Auto-fermeture des `<t>` et xpath sur `t-call` | 19.1 | templates QWeb. |
| Refonte des groupes de comptes | 19.3 | plans comptables localisés. |
| `ruff.toml` différent de celui de la 19.0 | 19.1+ | la config lint officielle a bougé. |

Conséquence pratique : **écrire « Odoo 19 » ne suffit pas.** Un module destiné à
Odoo Online / SaaS tourne sur la version que sert l'instance, pas sur la 19.0 :
la lire sur l'instance (`/odoo-env`), ne pas la supposer.

## 20.0 : la stable qui suit les saas~19.x

`20.0` (`version_info = (20, 0, 0, FINAL, 0, '')`, sources du 2026-09-30) reprend
**tout** ce que les saas~19.x ont changé : ses `odoo/upgrade_code/` reprennent
les scripts de la 19.4 (les outils de migration Owl 3 y sont révisés), plus un. Un module 19.0 qui monte en 20.0 subit
donc d'un coup la refonte `ir.access`, le cache ORM et `type="bytes"`.

| Changement | Depuis | Effet sur un module custom |
|---|---|---|
| Tout le § saas~19.x ci-dessus (`ir.access`, `invalidate_ormcache`, `type="bytes"`, `t-call`…) | 19.1 → 19.4 | idem : 226 modules 20.0 portent un `ir.access.csv`, aucun `ir.model.access.csv`. |
| `ormcache` s'importe de `odoo.api` : `@api.ormcache` | 19.4 | l'import par `odoo.tools` passe par un `__getattr__` qui lève un `DeprecationWarning` (« Since 20.0 import ormcache from odoo.api »). `ormcache_context` n'existe plus. |
| `_rec_names_search` en tuple | 20.0 | `upgrade_code/19.5-00-tuple-rec_names_search.py`. Une liste reste acceptée (`Collection[str]`) : forme de style, pas une panne. |
| `Query` n'accepte plus que du `SQL` | 20.0 | `add_where`, `select`, `order` avec une chaîne, `join` / `left_join` : `DeprecationWarning` (`odoo/orm/query.py`). Utiliser `SQL(...)` et `TableSQL.join` / `add_join`. |
| `type="base64"` en XML | 19.3 | accepté mais `DeprecationWarning` « Since 20.0, use type=bytes » (`odoo/tools/convert.py`). |
| Python ≥ 3.12, PostgreSQL ≥ 16 | 19.4 | `release.py` ; image Docker officielle `odoo:20.0` publiée (`20.0-20260926`). |
| `ruff.toml` propre à la 20.0 | 20.0 | exige ruff ≥ 0.16.1 ; ignore en plus `PLW0717`, `RUF075`, `RUF105`, `RUF201`, `SIM105`, `SIM109` ; `TID252` (imports relatifs) n'est plus ignorée — conseillée, pas encore imposée par le runbot : `odoo-lint.sh` la tient hors de la passe bloquante. |

Un module ne passe pas de 19.0 à 20.0 par simple changement de préfixe de
version : `odoo-lint.sh --series 20.0 <module>` chiffre l'écart.

## Modules supprimés

`19.0` (par rapport à 18.0) : `hr_contract`, `hr_holidays_contract`,
`hr_work_entry_contract`, `web_editor`, `membership`, `website_membership`,
`product_images`, `sale_async_emails`, `hw_*`, `pos_six`, `pos_paytm`,
`pos_viva_wallet`, `pos_epson_printer`, `auth_totp_mail_enforce`,
`payment_razorpay_oauth`, `website_jitsi`, `website_event_meet*`.

`19.4` retire encore, entre autres : `base_iban`, `hr_org_chart`, `hr_hourly_cost`,
`hr_homeworking*`, `hr_work_entry_holidays`, `iot_base`, `iot_box_image`,
`delivery_mondialrelay`, `website_sale_wishlist` et ses satellites,
`account_peppol_response`. Et en ajoute : `printer`, `populate`, `mail_tracking`,
`pos_stock`, `purchase_alternative*`, `base_report_paper_muncher`…

`20.0` retire en plus (par rapport à 19.4) : **`stock_picking_batch`** (le modèle
`stock.picking.batch` est dans `stock`), **`base_vat`** (contrôle TVA / VIES dans
`base`, `res.partner._check_vat`), `delivery_stock_picking_batch`,
`l10n_latam_base`, `portal_address_extended`, `transifex`, les `l10n_tr_nilvera*`.
Côté enterprise : **`industry_fsm`** et ses satellites (le service sur site passe
par `planning_field_service`, « Field Service » ; `is_fsm` n'existe plus),
`stock_barcode_picking_batch`, `quality_control_picking_batch`,
`hr_work_entry_attendance`, `pos_blackbox_be`, `ai_app`.

Où sont passés les modèles des modules fusionnés (vérifié dans les sources 20.0) :
`hr_org_chart`, `hr_hourly_cost`, `hr_homeworking` → `hr` ;
`website_sale_wishlist` (`product.wishlist`), `website_sale_comparison`
(`product.attribute.category`) → `website_sale` ; `base_iban` → `validate_iban`
dans `account/tools/` (19.4) puis `odoo/tools/bank_account_number.py` (20.0).
Ces remplacements sont portés par `odoo_series.REPLACEMENTS` : le lint les cite
quand un manifest dépend d'un module retiré.

La liste exacte se recalcule, elle ne se mémorise pas. Compter les
`__manifest__.py`, pas les dossiers : un dossier retiré peut subsister avec ses
seuls `i18n/` ou `static/` (`19.4/addons/website_sale_comparison`) :

```bash
mods() { ls ~/odoo-sources/$1/addons/*/__manifest__.py | xargs -n1 dirname | xargs -n1 basename | sort; }
comm -23 <(mods 19.4) <(mods 20.0)     # retirés
comm -13 <(mods 19.4) <(mods 20.0)     # ajoutés
```

## Ce que l'outillage fait de la série

| Script | Comportement |
|---|---|
| `odoo_lint.py` | chaque motif est daté (`since` / `before`) : `_sql_constraints` n'est une erreur qu'à partir de la 19.0, `models.Constraint` en est une avant. `--series X` force la comparaison — utile pour chiffrer une migration. |
| `odoo-lint.sh` | annonce la série, choisit le `ruff.toml` de la série (repli sur le plus proche publié). |
| `odoo-stack.sh` / `odoo-test.sh` | image `odoo-qa:<série>`, projet compose, volumes, base et sources enterprise propres à la série. Deux séries cohabitent. |
| `odoo-project-scan.py` | inscrit la série détectée dans le `PROJECT.md` du projet. |

Chiffrer une migration revient donc à comparer deux passes :

```bash
odoo-lint.sh <module>                 # dette réelle, dans sa série
odoo-lint.sh --series 19.0 <module>   # ce que coûterait la montée en 19.0
odoo-lint.sh --series 20.0 <module>   # … ou en 20.0
```
