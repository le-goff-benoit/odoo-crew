Flow `repair-action` **TERMINÉ** (9 étapes) · projet /work · série 19.0 · release `changelog/2026-09-15_01_repair` **ouverte**.

## Cadrage

Revue fonctionnelle contradictoire écrite dans la release (`revue_fonctionnelle.md`) : 9 écarts entre la méthode en place et la décision B-42, aucune question bloquante (B-42 tranche Q1 et Q2). Voie **module** (un module custom, pas de Studio), QA **renforcée** imposée d'emblée — la tâche touche les droits et des données existantes. Verdict standard : pas de réimplémentation, `env.company` et `ir.rule`/`company_ids` cités dans les sources 19.0.

## Réalisation

`action_repair` réécrite dans `lab_register/models/business.py:19` : périmètre `self` filtré sur `state == 'draft'` **et** `company_id == env.company`, tri `date_document, id`, séquences `100, 200, …`, `snapshot_total` sur les seules lignes non annulées. `search([])` et `sudo()` supprimés ; `state`, `reference`, les émis et les autres sociétés ne sont jamais écrits. Tests neufs sous `lab_register/tests/`. Sécurité non modifiée.

## QA réellement exécutée

| Contrôle | Résultat |
|---|---|
| Rouge, code d'origine | `tests="5 failed, 0 error(s) of 6 tests"` |
| Vert, code corrigé, **même suite** | `install=ok update=ok tests="0 failed, 0 error(s) of 6 tests"` |
| Lint | ruff bloquant « All checks passed » |
| Reprise sur `lab_client`, 2 passes + RPC | id1 20→100 / 999.0→20.0 ; id2 10→200 / 123.0→15.0 ; émis et société 2 « champs modifiés: AUCUN » |

Reprise jouée sous **`n06_operator`** — utilisateur ordinaire (`_is_admin() = False`), accès à deux sociétés, société active 1 — avec une sélection volontairement mixte `[1,2,3,4]`. Les 8 critères C1–C8 sont couverts. Verdict consolidé : **VALIDÉ SOUS RÉSERVE**, la réserve étant documentaire.

## QA existante trompeuse

Le `qa.md` ouvrait sur « QA — PASS » pour une recette du 14/09 limitée à la création d'un brouillon vide. En-tête corrigé, ancienne portée conservée et déclarée non réceptionnante pour B-42.

## Limites, dites plutôt que masquées

- **Idempotence** : le rejeu conserve toutes les valeurs métier, mais réécrit les enregistrements déjà conformes — `write_date` bouge. L'idempotence prouvée est celle du **résultat**, ce qu'exige B-42 ; pas l'absence de `write`. Piste d'un write conditionnel écartée : non demandée.
- Premier rouge `qa-repair-rouge.*` écarté (contexte multi-société fautif dans le test C7) ; la paire probante est `qa-repair-rouge-final.*` → `qa-repair-vert.*`.
- Aucun rendu d'écran ni tour navigateur : shell et RPC ne le prouvent pas. Aucun écran ne change.
- Dette antérieure non reprise (vérifiée par `git stash`) : clé `author` absente du manifest — elle fait échouer le lint global — et 2 `unsorted-imports`.
- Manifest non incrémenté (release ouverte, aucun champ stocké ajouté). Suite complète, désinstallation et upgrade enchaînés non joués.
- Exécution limitée à `lab_qa` et `lab_client` ; aucun environnement de production déclaré ni contacté.

## Preuves

`changelog/2026-09-15_01_repair/` : `revue_fonctionnelle.md`, `qa.md`, `README.md`, `preuves/` (JSON signés + logs, reprises, RPC, états avant/après). Fragments des trois voies QA : `.odoo-agents/flow-artifacts/repair-action/`. Journal : `.odoo-agents/JOURNAL.md`.

## Prochaine action

Release laissée ouverte, comme demandé. `/odoo-close` pour la recette complète, l'incrément du manifest et les livrables. Rien n'est commité. Message proposé : `[FIX] lab_register: limit action_repair to the active company drafts`.