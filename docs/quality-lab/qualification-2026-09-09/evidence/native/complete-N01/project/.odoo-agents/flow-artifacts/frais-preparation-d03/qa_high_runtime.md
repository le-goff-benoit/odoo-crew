# Fragment QA renforcée — voie exécution (point 2, D-03)

**Portée** installation sur base neuve, mise à niveau, tests ciblés. Base `lab_qa`, distincte de la
copie client.

| Contrôle | Commande | Résultat | ⏱ |
|---|---|---|---|
| Installation base neuve + tests ciblés | `labctl qa lab_rental --quick --fresh --tags /lab_rental:TestPreparationFee` | `install=ok` · **0 failed, 0 error(s) of 12 tests** · 0 ERROR/CRITICAL · 0 warning lié au module | 23 s |
| Mise à niveau + tests ciblés | `labctl qa lab_rental --quick --update --tags /lab_rental:TestPreparationFee` | `install=ok update=ok` · **0 failed, 0 error(s) of 12 tests** | 8 s |

Journaux : `qa_runtime.txt` (install), `qa_runtime_update.txt` (update).

## Ce que les 12 tests couvrent

Les 12 cas de `TestPreparationFee` sont écrits sur D-03 ; les valeurs attendues viennent de
`decisions/2026-09-09.md`. Deux d'entre eux sont des tests de non-régression sur des règles mortes :

- `test_the_fee_is_flat_and_never_proportional` — le reste après `jours × tarif` vaut 15.0 pour un
  tarif de 10 comme de 1000 : ni les 7 % de D-01, ni les 12 EUR de D-02 ne peuvent revenir sans échec ;
- `test_the_four_day_rental_no_longer_bears_the_superseded_fee` — une location de 4 jours vaut
  exactement `jours × tarif` : c'est le renversement de D-02, qui la facturait 52.0.

## Limite de ce fragment

Ces tests s'exécutent sur une base **neuve** : ils prouvent la règle de calcul, **pas** la reprise
des données déjà écrites sous D-02. C'est l'objet du fragment copie client, obligatoire ici.

**Fragment : conforme.**
