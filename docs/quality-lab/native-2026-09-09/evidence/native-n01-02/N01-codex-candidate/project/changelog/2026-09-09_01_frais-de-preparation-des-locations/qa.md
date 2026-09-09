> **Verdict actuel : VALIDÉ — D-03, QA de tâche renforcée locale du point 2, ci-dessous.**
> La première QA D-02 reste une preuve historique ; elle ne valide pas le changement D-03. Release ouverte, aucune livraison ni production validée ici.

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


## 2026-09-09 — Point 2 : D-03 remplace D-02 — mode tâche renforcée

**Module** lab_rental · **série** 19.0 (manifest) · **verdict VALIDÉ pour D-03 en local**.
Décision actée par Alice Martin : `decisions/2026-09-09.md`. Le verdict précédent ne porte que sur D-02 ; il est conservé sans réutilisation comme preuve verte du code D-03.
Run natif `preparation-d03`, trois voies exécutées par Codex sans sous-agent selon LAB.md. Ancien run `preparation` terminé conservé, aucune réinitialisation ; empreintes des anciennes preuves contrôlées.

### Résultats d'exécution
Preuves nouvelles : [flow-artifacts/preparation-d03](../../.odoo-agents/flow-artifacts/preparation-d03/). Les JSON lient les contrôles au contenu exact du module ; ceux des reprises incluent aussi le script actif. Vérification finale : `freshness.txt` (10 preuves valides).

| Contrôle | Résultat | Preuve |
|---|---|---|
| Tests D-03 contre compute D-02 avant correction | Rouge attendu, 11 assertions échouées dans 8 méthodes, 0 erreur technique | runtime-red.json/log ; business-d02.py et tests-d02.py archivés |
| Relecture et lint --changed depuis .base | 5 fichiers, ruff exécuté, 0 erreur/avertissement/info | lint-green.json/log, qa_static.md |
| Installation fraîche lab_qa et tests ciblés | -i exécuté, 8/8, aucun échec/erreur/ignoré ; 12 s | runtime-install.json/log |
| Point de contrôle suite complète du module sur base chaude | -u exécuté, 8/8, aucun échec/erreur/ignoré ; 4 s | runtime-update.json/log, qa_runtime.md |
| Mise à jour lab_client | Réussie ; les totaux D-02 subsistent avant reprise | client-update.json, after-update-before-recompute.json/log |
| Reprise des valeurs D-02 stockées | 7 témoins créés avant modification, 3 totaux corrigés | seed-before.json/log, recompute-1.json/log |
| Persistance | 7/7 conformes dans deux nouvelles sessions | copy-check-1/2.json/log |
| Idempotence | Deuxième passage : 0 changement | recompute-2.json/log |
| Nettoyage copie | 7 témoins supprimés ; nouvelle session confirme 0 record, comme initialement | cleanup.json, after-cleanup.json, qa_client.md |

### Couverture des critères D-03
| Critère actuel | Couverture | État |
|---|---|---|
| D3-C1 : seuil 5 inclus et forfait unique 15 | test_rental_threshold : 3/4/5/6/20 jours → 30/40/65/75/215 | Conforme |
| D3-C2 : prêts exclus | test_loans_have_no_fee : 3/4/5/6/20 jours → 30/40/50/60/200 ; copie 4/5/6 | Conforme |
| D3-C3 : zéros et décimales | test_zero_values, test_decimal_rate ; 5 × 1.2345 + 15 = 21.1725 | Conforme |
| D3-C4 : créations et changements des trois dépendances | test_mixed_batch, test_days_changes (4↔5), test_daily_rate_changes, test_kind_changes | Conforme |
| D3-C5 : stockage et reprise | assertStoredTotals ; 4 jours 52→40, 5 jours 62→65, 6 jours 72→75 ; deux relectures et idempotence | Conforme |
| D3-C6 : périmètre et mémoire | Relecture : écran/droits/facturation/dépendances/version inchangés ; D-03 active, D-02 historisée | Conforme |

### Anomalies et limites exactes
Aucun bloquant restant pour cette QA de tâche. Le premier lint de cette reprise était **partiel** : le venv temporaire indiqué par l'ancienne mémoire n'existait plus dans le contexte neuf. Ruff 0.16.6 réinstallé isolément puis lint rejoué vert ; `lint.json/log` et `ruff-install.log` conservés.
Les avertissements techniques du pont concernent `--without-demo=all` et, sur QA, l'absence de `--http-interface` explicite. Aucun défaut de vue/module constaté ; ne pas confondre le compteur filtré `warnings=0` de RECETTE avec l'absence de ces avertissements de démarrage.
La copie initialement vide a reçu sept témoins synthétiques sous D-02. La reprise de données client réelles n'a pas été testée. Les sources enterprise 19.1 restent absentes.
Tours, captures, désinstallation et recette complète de release non exécutés : ils attendent `/odoo-close`. Cette intervention valide le code et la reprise **en local**, sans clôturer ni déployer.
QA de l'arbre local : les tests non suivis, déjà présents au début, devront être inclus avec le module et le script de reprise lors d'une future livraison ; aucun commit effectué. Version 19.0.1.0.0 conservée.

### Appris
D-03 remplace D-02 dès cette release. Reprendre une décision après une première QA exige de nouvelles preuves liées au code final. Une mise à jour seule laisse effectivement les anciens totaux stockés : la reprise ORM explicite est nécessaire, y compris pour retirer le forfait à 4 jours.
