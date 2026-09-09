# QA — release 2026-09-09_01

## 2026-09-09 — Point 1 · Recalcul juste des dossiers et reprise des brouillons

**Module** `lab_dispatch` · **série** 19.0 · **niveau** renforcé (données existantes)
**Bases** `lab_qa` (neuve, tests) et `lab_client` (copie synthétique, reprise)
Fragments : `.odoo-agents/flow-artifacts/recalc-dispatch/module_high_{static,runtime}_qa.md`,
`module_client_copy_qa.md`. Preuves brutes : `preuves/`.

### Contrôles

| Contrôle | Résultat | Preuve |
|---|---|---|
| Test rouge avant correction | **4 FAIL + 3 ERROR / 7** — les deux défauts reproduits (110.0 au lieu de 20.0 ; validé écrasé 777 → 110) | `preuves/01_test_rouge.log` |
| Lint `--changed` (base `799eff1`) | 1 erreur, **antérieure** (`author` absent du manifest au commit de base) · **0 introduite** | voie statique |
| `ruff` (règles bloquantes) | **NON JOUÉ** — binaire absent de l'hôte et de l'image `odoo-qa:19.0` ; contrôle ignoré, pas passé | `preuves/02_test_vert.log` |
| Installation base neuve | ok | `preuves/02_test_vert.log` |
| Mise à jour du module | ok | idem |
| Tests ciblés | **7/7** (`0 failed, 0 error(s) of 7 tests`, ⏱ 5 s) | idem |
| Reprise sur la copie, passage 1 | migration `19.0.1.0.1` jouée, **2 dossiers repris** | `preuves/04`, `05` |
| Reprise sur la copie, passage 2 | **0 repris, 0 write, 3 `write_date` inchangées** | `preuves/06` |
| Sélection mixte sur la copie | aucune erreur, validé hors de la liste des écrits | `preuves/07` |
| Suite complète, désinstallation, tours | **non joués** — recette de clôture (`/odoo-close`) | — |

### Critères d'acceptation

| Critère | Couvert par | État |
|---|---|---|
| CA1 — brouillon hors lignes annulées → 20.0 | `test_draft_excludes_cancelled_lines` (rouge puis vert) | ✅ |
| CA2 — validé à 777.0 conservé **et non écrit** | `test_done_is_never_written` (espion sur `write`) | ✅ |
| CA3 — sélection mixte : brouillon recalculé, validé intact, sans erreur | `test_mixed_selection` + `preuves/07` sur la copie | ✅ |
| CA4 — brouillon tout annulé → 0.0 | `test_draft_fully_cancelled_is_zero` | ✅ |
| CA5 — LEGACY_DRAFT 999 → 20.0 et LEGACY_FRACTION 20.004 → 20.0 | `preuves/04`, `05` + `test_repair_fixes_drafts_only` | ✅ |
| CA6 — rejeu sans aucune écriture | `preuves/06` (0 repris, 0 write, `write_date` figées) + `test_repair_is_idempotent` | ✅ |
| CA7 — LEGACY_DONE : 777.0, `done`, `write_date` d'origine après les deux passages | `preuves/05`, `06` + `test_repair_never_touches_done` | ✅ |

7 critères sur 7 satisfaits.

### Arbitrages et réserves (aucune n'est un défaut introduit)

1. **Dette antérieure — `author` absent du manifest.** Présente au commit de base, elle
   produit l'unique erreur de lint et les 3 WARNING d'installation. Non corrigée : la valeur
   appartient au projet. À trancher à la clôture.
2. **`ruff` non installé.** Une des trois voies du lint n'a pas tourné. Dit explicitement
   plutôt que compté comme vert ; à rejouer après `odoo-stack.sh build`.
3. **Version du manifest incrémentée dès cette tâche** (`19.0.1.0.0` → `19.0.1.0.1`), par
   nécessité technique : sans incrément, Odoo ne joue pas le script de migration, donc pas
   de reprise. La release ne porte que ce point ; l'exception de la chaîne s'applique.
4. **Le bouton réécrit un brouillon déjà juste.** Conforme : D-12 n'exige l'absence
   d'écriture que pour les validés. La reprise automatique, elle, n'écrit qu'en cas d'écart.
5. **Idempotence : portée exacte de la preuve.** Prouvée pour un rejeu à données inchangées,
   par absence de `write` et non par simple égalité des montants. Un rejeu après modification
   d'une ligne recalculerait — c'est le comportement voulu, pas une non-idempotence.
6. **Point de méthode conservé** : `write_date` ne prouve rien dans un test unitaire (même
   horodatage de transaction) ; elle n'est utilisée comme preuve que sur la copie, entre
   transactions distinctes. Les tests s'appuient sur un espion posé sur `write`.

### Verdict

**VERT — point 1 validé.** Les deux défauts sont corrigés et prouvés par un test rouge
antérieur ; la reprise est jouée et idempotente sur `lab_client` ; les dossiers validés
n'ont reçu aucune écriture. Deux contrôles restent déclarés non joués (`ruff`, recette
complète) et une dette antérieure reste à arbitrer : aucun n'est masqué.
