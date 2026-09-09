# Fragment QA — voie statique (conformité et revue du diff)

**Module** `lab_dispatch` · **série** 19.0 · **base du diff** commit `799eff1`

## Lint des fichiers touchés
`odoo-lint.sh --changed 799eff1 lab_dispatch` — 6 fichiers examinés.

- **1 erreur** : `__manifest__.py` — clé obligatoire `author` manquante.
  **Antérieure au changement** : vérifiée par `git show 799eff1:lab_dispatch/__manifest__.py`,
  la clé manquait déjà. Non introduite par cette tâche. Dette signalée, non corrigée :
  la valeur d'`author` est une décision du projet, elle ne s'invente pas.
- **0 erreur** sur les fichiers écrits ou modifiés par la tâche
  (`models/business.py`, `tests/*`, `migrations/19.0.1.0.1/*`).

## Contrôle non joué (annoncé, non masqué)
`ruff` est absent de l'hôte et de l'image `odoo-qa:19.0` : la voie 1/3 du lint
(règles bloquantes) a été **IGNORÉE**, pas passée. À rejouer à la clôture après
`odoo-stack.sh build`.

## Conformité de série 19.0
Aucune forme d'une autre série : pas d'`attrs`/`states`, pas de `_sql_constraints`,
pas de `self._cr`, pas de `name_get`, pas de `<tree>`. `api` importé et utilisé
(`@api.model`). Sécurité inchangée (`ir.model.access.csv` conservé, conforme à 19.0
et à la décision « pas de changement de droits »).

## Revue du diff
| Fichier | Nature | Observation |
|---|---|---|
| `models/business.py` | modifié | `action_recalculate` filtre `state == 'draft'` **avant** l'affectation ; `_get_snapshot_total` isole la règle des lignes annulées ; `_repair_draft_snapshots` n'écrit qu'en cas d'écart. Docstrings citant D-12. |
| `__manifest__.py` | modifié | version `19.0.1.0.0` → `19.0.1.0.1`, incrément **nécessaire** : c'est lui qui déclenche le script de migration. La release ne porte que ce point. |
| `migrations/19.0.1.0.1/post-recalcul_brouillons.py` | ajouté | `migrate(cr, version)`, `Environment(cr, SUPERUSER_ID, {})`, journalise le nombre de dossiers repris. Emplacement conforme à `odoo/modules/migration.py` (19.0). |
| `tests/common.py`, `tests/test_recalculate.py` | ajoutés | `@tagged('post_install', '-at_install')`, `Command.create`, aucun attribut nommé `run`. |

**Point de vigilance relevé et traité** : le socle de test n'utilise pas `write_date`
comme preuve de non-écriture — dans une transaction de test elle porte l'horodatage de
la transaction et reste identique même après un `write`. Un espion sur `write` est
utilisé à la place ; `write_date` n'est employée comme preuve que sur la copie, où les
passages sont dans des transactions distinctes.

**Verdict de la voie statique : VERT** (sous réserve de la dette `author` antérieure et
de `ruff` non joué, tous deux déclarés).
