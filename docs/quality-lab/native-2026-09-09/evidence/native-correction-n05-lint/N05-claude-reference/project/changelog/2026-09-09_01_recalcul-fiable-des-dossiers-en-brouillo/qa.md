# QA de tâche — 2026-09-09 · point n°1 · niveau **sensible** (données existantes)

**Module** `lab_dispatch` · **série** 19.0 · **bases** `lab_qa` (tests), `lab_client` (copie synthétique)
**Trois voies QA** : statique, exécution, copie client. Fragments dans
`.odoo-agents/flow-artifacts/recalc-dispatch/`.

## Contrôles

| Contrôle | Commande | Résultat |
|---|---|---|
| Test rouge du défaut | `qa --quick --tags /lab_dispatch:TestDispatchRecalculate` | **4 échecs / 5** avant correction — `preuves/01_test_rouge.log` |
| Tests ciblés, base neuve | `qa --quick --fresh --tags …` | **5/5 verts** — `preuves/06_tests_verts.log` |
| Installation / mise à jour | `qa --quick --update` | `install=ok update=ok` — `preuves/07_install_update.log` |
| Lint (ruff, config 19.0) | `lint lab_dispatch` | **vert** sur le diff ; 1 erreur de dette antérieure — `preuves/05_lint.log` |
| Reprise sur la copie, passe 1 | `shell reprise_brouillons.py` | 2 modifiés — `preuves/03_reprise_passe1.log` |
| Reprise sur la copie, passe 2 | idem | **0 modifié (idempotent)** — `preuves/04_reprise_passe2.log` |
| Comportement réel sur la copie | `shell reprise/verif_copie.py` | sélection mixte OK, validé intact — `preuves/08_verif_copie.log` |

## Critères d'acceptation de la revue

| # | Critère | Couvert par | État |
|---|---|---|---|
| C1 | Lignes annulées exclues du total d'un brouillon | `test_draft_excludes_cancelled_lines` (rouge → vert) | ✅ |
| C2 | Dossier validé jamais recalculé | `test_done_is_never_recalculated` (total + `write_date`) | ✅ |
| C3 | Sélection mixte sans erreur | `test_mixed_selection` + rejeu réel sur `lab_client` | ✅ |
| C4 | Reprise des brouillons de la copie | passe 1 : 999.0 → 20.0 et 20.004 → 20.0 | ✅ |
| C5 | Reprise idempotente | passe 2 : 0 modification | ✅ |
| C6 | `LEGACY_DONE` et les états intacts | 777.0 avant/après les deux passes ; aucun état changé | ✅ |

## Dette antérieure et observations (ne masquent aucun défaut introduit)

1. **Dette antérieure — `__manifest__.py` sans clé `author`** : erreur de lint présente au commit de
   base `d6b5c10`, hors diff de la tâche. Non corrigée pour ne pas inventer une valeur d'éditeur ;
   **à arbitrer à la clôture**. C'est le seul point rouge du lint complet.
2. **Observation** : recalculer un brouillon déjà conforme met à jour sa `write_date` (assignation
   du même flottant). Sans effet sur D-12, à connaître si un suivi de modification est branché.
3. **Incohérence assumée** : `LEGACY_DONE` porte 777.0 alors que ses lignes valent 20.0 — Q1 de D-12
   la fige délibérément. Ce n'est pas une anomalie à corriger.
4. **Portée de la reprise** : jouée sur `lab_client` uniquement, comme autorisé. Son emballage en
   script de migration (`migrations/`) pour un déploiement réel n'est pas fait — la version du
   manifest s'incrémente à la clôture, c'est là que la question se tranche.

## Verdict

**VALIDÉ** — les 6 critères d'acceptation sont satisfaits par une exécution réelle, sur base neuve
pour les tests et sur la copie pour la reprise. Aucune régression introduite ; un point de dette
antérieure reste ouvert pour la clôture.
