## 2026-09-09 — Frais de préparation D-02 — mode tâche renforcé

**Série** 19.0 (manifest) · **module** lab_rental · **verdict : VALIDÉ**.
Les trois voies du graphe (statique, exécution, copie) sont vertes ; C1–C7 satisfaits.

### Résultats d'exécution
| Contrôle | Résultat | Preuve |
|---|---|---|
| Lint --changed | Ruff + Odoo : 0 erreur, 0 avertissement, 4 fichiers | [lint](proofs/lint.log) |
| Installation | OK, 3 s | [exécution](proofs/qa-install-update.log) |
| Mise à jour QA | OK, 4 s | même log |
| Tests métier ciblés | 7/7, 0 erreur, 0 échec, 0 ignoré, 4 s | même log ; TestPreparationFee |
| Update copie lab_client | OK, module déjà installé | [update](proofs/client-update.log) |
| Reprise des totaux existants | 30/40/40 → 30/52/40, entrées conservées | [première vérification](proofs/verify-first.log) |
| Idempotence et persistance | Deuxième exécution identique, lecture dans une nouvelle session | [deuxième vérification](proofs/verify-second.log) |
| Nettoyage copie | Trois fixtures supprimées, état initial vide restauré | [nettoyage](proofs/cleanup.log) |
| Diff et compilation | git diff --check et compileall : OK | [relecture](proofs/qa-static.md) |

Commande concluante : `/bridge/labctl qa lab_rental --update --tags /lab_rental:TestPreparationFee` (11 s).
Pour le lint : Ruff 0.16.6 dans `.odoo-agents/tooling-venv`, ajouté au PATH ; aucun fichier du dispositif modifié.

### Couverture des critères
| Critère | Couvert par | État |
|---|---|---|
| C1 : locations 3/4/5 jours | test_rental_threshold | OK |
| C2 : prêts exclus 3/4/5 jours | test_loans_excluded | OK |
| C3 : zéros et décimales | test_zero_and_decimal_amounts | OK |
| C4 : trois dépendances, aller-retour et lot | test_days_recompute_both_directions, test_daily_rate_recompute, test_kind_recompute_both_directions, test_mixed_batch_write_and_search | OK |
| C5 : stockage effectif | assertStoredTotals : flush/invalidation dans chaque test ; recherche par amount_total | OK |
| C6 : update/reprise/idempotence | fixtures créées sur l'ancien code, reprise et vérifications dans des processus distincts | OK |
| C7 : périmètre et release ouverte | diff, manifest inchangé, suivi ouvert | OK |

### Anomalies et réserves
Aucun bloquant ni anomalie métier. Avertissement préexistant : `lab_rental/__manifest__.py:1` omet `author` (8 occurrences dans les trois chargements). Le lint masque une anomalie antérieure hors diff ; pas de correction hors périmètre.
Les deux premières tentatives rapides sont **non concluantes** : 0 test. Le script choisit -u sur une base existante même si le module n'est pas installé ; --fresh crée aussi la base avant ce choix. L'installation explicite résout ce défaut d'outillage. Preuves conservées dans `qa-runtime.log` et `qa-install.log` du dossier de flow.

### Reprise livrée
`scripts/recompute_lab_totals.py` utilise add_to_compute et _recompute_recordset, puis commit, avec garde stricte sur lab_client. Après -u seul, les anciennes valeurs étaient encore 30/40/40 : reprise explicite nécessaire et prouvée.
Le bac initial était vide malgré la mention générique de données dans LAB.md ; trois essais ont donc été créés avant update, puis nettoyés. Aucun document historique ni production concernés.

### Non testé / suite
Recette complète, tours, désinstallation et livrables client réservés à la clôture. Aucun écran modifié, pas de parcours navigateur à tester pour ce point. Comparaison sources enterprise 19.1 indisponible.
Manifest 19.0.1.0.0 conservé pendant la release ; incrément et intégration de la reprise au protocole de livraison à la clôture.
Candidate pour /odoo-feedback : ne jamais valider zéro test ; choisir -i/-u selon l'installation du module, pas seulement l'existence de la base.
