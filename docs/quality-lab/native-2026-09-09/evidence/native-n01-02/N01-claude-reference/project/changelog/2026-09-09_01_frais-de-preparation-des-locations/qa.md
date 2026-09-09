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

---

## 2026-09-09 — Point n°2 : forfait de préparation à 15 EUR dès 5 jours (D-03) — **VALIDÉ**

**Module** `lab_rental` · **série** 19.0 · **niveau QA** normal (aucun droit, aucune compta,
aucune facturation ; 0 enregistrement recompté sur `lab_client` avant et après mise à niveau)
**Bases** `lab_qa` (recréée), `lab_client` (copie synthétique, laissée intacte)

> **D-03 remplace D-02.** La QA du point n°1 ci-dessus reste vraie pour ce qu'elle a mesuré,
> mais elle **ne vaut plus comme preuve de livraison** : elle porte sur une règle morte. C'est
> cette section qui fait foi pour ce qui sortira de la release.

### Contrôles

| Contrôle | Commande | Résultat |
|---|---|---|
| Lint des fichiers touchés | `odoo-lint.sh --changed d3c9977e2f lab_rental` | ✅ ruff bloquant : 0 · contrôles Odoo : 0 erreur / 0 avertissement |
| Relecture du diff | 2 fichiers, périmètre de la spec | ✅ seuil en `>=`, aucune forme périmée 19.0, aucun écran, aucun champ |
| Installation base neuve | `labctl qa lab_rental --fresh --update --tags /lab_rental:TestPreparationFee` | ✅ `install=ok` |
| Mise à niveau `-u` | idem | ✅ `update=ok` |
| Tests ciblés | idem | ✅ **11/11** — `0 failed, 0 error(s) of 11 tests` |
| Les tests mordent (rouge avant correctif) | même suite sur la formule D-02 | ✅ **6/11 rouges** (62≠65, 52≠40, 112≠115, 30≠40, 12,0≠15,0) |
| Mise à niveau de la copie client | `labctl update` sur `lab_client` | ✅ 0 erreur |
| Comportement sur la copie client | témoins ORM + relecture SQL | ✅ **5/5** conformes, copie intacte (rollback) |
| ERROR / CRITICAL dans les logs | analyse `odoo-test.sh` | ✅ 0 |

Preuves : `preuves/lint_changed_d03.log`, `preuves/qa_tests_verts_d03.log`,
`preuves/qa_tests_rouges_avant_d03.log`, `preuves/verif_copie_lab_client_d03.{py,log}`,
`preuves/etat_lab_client_avant_d03.{py,log}`.
Fragments de voie : `.odoo-agents/flow-artifacts/frais-preparation-d03/module_{static,runtime}_qa.md`.

### Critères d'acceptation de la revue (point n°2)

| Critère | Couvert par | État |
|---|---|---|
| CA1 — location 5 j à 10 € → 65,0 (borne inclusive) | `test_rental_at_threshold_pays_the_fee` + témoin `lab_client` | ✅ |
| CA2 — location 4 j → 40,0 (l'ancien seuil D-02 ne s'applique plus) | `test_rental_at_former_threshold_pays_no_fee` + témoin | ✅ |
| CA3 — location 3 j → 30,0 | `test_rental_below_threshold_pays_no_fee` + témoin | ✅ |
| CA4 — location 10 j → 115,0 (forfait fixe, non multiplié) | `test_rental_above_threshold_pays_the_fee_once` + témoin | ✅ |
| CA5 — prêt 5 j → 50,0 (exclu à la borne) | `test_loan_at_threshold_pays_no_fee` + témoin | ✅ |
| CA6 — prêt 10 j → 100,0 | `test_loan_above_threshold_pays_no_fee` | ✅ |
| CA7 — recalcul 4 j → 5 j, puis disparition sur `kind = loan` | `test_fee_follows_days_and_kind_changes` | ✅ |
| CA8 — location vide → 0,0 | `test_empty_rental_totals_zero` | ✅ |
| CA9 — valeur stockée, 65,0 lu en SQL | `test_amount_total_is_stored_in_database` + témoins SQL | ✅ |
| CA10 — aucun écran, champ ni ligne de sécurité modifiés | diff : 2 fichiers Python, aucun XML, aucun CSV | ✅ |
| Hors CA — constantes conformes à D-03 (garde-fou) | `test_rule_constants_match_the_decision` | ✅ |
| Hors CA — durée négative ne franchit pas le seuil | `test_negative_days_stay_below_threshold` | ✅ |

**10 critères sur 10 couverts**, aucune reprise déclenchée.

### Anomalies

| Sévérité | Point | Suite |
|---|---|---|
| majeure — **à décider à la clôture** | Un changement de formule sur un champ **stocké** ne recalcule pas les lignes existantes. Sans objet aujourd'hui (`lab_client` : 0 enregistrement, recompté en SQL avant et après `-u`), mais une base cible peuplée garderait des totaux D-01 **ou D-02**. | Trancher à `/odoo-close` : `migrations/<version>/post-recompute.py` ou constat écrit. La réserve du point n°1 reste ouverte et vise maintenant D-03. |
| majeure — **traitée** | Le point n°1 était marqué VALIDÉ sur une règle morte ; le suivi du README aurait fait documenter 12 EUR / 4 jours à la clôture. | Point n°1 requalifié **REMPLACÉ par D-03** dans le suivi, sa QA conservée comme historique ; note de release ajoutée. |
| mineure — dette antérieure | `__manifest__.py` sans clé `author` : 1 anomalie de lint sur fichier non modifié, 9 WARNING au chargement. | Hors périmètre de la tâche ; à corriger à la clôture avec l'incrément de version. |
| mineure — outillage | Rappel : `odoo-test.sh --quick` rend un faux vert `of 0 tests` quand la base existe sans le module. Contourné ici par `--fresh --update`. | Leçon candidate déjà portée pour `/odoo-feedback`. |

### Ce qui n'a pas été joué (c'est la clôture qui le fera)
Suite complète du module, désinstallation, tours navigateur, captures, guide et communication
client : `/odoo-close`. **La release reste ouverte.** La communication de clôture ne doit
décrire que D-03 : D-02 n'a jamais quitté le laboratoire.
