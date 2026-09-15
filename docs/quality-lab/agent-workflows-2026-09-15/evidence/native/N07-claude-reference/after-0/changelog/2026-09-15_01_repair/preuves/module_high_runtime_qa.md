# Fragment QA — voie exécution (module_high_runtime_qa)

Base QA `lab_qa`, séparée de la copie `lab_client`. Outil : `/bridge/labctl qa` (odoo-test.sh 19.0).
Les journaux complets restent du côté du pont (chemins `/tmp/...` inaccessibles depuis le projet) ;
les sorties intégrales de chaque commande sont conservées dans `changelog/2026-09-15_01_repair/preuves/`.

## Rouge avant vert — les tests prouvent le défaut
Suite écrite **avant** la correction, rejouée sur le code d'origine restauré depuis `HEAD`
(`git show HEAD:lab_preparation/models/business.py`) le temps de la mesure :

`RECETTE module=lab_preparation db=lab_qa install=ko tests="9 failed, 0 error(s) of 11 tests" errors=10 failed=9`
Preuve : `preuves/tests_rouge_avant_correction.txt`

Les 9 rouges : `test_cron_computes_remaining_quantity`, `test_cron_never_goes_negative`,
`test_cron_keeps_manual_zero`, `test_cron_keeps_manual_partial`, `test_cron_freezes_done`,
`test_copy_resets_history`, `test_copy_of_done_is_a_fresh_draft`,
`test_remainder_creates_the_rest`, `test_remainder_without_rest_creates_nothing`.

Les 2 verts d'emblée sont assumés : `test_cron_is_idempotent` (le code fautif était idempotent
en écrasant toujours avec `ordered_qty`) et `test_remainder_requires_a_singleton` (`ensure_one()`
était déjà là). Ce sont des garde-fous de non-régression, pas des révélateurs de ce défaut-ci.

## Vert après correction
- Base **neuve** (`--fresh`), installation depuis zéro + tests :
  `RECETTE … install=ok tests="0 failed, 0 error(s) of 11 tests" errors=0 failed=0 skipped=0`
  → `preuves/tests_vert_base_neuve.txt`
- Mise à jour + tests ciblés : `RECETTE … install=ok update=ok tests="0 failed, 0 error(s) of 11 tests" errors=0`
  → `preuves/tests_vert_update.txt`
- Avertissements restants : uniquement `Missing 'author' key in manifest` (dette antérieure,
  voir voie statique). Aucun autre WARNING lié au module.

## Parcours par l'API publique réelle (XML-RPC, base lab_client)
`preuves/parcours_copie_rpc.txt` — chaque appel passe par un serveur neuf :
- `action_set_manual(20, 0)` → `true` ; relecture : `prepared_qty=0.0, manual=true`
  → **le zéro traverse le vrai RPC sans être confondu avec une absence de saisie**.
- `action_remainder(20)` → `[21]` ; source `state='done'`, `prepared_qty=0.0` **non écrasée** ;
  reliquat `ordered_qty=6.0, delivered_qty=0.0, prepared_qty=0.0, manual=false, state='draft',
  parent_id=[20, 'RPC reliquat']`.
- `unlink` des deux enregistrements de contrôle → `true` ; l'état final relu montre les 4 lignes
  de référence : la copie n'est pas polluée par la QA.

## Parcours complet dans le vrai shell Odoo (lab_client, transaction annulée)
`preuves/parcours_copie_shell.txt` — zéro manuel, duplication, reliquat, solde sans reste, puis cron :
```
ZERO    0.0 True draft
DUP     10.0 0.0 10.0 False draft
SOURCE  6.0 done
RELIQ   6.0 0.0 6.0 False draft QA reliquat
SANS    lab.preparation() done 0.0
ROLLBACK ok, total en base = 4
```
`DUP` ressort à 10 après le cron (commandé 10, livré remis à 0) : la duplication est bien une
demande neuve. `SANS` retourne un recordset vide et ne crée rien.

**Portée non prouvée par cette voie** : aucun rendu d'écran, aucun droit d'un autre utilisateur
(le module ne livre ni vue ni groupe ; seul l'admin synthétique est exercé).

**Verdict de la voie** : vert — rouge d'abord démontré, vert sur base neuve et en mise à jour,
contrat vérifié aussi à travers le vrai XML-RPC et le vrai shell.
