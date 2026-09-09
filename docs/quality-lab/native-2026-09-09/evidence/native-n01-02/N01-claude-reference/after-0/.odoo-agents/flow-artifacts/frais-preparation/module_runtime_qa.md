# Fragment QA — voie d'exécution (installation, mise à niveau, tests ciblés)

**Module** `lab_rental` · **série** 19.0 · **base QA** `lab_qa` · **copie** `lab_client`

## Faux vert écarté (à ne pas perdre)
Premier passage `qa lab_rental --quick --tags /lab_rental:TestPreparationFee` :
`✅ tests OK`, mais `tests="0 failed, 0 error(s) of 0 tests"` — **aucun test n'a tourné**.
Cause lue dans le log : la base `lab_qa` existait sans `lab_rental` installé, et le chemin
`--quick` choisit `-u` dès que la base existe (`odoo-test.sh` : `if db_exists "$DB"; then MODE=-u`).
`--fresh` ne corrige rien : il recrée la base, donc `db_exists` reste vrai et le mode
reste `-u`. Un `-u` sur un module non installé ne charge ni le module ni ses tests.
Contournement retenu : chemin complet (sans `--quick`), qui fait un `-i` explicite.
Preuve : `preuves/qa_faux_vert_quick_0_test.log`.

## Les tests mordent-ils ?
Formule ramenée à `days * daily_rate` (ancien code), même commande :
**4 échecs sur 9** — `test_rental_at_threshold_pays_the_fee`,
`test_rental_above_threshold_pays_the_fee_once`, `test_fee_follows_days_and_kind_changes`,
`test_amount_total_is_stored_in_database`. Les 5 autres restent verts : ils décrivent le
comportement que D-02 ne change pas (prêts, sous-seuil, location vide, durée négative).
Code restauré ensuite. Preuve : `preuves/qa_tests_rouges_avant_correctif.log`.

## Passage retenu
`labctl qa lab_rental --fresh --update --tags /lab_rental:TestPreparationFee`
```
RECETTE module=lab_rental db=lab_qa install=ok update=ok uninstall=n.a.
        tests="0 failed, 0 error(s) of 9 tests" errors=0 failed=0 skipped=0 total=21s
```
installation ✅ · mise à niveau `-u` ✅ · tests **9/9** ✅ · ERROR/CRITICAL : 0.
Preuve : `preuves/qa_tests_verts.log`.

## Contrôle sur la copie `lab_client`
`labctl update` (mise à niveau du module sur la copie) puis création de quatre
enregistrements témoins, lecture ORM **et** lecture SQL, puis suppression :
```
location 4 j    attendu=  52.00 orm=  52.00 sql=  52.00 OK
location 3 j    attendu=  30.00 orm=  30.00 sql=  30.00 OK
pret 4 j        attendu=  40.00 orm=  40.00 sql=  40.00 OK
pret 10 j       attendu= 100.00 orm= 100.00 sql= 100.00 OK
enregistrements restants dans la copie : 0
```
La copie est laissée dans l'état où elle a été trouvée (0 enregistrement).
Preuves : `preuves/verif_copie_lab_client.py`, `preuves/verif_copie_lab_client.log`.

## Avertissements
9 WARNING `Missing 'author' key in manifest for 'lab_rental'` — dette antérieure, sans
rapport avec la tâche.

**Verdict de la voie d'exécution : VERT.**
