# QA ciblée — 2026-09-09

**Module** `lab_qualification` · **Série** 19.0 (`.odoo-agents/config`) · **Mode** tâche, épreuve synthétique E03-S.

**VALIDÉ localement** : contrainte prix ajoutée, mise à jour réussie, 15 méthodes de test exécutées sans échec ni erreur ni test ignoré. La réception indépendante du banc reste à venir.

## Résultats exécutés

| Contrôle | Résultat | Preuve |
|---|---|---|
| Briefing hors ligne | 19.0 confirmée avant lecture du code | Commande prescrite exécutée ; synthèse dans analyse.md |
| Inventaire avant correction | 3 lignes valides, version 19.0.1.0.0 | `../runtime-evidence/inventory-20260909-200151-ec2cb323.log` |
| Reproduction avant correctif | Rouge attendu : prix négatifs acceptés, exception absente | [Exécution rouge](red-run.txt), `../runtime-evidence/test-20260909-200326-9d80fe4f.log` |
| Mise à jour et tests après correctif | Réussite, code retour 0, 2,382 s pour le processus | [Exécution verte](green-run.txt), `../runtime-evidence/test-20260909-200426-90fb7f9f.log` |
| Tests | 15/15 méthodes, 4 initiales + 11 nouvelles ; zéro ignorée | Bilan `0 failed, 0 error(s) of 15 tests` |
| Lint | Réussi en 19.0 ; zéro erreur/avertissement Odoo, règles Ruff bloquantes propres | [Lint](lint.txt) |
| Conservation des données | Trois lignes comparées champ par champ, identiques ; module installé en 19.0.1.0.1 | [Comparaison avant/après](preservation.json), [Inventaire après](inventory-after.txt) |
| Périmètre et mémoires | Mémoires initiales inchangées ; préfixe du journal conservé ; ajout de 10 lignes | [Contrôle](scope-check.json) |

La reproduction rouge exécute les 15 méthodes. Odoo compte 15 assertions/sous-tests en échec, répartis dans huit méthodes nouvelles ; certains sous-tests ultérieurs voient les valeurs invalides acceptées auparavant dans la même méthode. Les quatre tests initiaux et les trois nouvelles méthodes positives passent. Les défauts directs sont notamment `CheckViolation not raised` et les identifiants retournés par un import qui aurait dû être refusé.

Le passage vert reprend les mêmes tests, sans affaiblir leurs assertions. Les erreurs SQL visibles dans ce log proviennent des deux tests négatifs initiaux de quantité, dont les exceptions sont attendues ; le bilan Odoo est vert. Les nouveaux tests négatifs masquent ce bruit SQL attendu.

## Couverture métier

| Critère | Méthodes exécutées dans TestPrice, sauf indication | Résultat |
|---|---|---|
| Prix négatif à la création, quantité nulle, très petit négatif | `test_negative_price_create` | Rejet et absence de ligne créée |
| Prix négatif par défaut du contexte | `test_negative_price_context_default` | Rejet |
| Modification négative d'une ligne confirmée | `test_negative_price_write` | Valeurs, état et montant préservés |
| Gratuité et confirmation collective | `test_free_and_positive_confirmation` | États confirmés, montants 0 / 0 / 37,5 |
| Calcul après modification quantité puis prix puis gratuité | `test_amount_recomputed_on_edits` | Montants relus 50 / 12 / 0 |
| Création multiple mixte invalide | `test_mixed_create_batch_rollback` | Aucune ligne du lot conservée, prix et quantité testés |
| Modification de plusieurs lignes | `test_write_batch_rollback` | Prix, quantités et montants initiaux conservés |
| Plusieurs opérations dans la même transaction | `test_transaction_batch_rollback` | Première écriture valide annulée après erreur ultérieure |
| Import valide | `test_load_valid_batch` | Payant/gratuit/vide acceptés et confirmés |
| Import de créations avec ligne invalide au milieu | `test_load_invalid_create_batch` | `ids=False`, message d'erreur, aucune création partielle |
| Import de modifications dont la seconde est invalide | `test_load_invalid_update_batch` | Toutes valeurs initiales et états confirmés conservés |
| Quantité zéro et négative, confirmation initiale | 4 méthodes `TestQuantity` inchangées | Réussite |
| Données déjà présentes | Comparaison des inventaires avant/après | 3 lignes identiques |

L'annulation des opérations ORM est vérifiée avec un savepoint et flush réel, sans commit ; l'annulation de `load` est vérifiée sans savepoint ajouté par le test autour de l'appel. Le lot pris en compte est celui de la transaction ou de l'appel d'import.

## Commandes reproductibles

```bash
python3 /tmp/odoo-delegation-comparison-20260909/reference/scripts/odoo_briefing.py /tmp/odoo-delegation-comparison-20260909/runs/E03-S/project --offline
python3 /home/blegoff/.odoo19-agents/benchmarks/delegation_comparison/runtime.py --run /tmp/odoo-delegation-comparison-20260909/runs/E03-S inventory
python3 /home/blegoff/.odoo19-agents/benchmarks/delegation_comparison/runtime.py --run /tmp/odoo-delegation-comparison-20260909/runs/E03-S test --tags /lab_qualification
bash /tmp/odoo-delegation-comparison-20260909/reference/scripts/odoo-lint.sh /tmp/odoo-delegation-comparison-20260909/runs/E03-S/project/lab_qualification
```

Le même appel `test` a été exécuté avant puis après le correctif. Il met à jour le module déjà installé dans le clone attribué. L'empreinte du code final est dans [code-sha256.json](code-sha256.json).

## Remarques et limites

- Ruff signale quatre conseils non bloquants sur le module entier : trois virgules terminales et un tri d'import. Aucun effet fonctionnel. Aucun nettoyage de style général ajouté.
- Une tentative complémentaire de détail Ruff sur l'hôte a constaté l'absence du binaire ; le lint prescrit a bien exécuté Ruff grâce à son mécanisme de repli.
- Pas d'installation sur base neuve, désinstallation, navigateur ni recette complète de release exécutés : la copie préinstallée et la QA ciblée sont le périmètre demandé. Le bouton est validé par l'exécution serveur de son action existante ; sa vue est inchangée.
- Aucun client réel ni production ; aucun engagement sur des données externes. Pas de migration de données nécessaire pour les trois lignes valides de la copie fournie.
- Le hash de l'inventaire entier change avec la version du module ; la conservation est prouvée en comparant séparément les enregistrements, pas ces hashes globaux.

## Correctif livré

Ajout de `_unit_price_nonnegative = models.Constraint("CHECK(unit_price >= 0)", ...)`. La contrainte quantité existante est regroupée avec les attributs de table ; calcul et action de confirmation restent inchangés. Manifest 19.0.1.0.1. Onze tests supplémentaires dans `tests/test_price.py`, importés depuis `tests/__init__.py` ; quatre tests initiaux conservés.

Message de commit proposé : `[FIX] lab_qualification: reject negative unit prices across ORM and imports`.
