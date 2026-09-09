# Implémentation — correction de action_recalculate (sensible : données existantes)

## Fichiers
- `lab_dispatch/models/business.py` — filtre `state == 'draft'`, exclusion des lignes `cancelled`.
- `lab_dispatch/migrations/19.0.1.0.1/post-migrate.py` — reprise idempotente des brouillons (nouveau).
- `lab_dispatch/__manifest__.py` — version 19.0.1.0.0 → 19.0.1.0.1 (obligatoire : sans incrément, la migration ne se déclenche pas ; release à un seul point).
- `lab_dispatch/tests/{__init__,common,test_recalculate}.py` — 5 tests (nouveaux).

## Test rouge avant correction
`.odoo-agents/flow-artifacts/recalc-dispatch/test_rouge.log`
`RECETTE … tests="4 failed, 0 error(s) of 5 tests"` — 110,00 au lieu de 20,00 (lignes annulées comptées),
777,00 écrasé par 110,00 (dossier validé réécrit).

## Après correction
`.odoo-agents/flow-artifacts/recalc-dispatch/test_vert.log`
`RECETTE module=lab_dispatch db=lab_qa install=ok update=ok tests="0 failed, 0 error(s) of 5 tests"`

## Reprise sur la copie lab_client
`.odoo-agents/flow-artifacts/recalc-dispatch/reprise.txt` (+ `update_passe1.log`, `update_passe2.log`).
Deux passes de la même migration, valeurs identiques ; LEGACY_DONE jamais réécrit.

## Lint
`odoo-lint.sh --changed` : 1 erreur, `author` manquant dans le manifest — dette antérieure au commit de base
(vérifié : `git show 799eff1:lab_dispatch/__manifest__.py`). Non corrigée volontairement (règle du rôle), signalée.
