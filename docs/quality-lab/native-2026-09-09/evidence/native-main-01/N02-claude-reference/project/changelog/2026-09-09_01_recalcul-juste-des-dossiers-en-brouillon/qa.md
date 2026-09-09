# QA de la release — Recalcul juste des dossiers en brouillon

## 2026-09-09 — Point 1 · Correction de `action_recalculate` et reprise des brouillons

**Niveau QA : renforcé** (la tâche modifie des données existantes) — trois voies jouées :
statique, exécution, copie client. Verdict unique : **VERT**.

### Contrôles

| Contrôle | Résultat |
|---|---|
| Test rouge avant correction (`--fresh`, tests ciblés) | **6 échecs / 7** — défaut prouvé |
| `odoo-lint.sh --changed 7589f93 lab_dispatch` | 0 erreur, 0 avertissement · ⚠️ partiel : `ruff` indisponible |
| Installation `-i lab_dispatch` sur base neuve `lab_qa` | ok |
| Mise à jour `-u lab_dispatch` | ok |
| Tests ciblés `/lab_dispatch:TestDispatchRecalculate` | **7/7 verts**, 0 erreur, 0 ignoré |
| ERROR/CRITICAL dans le log | 0 |
| Mise à niveau du module sur la copie `lab_client` | ok |
| Reprise, passe 1 | 1 enregistrement écrit (999,00 → 20,00) |
| Reprise, passe 2 rejouée | **0 enregistrement écrit** → idempotente |
| Validé id=2 sur la copie | 777,00 et `write_date` **inchangés** |

### Critères d'acceptation de la revue

| Critère | Couvert par | État |
|---|---|---|
| C1 — brouillon hors lignes annulées = 20,00 | `test_draft_excludes_cancelled_lines` | ✅ |
| C2 — validé garde 777,00 | `test_done_total_is_frozen` | ✅ |
| C3 — validé jamais réécrit (`write_date`) | `test_done_is_never_written` (date repoussée dans le passé pour être discriminante) | ✅ |
| C4 — sélection mixte sans exception | `test_mixed_selection` + contrôle croisé sur `lab_client` | ✅ |
| C5 — brouillon tout annulé = 0,00 | `test_draft_fully_cancelled` | ✅ |
| C6 — reprise idempotente | passes 1 et 2 sur `lab_client` (`reprise-passe2.txt` : 0 écriture) | ✅ |
| C7 — seuls les brouillons divergents écrits, validé à 777,00 | passe 1 sur `lab_client` | ✅ |

Cas limite supplémentaire : `test_empty_selection` (recordset vide) ✅.

### Anomalies

| Sévérité | Anomalie | Suite |
|---|---|---|
| Majeure (outillage, pas le code) | `labctl qa … --quick` rend un **faux vert** : sur une base clonée du gabarit, `odoo-test.sh` choisit `-u`, or le module n'y est pas installé → `-u` no-op, `updated_modules` vide, **0 test collecté** et verdict « propre ». Détecté en lisant le compte de tests. | Contournement : chemin complet (sans `--quick`). Leçon candidate pour `/odoo-feedback` |
| Mineure | `ruff` introuvable (hôte et image `odoo-qa:19.0`) → passe 1/3 du lint non exécutée | Signalé, lint déclaré partiel |
| Mineure | `__manifest__.py` sans clé `author` (6 à 9 WARNING/exécution) | Dette antérieure, fichier non touché, non corrigée sans demande |
| Mineure | `action_recalculate` réécrit un brouillon même à valeur inchangée | Conforme au contrat ; à arbitrer si un tracking est ajouté sur `snapshot_total` |

### Fragments détaillés
`.odoo-agents/flow-artifacts/recalcul-dispatch/` : `qa_high_static.md`, `qa_high_runtime.md`,
`qa_client.md`, `test-rouge-avant-correction.txt`, `reprise-passe1.txt`, `reprise-passe2.txt`,
`copie-selection-mixte.txt`, `inventaire-avant.txt`, `lint-changed.txt`, `qa-runtime-brut.txt`.

**Reste dû à la clôture (`/odoo-close`)** : recette complète (base neuve, suite entière,
désinstallation, mise à niveau), captures, guide et communication client, incrément de version du
manifest. Rien de tout cela n'est produit tant que la release est ouverte.
