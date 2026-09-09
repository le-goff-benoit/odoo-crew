# Fragment QA — voie EXÉCUTION (D-03, point n°2)

Mode `graph-lane-runtime`. Série 19.0. Base de QA `lab_qa`, séparée de la copie
client. Transport : `/bridge/labctl qa` (appelle `odoo-test.sh` de la série).

## Résultats

| Contrôle | Commande | Résultat | ⏱ |
|---|---|---|---|
| Installation sur base neuve | `qa lab_rental --quick --fresh --tags /lab_rental:TestPreparationFee` | **install=ok** | 11 s |
| Tests ciblés sur base neuve | idem | **11/11** — 0 failed, 0 error, 0 skipped | |
| Mise à jour sur base existante | `qa lab_rental --quick --tags …` | **install=ok, update=ok** | 4 s |
| Tests ciblés après mise à jour | idem | **11/11** | |
| Suite du module sans filtre de tag | la classe testée est toute la suite du module | **11/11** | |
| ERROR / CRITICAL dans les logs | analyse `odoo-test.sh` | **0** | |
| WARNING liés à `lab_rental` | idem | **0** | |
| Désinstallation | — | ⏳ n.a., revient à `/odoo-close` | |

Preuves : `preuves/d03_tests_cibles.txt` (base neuve),
`preuves/d03_tests_cibles_update.txt` (chemin de mise à jour).

## Les tests discriminent-ils ?

Contrôle explicite, parce que D-03 ne change que deux littéraux : des tests qui
passeraient aussi sur D-02 ne prouveraient rien. Les constantes ont été remises
temporairement à `12.0` / `4`, code par ailleurs inchangé, sur base neuve.

**6 tests sur 11 rouges** (`preuves/d03_tests_rouges_sur_d02.txt`) :

- `test_rental_above_threshold_carries_the_fee` (5 j → 65 attendu, 62 obtenu)
- `test_rental_well_above_threshold_carries_the_fee` (6 j → 75 / 72)
- `test_rental_at_former_threshold_is_free_of_fee` (4 j → 40 / 52) — **le test qui
  porte tout le sens de D-03 : le retrait des frais à quatre jours**
- `test_fee_follows_days_and_kind_changes`
- `test_stored_value_is_written_in_database`
- `test_fee_amount_and_threshold_are_the_ones_of_d03`

Les 5 verts sous D-02 sont ceux que D-03 ne change pas (prêts, location de 3 jours,
0 jour, forfait plat). Discrimination prouvée dans les deux sens. Le code D-03 a
été restauré immédiatement après, et la suite verte rejouée sur base neuve.

## Nombre de tests

11 méthodes (9 au point n°1). Les deux ajouts sont le cas 6 jours (au-dessus du
nouveau seuil, pas seulement à la borne) et le verrou sur les deux paramètres.

## Verdict de la voie

**VERT.** 11/11 sur base neuve et sur chemin de mise à jour, logs propres,
discrimination prouvée. Non couvert par cette voie : la désinstallation
(clôture) et l'écran (le module n'a aucune vue — rien à jouer, rien à capturer).
