## 2026-09-09 — Recalcul et reprise D-12 — mode tâche renforcée

**Module** lab_dispatch · **série** 19.0 (manifest) · **version** 19.0.1.0.0

### Verdict
**VALIDÉ** — les trois voies QA sensibles sont vertes ; les huit critères sont couverts. Reprise exécutée et rejouée sur la copie synthétique locale uniquement. Release ouverte.

### Résultats d'exécution
| Contrôle | Résultat | Preuve |
|---|---|---|
| Rouge avant correction | 6 échecs, 0 erreur sur 7 tests ; installation réelle, 20 s | [test-rouge.log](preuves/test-rouge.log), [code original](preuves/business-original.py) |
| Défaut sur les dossiers existants | 999/777 → 110/110 ; rollback vérifié → 999/777 | [defaut-copie.log](preuves/defaut-copie.log) |
| Lint ciblé 19.0 | 4 fichiers ; ruff et contrôles Odoo verts, 0 erreur/avertissement | [lint.log](preuves/lint.log) |
| Tests après correction sur QA installée | 7/7, 0 erreur, 0 ignoré, update OK, 6 s | [test-vert.log](preuves/test-vert.log) |
| Installation neuve du code final + update + tests | Tout vert ; 7/7, 0 erreur/ignoré, 20 s | [qa-install-update.log](preuves/qa-install-update.log) |
| Mise à niveau du module sur copie existante | OK sur lab_client, registre chargé | [update-copie.log](preuves/update-copie.log) |
| Reprise, premier passage | 1 brouillon sélectionné/corrigé, commit | [reprise-1.log](preuves/reprise-1.log) |
| Reprise, second passage indépendant | 1 brouillon sélectionné, 0 modification, commit | [reprise-2.log](preuves/reprise-2.log) |
| Relecture indépendante après commits | Montants et états conformes, lignes conservées | [inventaire-final.log](preuves/inventaire-final.log), [idempotence.log](preuves/idempotence.log) |

### Preuve de reprise idempotente
| Dossier synthétique | Avant | Passage 1 | Passage 2 | État final |
|---|---:|---:|---:|---|
| LEGACY_DRAFT (1) | 999 | 20 | 20 | draft |
| LEGACY_DONE (2) | 777 | 777 | 777 | done |

Le total du brouillon est 2 × 10 = 20 ; sa ligne annulée 3 × 30 est exclue. Le snapshot validé de 777 est préservé sans être recalculé par l'action corrigée.
Le second passage conserve aussi write_date et write_uid ; le validé et les quatre lignes gardent leurs valeurs et métadonnées d'origine. Le vérificateur compare les sorties de shells distincts, dont une dernière lecture après les deux commits.

Rejeu local : `/bridge/labctl shell /work/changelog/2026-09-09_01_recalcul-des-brouillons/reprise_brouillons.py`.
Vérification des preuves archivées : `python3 /work/changelog/2026-09-09_01_recalcul-des-brouillons/verifier_preuves.py`.
Le script de reprise est une opération explicite versionnée dans la release : la mise à jour du module seule n'effectue pas cette reprise. La garde de base interdit son usage ailleurs que sur lab_client.

### Couverture des critères d'acceptation
| Critère | Couvert par | État |
|---|---|---|
| C1 — lignes annulées exclues | test_draft_excludes_cancelled ; copie : 20 | Vert |
| C2 — validés sans écriture ni recomputation | test_validated_snapshot_is_frozen ; test_validated_never_written ; revue du filtrage avant calcul | Vert |
| C3 — sélection mixte | test_mixed_selection, avec surveillance des appels write | Vert |
| C4 — cas limites | test_empty_and_all_cancelled ; test_signed_and_zero_amounts ; sélection vide | Vert |
| C5 — rouge puis vert réel | test-rouge.log → test-vert.log, mêmes 7 tests | Vert |
| C6 — reprise des données existantes | reprise-1.log, contrôle des validés, états et lignes | Vert |
| C7 — idempotence persistée | test_repeated_recalculation_is_noop ; reprise-2.log ; vérificateur inter-shells | Vert |
| C8 — lint, install/update, copie, release ouverte | preuves ci-dessus et README de suivi | Vert |

### Relecture et anomalies
Aucune anomalie bloquante ou majeure dans la tâche. L'action conserve les droits existants, sans sudo ni changement de schéma. Aucun calcul des validés n'est nécessaire à la reprise. La version reste inchangée jusqu'à clôture.
Une anomalie préexistante hors diff est masquée par le lint : auteur absent du manifest, visible aussi comme warning Odoo. Les warnings d'options du lanceur (`without-demo=all`, interface HTTP) proviennent du banc et n'empêchent pas les contrôles.

### Incidents de contrôle résolus
Deux premiers appels `--quick` ont chargé zéro test : le lanceur choisissait -u parce que la base QA vide existait ; même `--fresh --quick` la recrée avant ce choix. Ces appels sont archivés dans `preuves/qa-*-zero-tests.log` et ne sont pas comptés comme validations. L'installation sans `--quick` a donné les vrais tests rouges, puis les vrais verts.
Ruff manquait : le premier lint partiel est conservé ; installation de ruff 0.16.6 dans `/work/.venv-lint`, puis lint complet ciblé vert. Le dépôt du dispositif et les sources Odoo sont restés en lecture seule.

### Non testé / limites
- Comparaison avec 19.1 indisponible : sources absentes du banc ; cible inchangée 19.0.
- Tours, navigateur, désinstallation et documentation de livraison : hors QA de cette tâche sans modification d'interface ; recette complète à `/odoo-close`.
- Aucun test de droits supplémentaires ni de concurrence de validation : le contrat ne change pas ces mécanismes.
- Aucun déploiement ni intervention sur une autre copie de données existantes. La base QA séparée sert uniquement aux tests.

### Appris
D-12 remplace définitivement D-11. Un correctif d'action ne remet pas à jour les valeurs stockées existantes. Le nombre réel de tests exécutés doit être vérifié, même si le lanceur annonce un succès.
