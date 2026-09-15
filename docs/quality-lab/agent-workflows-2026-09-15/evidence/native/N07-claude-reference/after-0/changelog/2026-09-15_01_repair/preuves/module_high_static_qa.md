# Fragment QA — voie statique (module_high_static_qa)

Série appliquée par l'outil : **19.0** — conforme à `.odoo-agents/config`.
Commande : `/bridge/labctl lint lab_preparation` (le pont n'expose pas `--changed` ;
la release n'a pas de fichier `.base`, la distinction dette/diff est donc faite à la main
en comparant avec `git show HEAD:lab_preparation/__manifest__.py`).

## Résultat outillé
- `ruff` règles bloquantes (config Odoo 19.0) : **All checks passed**.
- `ruff` conseils (non bloquant) : 2 × `no-space-after-block-comment` — ce sont les
  marqueurs de section `#=== ACTION METHODS ===#` / `#=== BUSINESS METHODS ===#`, forme
  prescrite par `ODOO19_STYLE_GUIDE.md` l.168-174 et employée telle quelle par le standard
  (`~/odoo-sources/19.0/addons/sale/models/sale_order.py` l.52, 331, 846). Non retenu.
- Contrôles Odoo : **1 erreur — `__manifest__.py` : clé obligatoire `author` manquante**.
  **Dette antérieure, hors diff** : le manifest à `HEAD` ne portait déjà pas cette clé
  (`git show HEAD:lab_preparation/__manifest__.py`). Non corrigée (le rôle interdit de
  reprendre la dette sans demande) → **le lint du module reste rouge**, à traiter avant
  `/odoo-close`.

## Revue humaine du diff
- **Manifest** : `version` passe de `19.0.1.0.0` à `19.0.1.1.0`, préfixe de série correct ;
  l'incrément est ici obligatoire car il conditionne l'exécution du `post-migrate` de reprise.
  `data` inchangé, dépendance `base` seule, aucun bundle.
- **Python** : ordre champs → actions → métier avec marqueurs ; `_description` présent ;
  aucun `create`/`unlink` surchargé donc ni `@api.model_create_multi` ni `@api.ondelete` requis ;
  aucun compute, aucune contrainte, aucun `_()`, aucun f-string, aucun `sudo()`, aucun SQL.
  `_cron_prepare` écrit dans une boucle sur un `search` borné au domaine utile — acceptable
  au volume du modèle, signalé sans plus (le contrat ne fixe pas de volumétrie).
  `copy=False` porté par les champs plutôt qu'une surcharge de `copy_data` : forme la plus
  simple, validée dans les sources (`odoo/orm/models.py` l.5434-5436 — les champs `copy=False`
  sont exclus de `fields_to_copy` et retombent sur leur défaut).
- **XML** : aucun fichier XML dans le module.
- **Sécurité** : `ir.model.access.csv` inchangé, une ligne pour `lab.preparation` × `base.group_user` ;
  aucun groupe, aucun `company_id`, donc aucune règle multi-société attendue.
- **Tests** : `tests/__init__.py` importe `test_preparation` ; aucun attribut de classe `run` ;
  pas de contrainte ni de groupe à couvrir.

**Verdict de la voie** : conforme sur le diff livré ; une anomalie **antérieure** (clé `author`)
maintient le lint du module en rouge et doit être tranchée avant la clôture de la release.
