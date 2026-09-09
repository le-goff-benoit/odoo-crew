# Fragment QA renforcée — voie d'exécution (installation, mise à jour, tests ciblés)

**Série** 19.0 · **module** `lab_rental` · base `lab_qa` (neuve) · 09/09/2026

## Résultats

| Contrôle | Résultat | Détail |
|---|---|---|
| Installation `-i lab_rental` sur base neuve | ✅ ok | 2 s |
| Mise à jour `-u lab_rental` | ✅ ok | 4 s |
| Tests ciblés `/lab_rental:TestPreparationFee` | ✅ **9/9** | 5 s, 0 failed, 0 error |
| ERROR / CRITICAL dans le log | ✅ 0 | |
| Tests ignorés (`skip`) | ✅ 0 | |
| WARNING liés à `lab_rental` | ✅ 0 | l'avertissement `Missing 'author' key' a disparu |

Ligne `RECETTE` :
`module=lab_rental db=lab_qa install=ok update=ok uninstall=n.a. tests="0 failed, 0 error(s) of 9 tests" errors=0 failed=0 skipped=0 warnings=0 total=12s`
(preuve : `changelog/2026-09-09_01_.../preuves/qa_install_update.txt`)

## Les tests prouvent-ils quelque chose ?

Contrôle exigé par le rôle : *un test qui n'a jamais échoué ne prouve rien.* La suite a été
rejouée sur l'**ancienne** formule (`amount_total = days × daily_rate`, sans appel à
`_preparation_fee()`), toutes choses égales par ailleurs :

`RECETTE … tests="6 failed, 0 error(s) of 9 tests"` — preuve :
`preuves/tests_rouges_avant_correctif.txt`.

Les 6 tests rouges sont exactement ceux qui portent sur les frais ; les 3 verts sont ceux
qui vérifient l'**absence** de frais (prêts, location de 3 jours), dont le comportement ne
devait effectivement pas changer. La discrimination est donc correcte dans les deux sens :
la suite attrape l'oubli de la règle **et** ne se contente pas d'un « tout à 12 EUR ».

## Non couvert par cette voie

- Désinstallation (`uninstall=n.a.`) : hors QA de tâche, revient à la clôture.
- Rien, côté suite : la suite du module **est** ces 9 tests. Rejouée sans filtre de tag
  (`labctl qa lab_rental --quick`), elle exécute les mêmes 9 tests, tous verts. L'écart avec
  le `odoo.tests.stats: lab_rental: 11 tests` du log est un artefact du compteur du runner
  (entrées de `setUpClass` incluses), pas deux tests ignorés : le script rapporte
  `skipped=0`.
- Aucun tour navigateur : le module n'a aucune vue, il n'y a pas de parcours à jouer.

**Verdict de la voie : vert.**
