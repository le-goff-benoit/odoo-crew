# Fragment QA renforcée — voie statique (point 2, D-03)

**Portée** conformité 19.0 et revue du diff. Aucune exécution de test dans ce fragment.

## Lint

`/bridge/labctl lint lab_rental` → **0 erreur, 0 avertissement, 0 info** (`lint.txt`).
Restent 9 `no-space-after-block-comment` dans la voie « conseils » non bloquante : ce sont les
séparateurs `#=== … ===#` du modèle, **dette antérieure** identique au point 1, non introduite par
ce diff.

## Revue du diff (`diff.patch`)

| Fichier | Changement | Verdict |
|---|---|---|
| `models/business.py` | `PREPARATION_FEE` 12.0 → **15.0**, `PREPARATION_FEE_MIN_DAYS` 4 → **5** ; docstring réécrite sur D-03 avec la filiation D-01 → D-02 → D-03 | conforme à la spec §7 |
| `__manifest__.py` | version 19.0.1.1.0 → **19.0.1.2.0** | requis par le risque n°1 de la revue |
| `migrations/19.0.1.2.0/post-migrate.py` | nouveau ; `add_to_compute` sur toutes les locations | pur recalcul, aucun autre champ écrit |
| `migrations/19.0.1.1.0/post-migrate.py` | **conservé, inchangé** | une base encore en 19.0.1.0.0 traverse les deux ; les deux sont des recalculs |
| `tests/test_preparation_fee.py` | 10 → **12 tests**, valeurs attendues réécrites sur D-03 | oracles tirés de `decisions/2026-09-09.md`, jamais de la méthode testée |

Conformité 19.0 : aucune forme périmée introduite (pas d'`attrs`, pas de `<tree>`, pas de
`_sql_constraints`, pas de `self._cr`). Le module n'a ni vue ni JS.

## Périmètre

Aucune vue, aucun droit, aucun champ, aucune dépendance ajoutés dans le diff — conforme au
« Hors périmètre » de la spec. Confirmé côté base par le fragment copie client.

## Point de vigilance transmis à la jointure

La logique n'a **pas** été rendue paramétrable, conformément à la revue §2. C'est la troisième
écriture de la même règle en deux jours : à reproposer au client, pas à décider ici.

**Fragment : conforme.**
