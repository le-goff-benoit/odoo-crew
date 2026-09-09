# QA de tâche — release 2026-09-09_01

## 2026-09-09 — Point n°1 · `action_recalculate` et reprise des brouillons

**Niveau : QA renforcée** (la tâche modifie des **données existantes** → validation
sur la copie client immédiate, sans attendre la clôture). Trois voies fusionnées :
`.odoo-agents/flow-artifacts/recalcul-brouillons/{qa_high_static,qa_high_runtime,qa_client}.md`.

### Contrôles

| Contrôle | Commande | Résultat |
|---|---|---|
| Lint des fichiers touchés | `odoo-lint.sh --changed <base> lab_dispatch` | ✅ ruff « All checks passed », contrôles Odoo 0 erreur / 0 avertissement (5 fichiers) |
| Test **rouge** avant correction | `labctl qa --quick --tags …TestLabDispatchRecalculate` | ✅ défaut reproduit : **5 échecs / 6** |
| Installation base neuve + tests ciblés | `labctl qa --quick --fresh --tags …` | ✅ install=ok · **6/6** · 0 ERROR · 0 WARNING · ⏱ 14s |
| Mise à jour base chaude + tests | `labctl qa --quick --update --tags …` | ✅ update=ok · **6/6** · ⏱ 4s |
| Mise à jour sur la copie `lab_client` | `labctl update` | ✅ sans erreur |
| Reprise des données, 2 passages | `labctl shell …/reprise_brouillons.py` ×2 | ✅ passe 1 `modifies=1`, passe 2 `modifies=0`, `valides_modifies=0` aux deux passes |
| Absence d'écriture sur un validé (copie) | `…/controle_ecritures.py` | ✅ `LEGACY_DONE` : `write_date == create_date` (jamais écrit) ; le brouillon, lui, l'a été → contrôle discriminant |

### Critères d'acceptation

| # | Critère | Couvert par | État |
|---|---|---|---|
| CA1 | Brouillon = somme des lignes non annulées | `test_draft_excludes_cancelled_lines` (+ `test_empty_and_fully_cancelled`) | ✅ |
| CA2 | Validé : total **et** absence totale d'écriture | `test_done_is_never_written` (espion sur `write`) + `write_date` sur la copie | ✅ |
| CA3 | Sélection mixte : brouillons recalculés, validés ignorés, sans erreur | `test_mixed_selection` (+ `test_empty_recordset_does_not_fail`) | ✅ |
| CA4 | Idempotence de la méthode | `test_recalculate_is_idempotent` | ✅ |
| CA5 | Reprise sur `lab_client` : 999 → 20, 777 intact, second passage sans changement | preuves `copie_01` à `copie_06` | ✅ |

**Test rouge → vert, mêmes tests** : les assertions qui échouaient sur le code
d'origine (`110.0 != 20.0`, `110.0 != 777.0`, `(110.0, 20.0) != (20.0, 777.0)`)
passent après correction. Le test de non-régression a réellement échoué avant.

### Réserves et arbitrages (non bloquants)

1. **`'author': 'Camptocamp'` ajouté au manifest** — clé obligatoire manquante
   (lint rouge + WARNING à chaque chargement). Hors périmètre strict de D-12 ;
   la valeur est à confirmer par l'humain.
2. **Idempotence « au bit près » des brouillons** — la reprise réécrit un
   brouillon à l'identique quand rien ne change (`write_date` bouge). D-12 exige
   l'absence d'écriture pour les **validés** seulement, et elle est prouvée.
   Garde-fou possible sur demande ; non fait (hors spec, arrondi `Float`).
3. **Dette antérieure** — `quantity`, `price` et `snapshot_total` sont des
   `Float` sans `digits`. Signalée en revue, non corrigée : hors périmètre.
4. **Reprise hors de cette copie** — le script n'a été joué que sur `lab_client`
   (copie synthétique locale). Toute exécution ailleurs relève d'une décision
   humaine explicite, opération par opération.
5. **Non joué à ce stade** (c'est la clôture qui le fait) : suite complète du
   module, désinstallation, base neuve intégrale, captures, guide.

### Verdict

**VALIDÉ** — 5 critères d'acceptation sur 5, aucun contrôle rouge.
