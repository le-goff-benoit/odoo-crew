# Fragment QA d'exécution — point n°2 (D-03), module `lab_rental`, série 19.0

Bases : `lab_qa` (recréée, `--fresh`), `lab_client` (copie synthétique).

| Contrôle | Commande | Résultat |
|---|---|---|
| Installation base neuve | `labctl qa lab_rental --fresh --update --tags /lab_rental:TestPreparationFee` | ✅ `install=ok` |
| Mise à niveau `-u` | idem | ✅ `update=ok` |
| Tests ciblés | idem | ✅ **11/11** — `0 failed, 0 error(s) of 11 tests` (tests 4 s, total 17 s) |
| Les tests mordent | même suite jouée sur la formule D-02 encore en place | ✅ **6/11 rouges**, avec les écarts attendus (62≠65, 52≠40, 112≠115, 30≠40, 12,0≠15,0) |
| ERROR / CRITICAL dans les logs | analyse `odoo-test.sh` | ✅ 0 |
| Mise à niveau sur la copie client | `labctl update` (lab_client) | ✅ 21 modules chargés, 0 erreur |
| Comportement sur la copie client | témoins ORM + relecture SQL | ✅ **5/5** conformes (40,0 / 65,0 / 115,0 / 50,0 / 30,0) |
| Copie laissée intacte | `rollback` sans `commit` | ✅ 0 ligne avant, 0 ligne après |

Preuves : `preuves/qa_tests_verts_d03.log`, `preuves/qa_tests_rouges_avant_d03.log`,
`preuves/verif_copie_lab_client_d03.{py,log}`, `preuves/etat_lab_client_avant_d03.{py,log}`.

## Reprise de données
`lab_rental` contient **0 enregistrement** sur `lab_client`, recompté en SQL avant et après
la mise à niveau. Le changement de formule sur un champ **stocké** n'a donc rien à recalculer
aujourd'hui ; la réserve pour une base cible peuplée reste ouverte pour la clôture, et vise
maintenant D-03.

**Fragment d'exécution : VERT.**
