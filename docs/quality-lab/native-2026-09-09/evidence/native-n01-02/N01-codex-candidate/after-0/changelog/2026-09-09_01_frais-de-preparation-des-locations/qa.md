## 2026-09-09 — Frais de préparation D-02 — mode tâche renforcée

**Module** lab_rental · **série** 19.0 (manifest) · **verdict VALIDÉ**.
Les trois voies du graphe ont été exécutées par Codex, sans sous-agent, via le pont prévu dans LAB.md.

### Résultats d'exécution
Les preuves et journaux complets sont dans [flow-artifacts/preparation](../../.odoo-agents/flow-artifacts/preparation/).

| Contrôle | Résultat | Preuve |
|---|---|---|
| Relecture et lint natif --changed | 5 fichiers, ruff exécuté, 0 erreur, 0 avertissement | lint-green.json, qa_static.md |
| Installation sur base QA séparée | OK, 19 s avec tests | runtime.json et runtime.log |
| Tests métier ciblés | 8/8, 0 échec, 0 erreur, 0 ignoré | TestPreparationFee ; runtime.log |
| Mise à jour de la copie lab_client | OK, environ 5 s | client-update.json |
| Reprise des valeurs antérieures | 4 témoins, 2 totaux corrigés | seed_before.log, recompute-1.json |
| Idempotence | Deuxième passage : 0 changement | recompute-2.json |
| Persistance après reprise | 4/4 conformes dans deux nouvelles sessions | copy-check-1.json, copy-check-2.json |
| Nettoyage | 4 témoins supprimés, retour aux 0 locations initiales | cleanup.json |

### Couverture des critères d'acceptation
| Critère | Couverture | État |
|---|---|---|
| C1 locations et seuil inclusif | test_rental_threshold, témoins 3/4/5 jours | Conforme |
| C2 prêts exclus | test_loans_have_no_fee, témoin prêt 4 jours | Conforme |
| C3 zéros et décimales sans arrondi supplémentaire | test_zero_values, test_decimal_rate | Conforme |
| C4 créations multiples et modifications des trois dépendances | test_mixed_batch, test_days_changes, test_daily_rate_changes, test_kind_changes | Conforme |
| C5 stockage et reprise idempotente | assertStoredTotals + deux reprises et relectures indépendantes | Conforme |
| C6 aucun écran, droit, flux de facturation ou changement de version | Relecture du diff ; manifest 19.0.1.0.0 conservé | Conforme |

### Anomalies et limites
Aucun bloquant restant. Le premier lint a échoué sur l'absence d'auteur dans le manifest initial et l'indisponibilité de ruff ; auteur synthétique Atelier Boréal ajouté, ruff 0.16.6 installé dans un environnement isolé `/tmp/odoo-lab-tools`, puis lint complet des fichiers touchés réussi. Preuve initiale conservée dans lint.json.
Le pont update émet un avertissement Odoo 19.0 : `--without-demo=all` est interprété comme True. Mise à jour réussie, aucun défaut du module ; dispositif en lecture seule, avertissement à transmettre via `/odoo-feedback`.
Les sources 19.1 enterprise sont absentes : comparaison avec la série suivante non effectuée. La copie était vide : la reprise est prouvée sur quatre témoins synthétiques créés avant modification, sans données client réelles.
Tours, captures, désinstallation et recette complète de release non exécutés : cette demande est une QA de tâche sans changement d'écran ; ils relèvent de `/odoo-close`. La mise à jour et la reprise sensibles ont bien été validées immédiatement.

### Appris
D-02 remplace D-01 ; modifier le compute ne reprend pas à lui seul les montants stockés. Exécuter explicitement `recompute_totals.py` après update sur le périmètre autorisé. Le second passage n'ajoute pas de frais cumulés.
