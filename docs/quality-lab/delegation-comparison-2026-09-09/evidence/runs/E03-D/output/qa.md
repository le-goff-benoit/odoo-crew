# QA ciblée — validée sur copie synthétique Odoo 19.0

## Correctif reçu

`lab_qualification` passe de 19.0.1.0.0 à 19.0.1.0.1. Ajout de `models.Constraint("CHECK(unit_price >= 0)", ...)`, en complément de la contrainte de quantité existante. La borne est zéro, sans arrondi ni condition sur l'état. Aucun override CRUD/import, aucune modification du compute, du bouton, des vues ou des accès. Les quatre tests initiaux sont conservés et dix nouveaux tests sont importés dans la suite.

Fichiers modifiés : `models.py`, `__manifest__.py`, `tests/__init__.py` ; ajout de `tests/test_price.py`. Empreintes du module livré dans [code-sha256.json](code-sha256.json). Modèle initial archivé dans [models-before.py](models-before.py).

## Exécution réelle locale

Runtime fourni, clone exclusif E03-D, un seul écrivain/utilisateur de la base. Commandes utilisées :

```bash
python3 /tmp/odoo-delegation-comparison-20260909/reference/scripts/odoo_briefing.py /tmp/odoo-delegation-comparison-20260909/runs/E03-D/project --offline
python3 /home/blegoff/.odoo19-agents/benchmarks/delegation_comparison/runtime.py --run /tmp/odoo-delegation-comparison-20260909/runs/E03-D inventory
python3 /home/blegoff/.odoo19-agents/benchmarks/delegation_comparison/runtime.py --run /tmp/odoo-delegation-comparison-20260909/runs/E03-D test --tags /lab_qualification
bash /tmp/odoo-delegation-comparison-20260909/reference/scripts/odoo-lint.sh /tmp/odoo-delegation-comparison-20260909/runs/E03-D/project/lab_qualification
```

- Avant correctif, après ajout des tests : processus 1, 14 méthodes exécutées, 18 échecs d'assertion/sous-tests, aucune erreur de test. `CheckViolation not raised` et imports négatifs acceptés reproduisent le défaut. Certains échecs de sous-tests suivants sont les conséquences de cette acceptation dans la même méthode ; ce ne sont pas 18 défauts distincts. [Journal rouge](../runtime-evidence/test-20260909-200959-2b347d9f.log), [commande rouge](test-red-command.log).
- Après correctif et mise à jour `-u lab_qualification` : processus 0, **0 failed, 0 error(s) of 14 tests**. Les 14 noms réellement démarrés apparaissent dans le bilan, aucun test manquant ni sauté. [Journal vert](../runtime-evidence/test-20260909-201020-c48e66d7.log), [commande et bilan](test-green-command.log).
- Lint : série cible 19.0, code retour 0, règles Ruff bloquantes réussies ; contrôles Odoo : 0 erreur, 0 avertissement. Le mode conseil signale 7 virgules terminales et 1 ordre d'imports, non bloquants. [Log complet](lint.log). La tentative de détail par `ruff` directement sur l'hôte échoue car le binaire n'y est pas installé ; le script fourni a exécuté Ruff avec succès via son mécanisme de repli.
- Inventaires avant et après : module installé en 19.0.1.0.1, **les trois lignes valides initiales sont conservées** avec mêmes id, name, quantity, unit_price, amount et state. Comparaison Python exacte réussie, pas de ligne supplémentaire. [Avant](inventory-before.json), [après](inventory-after.json), [comparaison](preservation.json). L'empreinte globale du runtime change légitimement avec la version du module ; la conservation est vérifiée sur les lignes elles-mêmes.

## Couverture du contrat

| Critère | Méthodes exécutées et assertions |
|---|---|
| Prix négatif interdit en création, tous états | `TestPrice.test_negative_create` : -5 et -0.000001, draft et confirmed ; `test_negative_context_default` : défaut de contexte négatif refusé |
| Modification refusée, état valide conservé | `test_negative_write_preserves_record` : prix, quantité, montant et état relus après rollback, deux états et deux valeurs négatives |
| Gratuité, quantité zéro, calcul, confirmation | `test_free_confirmation_and_recomputation` : gratuit confirmé ; 4 × 2.5 = 10 ; 6 × 2.5 = 15 ; retour au gratuit ; quantité zéro. `TestQuantity.test_zero`, `test_confirmation` conservés |
| Quantité négative refusée | `TestQuantity.test_negative_create`, `test_negative_write`, plus cas quantité dans les tests de lots/imports |
| Création par lot atomique | `test_batch_create_atomicity` : valide + invalide + gratuite ; aucune ligne du lot persistée pour prix ou quantité négative |
| Écriture multi-enregistrements atomique | `test_batch_write_atomicity` : refus prix/quantité négatifs, toutes les valeurs initiales préservées ; puis passage du lot au gratuit et confirmation réussis |
| Plusieurs opérations dans une transaction | `test_transaction_batch_rollback` : première écriture valide flushée, seconde invalide ; rollback des deux écritures |
| Import valide et confirmation | `test_load_valid` : payant, gratuit et quantité zéro importés puis confirmés ; montants 7.5, 0 et 0 |
| Import de création invalide atomique | `test_load_create_atomicity` : une ligne négative entre deux valides ; `ids is False`, message d'erreur et aucun ajout, pour prix et quantité |
| Import de modification invalide atomique | `test_load_update_atomicity` : première modification valide puis seconde invalide ; message d'erreur et les deux lignes confirmées inchangées ; import valide ultérieur à zéro/positif et montants 0/10 |
| Données préexistantes conservées à la mise à jour | Inventaires avant/après comparés champ par champ, 3 lignes identiques |

Les tests SQL utilisent `CheckViolation` et un savepoint englobant l'écriture et `flush_all`. Le retour utilisateur de `load` est vérifié via ses messages d'erreur, sans attendre une exception externe. Le test de transaction n'ajoute pas d'annulation artificielle dans le code métier : il représente la limite transactionnelle d'un lot.

## Sources consultées et limites

Sources locales 19.0 : `addons/stock/models/stock_package_type.py:45-60` pour `models.Constraint` avec borne inclusive ; `odoo/orm/models.py:895-1065` pour l'import et son rollback ; `odoo/addons/base/tests/test_sql.py:181` pour `CheckViolation`. Briefing et rôles pertinents du référentiel figé, modèle, vue, manifest, sécurité, tests et mémoires de ce RUN consultés.

La preuve concerne une copie **synthétique**, pas une base client. Pas de réseau métier, production, capture ou recette navigateur. Le bouton est validé par son action ORM ; aucun XML n'est modifié. Pas de certification de release ni d'installation sur base neuve : le périmètre imposé est une mise à jour locale et QA ciblée. Un lot désigne une transaction ORM ou un appel `load` ; plusieurs appels distants validés séparément ne bénéficient pas d'une annulation commune. La conservation n'atteste pas des métadonnées non inventoriées telles que `write_date`.

Aucune reprise de données ni décision humaine nécessaire dans le jeu fourni. Si une autre base contient déjà des prix négatifs, leur traitement et l'installation effective de la contrainte devront être vérifiés avant livraison sur cette base.

Message de commit proposé : `[FIX] lab_qualification: reject negative unit prices`.
