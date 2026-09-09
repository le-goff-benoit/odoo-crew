## 2026-09-09 — Frais D-02 — QA de tâche renforcée, tentative 1

Odoo 19.0 (manifest), lab_rental. **REFUSÉ** : six sous-cas en erreur dans deux tests de contraintes, qui attendent ValidationError au lieu de CheckViolation. Les huit tests de calcul passent. Lint vert ; update copie réussi, reprise prouvée (30/40/50/40 → 30/52/62/40). Idempotence et nettoyage restent à terminer.

Reprise 1 : corriger les assertions SQL et leur logger selon le précédent Odoo 19.0 `odoo/addons/base/tests/test_sql.py`, puis rejouer les contrôles. Preuves détaillées dans `.odoo-agents/flow-artifacts/preparation-d02/qa_*attempt1.md` et `runtime.json/log`.

## 2026-09-09 — Verdict final après reprise 1 — mode tâche renforcée

**VALIDÉ** — `lab_rental`, Odoo 19.0 (manifest), sept critères satisfaits. Release ouverte, version 19.0.1.0.0 conservée.

### Résultats d'exécution

| Contrôle | Résultat | Preuve dans preuves/ |
|---|---|---|
| Lint des cinq fichiers touchés, Ruff inclus | 0 erreur, 0 avertissement | lint_final.log/json |
| Installation neuve, tests ciblés | 10/10, 0 erreur/échec/skip, 11 s | runtime_final.log/json |
| Mise à jour QA, tests ciblés | 10/10, 0 erreur/échec/skip, 4 s | runtime_update.log/json |
| Update copie lab_client | OK | copy_final.log/json |
| Reprise des totaux préexistants | 30/40/50/40 → 30/52/62/40 | seed_before.log, copy_check_attempt1.log |
| Idempotence et persistance inter-sessions | Deux rejeux identiques, entrées préservées | copy_final.log |
| Nettoyage copie | 4 témoins retirés, retour à zéro location | copy_final.log |
| Revue des écrans, droits, facturation | Aucun changement dans le diff | qa_static_final.md |

### Critères d'acceptation

| Critère | Couverture | État |
|---|---|---|
| C1 : seuil inclusif, forfait fixe | test_rental_threshold | OK |
| C2 : prêts exclus 3/4/5 jours | test_loans_excluded | OK |
| C3 : zéro, valeurs par défaut, décimales | test_zero_values_and_defaults, test_no_extra_rounding | OK |
| C4 : chaque dépendance, transitions, lots, aucun cumul | test_days_recompute_both_directions, test_rate_recompute, test_kind_recompute_both_directions, test_mixed_batch_and_no_cumulative_fee | OK |
| C5 : total stocké, périmètre UI/droits/facturation | assertStoredTotals dans tous les tests de calcul, relecture en nouveau shell, revue du diff | OK |
| C6 : valeurs non négatives | test_negative_values_rejected_on_create/write, assertions sur chaque nom de contrainte | OK |
| C7 : install/update, reprise et idempotence | runtime_final, runtime_update, copy_final | OK |

### Anomalies et remarques

Aucune anomalie restante de la tâche. Les six erreurs de la première tentative sont corrigées par les assertions `CheckViolation` appropriées aux contraintes SQL en TransactionCase ; historique rouge conservé.
Métadonnée `author` absente du manifest initial : ajoutée pour passer le contrôle obligatoire, sans changement de version ni dépendance.
Le pont émet un avertissement antérieur `--without-demo=all` (Odoo 19.0 attend un booléen, le convertit à True) et un avertissement d'interface HTTP par défaut. Aucun avertissement lié à lab_rental, aucun impact sur les données créées par les tests. Dispositif en lecture seule : candidat à `/odoo-feedback`, pas de modification ici.

### Non exécuté et livraison ultérieure

- Recette de clôture (tours, désinstallation, captures et livrables client) non exécutée : la release doit rester ouverte et aucun écran n'est modifié.
- Sources 19.1 absentes : comparaison au futur standard non exécutée.
- La seule classe ciblée contient toute la suite actuelle du module (10 méthodes).
- À la clôture : incrémenter la version et intégrer explicitement `scripts/recompute_totals.py` après l'update dans le protocole de livraison. Le script est déjà exécuté et validé sur la copie synthétique ; aucune production concernée.

### Appris

Le changement d'un compute stocké nécessite une reprise explicite même si l'update réussit. D-02 remplace définitivement D-01 ; ne pas réintroduire de pourcentage.
