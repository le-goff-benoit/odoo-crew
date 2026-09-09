# QA de la release — Frais de préparation des locations

## 2026-09-09 — Point n°1 : forfait de préparation (D-02) — **VALIDÉ**

**Module** `lab_rental` · **série** 19.0 · **niveau QA** normal (aucun droit, aucune
compta, aucune facturation, aucune donnée existante — copie `lab_client` à 0 enregistrement)
**Bases** `lab_qa` (neuve), `lab_client` (copie synthétique)

### Contrôles

| Contrôle | Commande | Résultat |
|---|---|---|
| Lint des fichiers touchés | `odoo-lint.sh --changed d3c9977 lab_rental` | ✅ ruff bloquant : 0 · contrôles Odoo : 0 erreur / 0 avertissement |
| Installation base neuve | `labctl qa lab_rental --fresh --update` | ✅ `install=ok` |
| Mise à niveau `-u` | idem | ✅ `update=ok` |
| Tests ciblés | `--tags /lab_rental:TestPreparationFee` | ✅ **9/9** — `0 failed, 0 error(s) of 9 tests` |
| Les tests mordent (rouge avant correctif) | ancienne formule rejouée | ✅ **4/9 rouges**, restaurés ensuite |
| Comportement sur la copie client | `labctl update` + témoins ORM/SQL | ✅ 4/4 cas conformes, copie laissée intacte |
| ERROR / CRITICAL dans les logs | analyse `odoo-test.sh` | ✅ 0 |

Preuves : `preuves/lint_changed.log`, `preuves/qa_tests_verts.log`,
`preuves/qa_tests_rouges_avant_correctif.log`, `preuves/qa_faux_vert_quick_0_test.log`,
`preuves/verif_copie_lab_client.{py,log}`.

### Critères d'acceptation de la revue

| Critère | Couvert par | État |
|---|---|---|
| CA1 — location 4 j à 10 € → 52,0 (borne inclusive, Q1) | `test_rental_at_threshold_pays_the_fee` | ✅ |
| CA2 — location 3 j → 30,0 (pas de forfait sous le seuil) | `test_rental_below_threshold_pays_no_fee` | ✅ |
| CA3 — location 10 j → 112,0 (forfait fixe, non multiplié) | `test_rental_above_threshold_pays_the_fee_once` | ✅ |
| CA4 — prêt 4 j → 40,0 (Q2) | `test_loan_at_threshold_pays_no_fee` | ✅ |
| CA5 — prêt 10 j → aucun forfait | `test_loan_above_threshold_pays_no_fee` | ✅ |
| CA6 — recalcul au changement de `days` puis de `kind` | `test_fee_follows_days_and_kind_changes` | ✅ |
| CA7 — location vide → 0,0 | `test_empty_rental_totals_zero` | ✅ |
| CA8 — valeur bien stockée (lue en SQL) | `test_amount_total_is_stored_in_database` + témoins `lab_client` | ✅ |
| Hors CA — durée négative ne franchit pas le seuil | `test_negative_days_stay_below_threshold` | ✅ |
| Aucun écran modifié | diff : aucun XML, aucun champ nouveau | ✅ |

**8 critères sur 8 couverts.**

### Anomalies (aucune reprise déclenchée)

| Sévérité | Point | Suite |
|---|---|---|
| majeure — **à décider à la clôture** | Un changement de *formule* sur un champ stocké ne recalcule pas les lignes existantes. Sans objet aujourd'hui (`lab_client` : 0 enregistrement, vérifié en SQL), mais une base cible peuplée garderait d'anciens totaux. | Trancher à `/odoo-close` : script `migrations/<version>/post-recompute.py` ou constat écrit qu'il n'y a rien à reprendre. |
| mineure — dette antérieure | `__manifest__.py` sans clé `author` : 1 erreur de lint sur fichier non modifié, 9 WARNING au chargement. | Hors périmètre de la tâche ; à corriger à la clôture avec l'incrément de version. |
| mineure — outillage | `odoo-test.sh --quick` rend `✅ tests OK` avec `of 0 tests` quand la base existe sans le module (`-u` au lieu de `-i`), y compris avec `--fresh`. Faux vert. | Leçon candidate pour `/odoo-feedback` (voir le journal). |

### Ce qui n'a pas été joué (c'est la clôture qui le fera)
Suite complète du module, désinstallation, tours navigateur, captures, guide et
communication client : `/odoo-close`. **La release reste ouverte**, comme demandé.
