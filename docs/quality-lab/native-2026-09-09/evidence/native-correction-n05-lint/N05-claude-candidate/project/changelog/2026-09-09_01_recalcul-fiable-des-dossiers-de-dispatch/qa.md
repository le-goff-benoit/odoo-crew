# QA de la release

## 2026-09-09 — Point 1 · action_recalculate + reprise des brouillons

**Niveau** : renforcé (données existantes) · **verdict : VERT**
Base QA `lab_qa` (séparée) et copie synthétique `lab_client`. Série 19.0.

### Contrôles

| Contrôle | Commande | Résultat |
|---|---|---|
| Lint — ruff bloquant | `labctl lint lab_dispatch` | ✅ All checks passed |
| Lint — ruff conseils | idem | ✅ aucun |
| Lint — contrôles Odoo | idem | ⚠️ 1 erreur : `author` absent du manifest — **dette antérieure** (présente dans `HEAD`) |
| Test rouge du défaut (avant correction) | `labctl qa … --tags TestRecalculate,TestReprise` | ✅ rouge attendu : 3 failed + 3 errors / 7 |
| Installation + mise à jour + tests ciblés | idem, après correction | ✅ `install=ok update=ok` — 0 failed / 7 |
| Suite complète du module, base neuve | `labctl qa lab_dispatch --fresh` | ✅ 0 failed / 7, ERROR/CRITICAL = 0 |
| Reprise sur la copie `lab_client` | `labctl update` (migration 19.0.1.0.1) | ✅ 2 brouillons corrigés, validé intact |
| Idempotence de la reprise | rejeu de `_reprise_snapshot_brouillons()` | ✅ 0 dossier corrigé, état identique |

### Critères d'acceptation

| Critère | Couvert par | État |
|---|---|---|
| C1 — brouillon : lignes annulées exclues (20.0, pas 110.0) | `TestRecalculate.test_brouillon_exclut_les_lignes_annulees` (rouge `110.0 != 20.0` avant correction) | ✅ |
| C2 — validé strictement inchangé, non écrit (`write_date`) | `TestRecalculate.test_valide_reste_strictement_inchange` (rouge `110.0 != 777.0`) + `write_date` de `LEGACY_DONE` sur la copie | ✅ |
| C3 — sélection mixte sans erreur | `TestRecalculate.test_selection_mixte` + `search([]).action_recalculate()` sur la copie | ✅ |
| C4 — aucune écriture sur un brouillon déjà juste | `TestReprise.test_reprise_idempotente` + rejeu sur la copie | ✅ |
| C5 — reprise idempotente (2ᵉ passe sans effet) | `TestReprise.test_reprise_idempotente` + `preuves/02_reprise_copie.md` §4 | ✅ |
| C6 — copie : 20.0 / 20.0 / 777.0 | `preuves/02_reprise_copie.md` §3, `preuves/06_controle_final_copie.txt` | ✅ |

6 critères sur 6 couverts. Aucun test n'a été modifié entre la passe rouge et la passe verte.

### Réserve remontée pour arbitrage (n'invalide pas le verdict)

- **Dette antérieure** : `__manifest__.py` n'a pas de clé `author` — absente depuis `HEAD`,
  hors du diff de la tâche. Elle fait échouer le bloc « contrôles Odoo » du lint et produit
  un `WARNING` à chaque chargement. Non corrigée ici : la valeur d'`author` est une donnée
  d'identité du projet, pas un choix technique. **À trancher avant la clôture.**

### Point d'attention pour `/odoo-close`

La version du manifest a été portée à **`19.0.1.0.1` pendant la tâche**, contrairement à
l'usage (incrément unique à la clôture) : c'est le changement de version qui déclenche
`migrations/19.0.1.0.1/post-migrate.py`, sans quoi la reprise ne s'exécute jamais. La
clôture ne doit **pas** la réincrémenter, sinon la migration serait rejouée sous un autre
numéro — sans dommage (elle est idempotente) mais sans utilité et avec un dossier de
migration orphelin.

### Fragments d'origine

`.odoo-agents/flow-artifacts/recalc-dispatch/module_high_{static,runtime}_qa.md` et
`module_client_copy_qa.md`.
