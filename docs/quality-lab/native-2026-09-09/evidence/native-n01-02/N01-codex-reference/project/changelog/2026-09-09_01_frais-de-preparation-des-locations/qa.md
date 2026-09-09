## 2026-09-09 — Frais de préparation D-02 — mode tâche renforcée

**Série** 19.0 (manifest) · **module** lab_rental · **Verdict : VALIDÉ**.
La règle D-02 et les sept critères sont couverts ; les trois voies du graphe (statique, exécution, copie) sont vertes. Release maintenue ouverte.

### Résultats d'exécution

| Contrôle | Résultat | Preuve |
|---|---|---|
| Relecture et lint --changed | 5 fichiers ; Ruff et contrôles Odoo verts, aucun conseil ; git diff --check vert | [lint.log](preuves/lint.log), [code.diff](preuves/code.diff) |
| Installation réelle sur QA | OK, 2 s ; les erreurs de tests lors de ce passage ont été corrigées ensuite | [qa-install-tests.log](preuves/qa-install-tests.log) |
| Mise à jour QA et tests finaux | **8/8**, 0 échec, 0 erreur, 0 ignoré ; 4 s | [qa-final.log](preuves/qa-final.log) |
| Mise à jour lab_client | OK, registre chargé en 2,7 s, sans erreur | [copy-update.log](preuves/copy-update.log) |
| Reprise des valeurs stockées | Deux passages identiques, données d'entrée conservées | [copy-validation.log](preuves/copy-validation.log) |
| Persistance après commit | Totaux SQL et ORM corrects dans une nouvelle session ; quatre essais nettoyés | [copy-reload.log](preuves/copy-reload.log) |

Commandes finales :

```bash
PATH=/work/.tools/lint/bin:$PATH ~/.odoo19-agents/scripts/odoo-lint.sh --changed ace91a8b8126a559073aebe72fa091d30a47f1e9 /work/lab_rental
/bridge/labctl qa lab_rental --tags /lab_rental:TestPreparation
/bridge/labctl qa lab_rental --quick --tags /lab_rental:TestPreparation
/bridge/labctl update
/bridge/labctl shell /work/changelog/2026-09-09_01_frais-de-preparation-des-locations/preuves/validate_copy.py
/bridge/labctl shell /work/changelog/2026-09-09_01_frais-de-preparation-des-locations/preuves/verify_copy.py
```

Les scripts copie identifient les essais de cette exécution (IDs 5–8). Pour rejouer après nettoyage, exécuter prepare_copy.py sur la version d'origine puis adapter les IDs de validation à ceux rendus ; ne pas créer des doublons sans contrôler l'inventaire.

### Couverture des critères

| Critère | Couvert par | État |
|---|---|---|
| C1 : location 3/4/5 jours → 30/52/62 | test_rental_threshold + copie | OK |
| C2 : prêts sans frais → 30/40/50 | test_loans_excluded + copie | OK |
| C3 : zéro et décimales sans arrondi ajouté | test_zero_and_decimal_amounts | OK |
| C4 : dépendances jours/tarif/type, aller-retour, lot, stockage SQL | test_days_recompute_both_directions, test_rate_recompute, test_kind_recompute_batch | OK |
| C5 : entrées négatives refusées en création/modification, zéro admis | test_negative_inputs_rejected, quatre sous-tests | OK |
| C6 : reprise idempotente, entrées inchangées, stockage persistant | test_migration_existing_totals_idempotent + copy-validation/reload.log | OK |
| C7 : pas d'écran/droit/facture modifié ; version conservée ; release ouverte | Relecture du diff, manifest et marqueur README | OK |

Chaque assertion de total dans les tests relit la colonne SQL puis le champ ORM après invalidation du cache. Les entrées négatives sont contrôlées par des models.Constraint 19.0 ; les tests attendent CheckViolation conformément aux précédents standard pour contraintes SQL.

### Copie : avant / après

L'inventaire [inventory.log](preuves/inventory.log) a montré une copie sans location, sans champ manuel, action serveur ou vue de ce modèle. Quatre essais ont été créés **avant modification** et commités :

| Essai | Avant / après update seul | Après migration (deux fois) / nouvelle session |
|---|---|---|
| Location 3 j × 10 | 30 | 30 |
| Location 4 j × 10 | 40 | 52 |
| Location 5 j × 10 | 50 | 62 |
| Prêt 4 j × 10 | 40 | 40 |

La migration est livrée dans `lab_rental/migrations/19.0.1.0.1/post-recompute-amount-total.py`. Le manifest reste à 19.0.1.0.0 durant la release : la même fonction migrate a donc été appelée explicitement après update, puis exécutée deux fois et vérifiée après commit. **L'incrément et le déclenchement automatique par Odoo seront à valider à la clôture**, avant livraison.

### Anomalies bloquantes

Aucune restante.

### Remarques et incidents résolus

- Dette préexistante : `lab_rental/__manifest__.py:1` n'a pas de clé author ; le lint masque cette unique anomalie hors périmètre, Odoo répète trois warnings dans le passage final. Manifest inchangé conformément au périmètre.
- Outillage : Ruff absent initialement, installé dans `.tools/lint` (exclu localement de Git), puis lint complet vert. Version et installation dans [lint-tool-install.log](preuves/lint-tool-install.log).
- Les deux premières tentatives rapides ([qa-runtime.log](preuves/qa-runtime.log), [qa-install.log](preuves/qa-install.log)) affichaient du vert **avec zéro test**. `odoo-test.sh --quick` choisit -u si la base existe, même si le module n'est pas installé. `--fresh` recrée également une base avant ce choix. L'installation explicite via le pont sans --quick a débloqué la vraie exécution.
- Premier passage réel : les quatre sous-tests négatifs attendaient ValidationError, mais le shell ORM lève CheckViolation pour les contraintes SQL ; assertions corrigées, puis 8/8 verts. Aucun défaut du calcul constaté.
- Warnings de transport : `--without-demo=all` est toléré comme True en 19.0 ; avertissement http-interface. Aucun warning de vue.
- Premier script de préparation : tentative d'écrire `/work` depuis le conteneur, chemin non monté sous ce nom ; transaction annulée. Les états sont désormais imprimés et sauvegardés par le pont sur l'hôte. Aucun essai de cette tentative conservé.

### Non testé / limites

- Sources de la série suivante absentes : comparaison standard 19.1 non réalisable ici.
- Déclenchement automatique de migration après incrément de version, recette complète de release, tours et désinstallation : différés à `/odoo-close`. Aucun écran n'est ajouté ou modifié ; pas de capture ni de documentation client produite.
- Aucun déploiement ; tous les essais ont lieu sur les bases synthétiques autorisées.

### Appris

Un changement de compute stocké ne reprend pas les totaux existants à lui seul. Un résumé RECETTE vert avec zéro test ne valide pas une tâche ; vérifier le nombre de tests et l'installation réelle du module.

Message de commit proposé : `[IMP] lab_rental: appliquer les frais de préparation D-02` (non exécuté).

## 2026-09-09 — D-03, QA de tâche renforcée, tentative 1

**REFUSÉ pour cette tentative** : tests 8/8 et lint verts, update copie réussi, mais assertion de conservation de write_date rouge (`preuves/d03/copy-validation.log`). Les montants D-03 sont corrects et les entrées métier conservées. Aucun commit de reprise ; rollback à la sortie du shell en erreur.
Cause prouvée : Odoo 19.0 `_write_multi` (`odoo/orm/models.py:4536`) actualise les métadonnées d'audit même pour un compute stocké. Le critère de conservation de write_date, ajouté par l'agent au cadrage D-03, dépasse la demande et contredit ce comportement standard. Le test transactionnel ne le révélait pas car l'horodatage de transaction reste constant.
Reprise 1 : conserver les entrées métier comme exigé ; constater les métadonnées avant/après au lieu d'en empêcher la mise à jour. Aucune modification du mécanisme de migration nécessaire. La QA finale reste à effectuer.

## 2026-09-09 — D-03, verdict final après reprise 1 — mode tâche renforcée

**Série 19.0 (manifest), module lab_rental — VALIDÉ EN LOCAL.**
D-03 d'Alice Martin remplace D-02 dès cette release : forfait de **15 EUR dès 5 jours inclus pour les locations**, prêts exclus, jours × tarif inchangé. La QA D-02 ci-dessus reste historique ; le présent verdict couvre le code D-03 et C1–C7 (C6 rectifié dans la revue). Aucun bloquant restant.

### Résultats réels

| Contrôle | Résultat | Preuve |
|---|---|---|
| Lint --changed depuis ace91a8b8126a559073aebe72fa091d30a47f1e9 | 5 fichiers, 0 erreur/avertissement ; git diff --check vert | [lint-final.log](preuves/d03/lint-final.log), [diff final](preuves/d03/code-final.diff) |
| Non-régression rouge sous D-02 | 8 méthodes exécutées ; 7 échecs comptés dont 2 sous-tests, écarts 52≠40 et 62≠65 | [qa-red.log](preuves/d03/qa-red.log) |
| Mise à jour et suite métier D-03 sur lab_qa | **8/8**, 0 échec, erreur ou skip, 7 s | [qa-final.log](preuves/d03/qa-final.log) |
| Mise à jour lab_client | OK, registre chargé en 4,891 s | [copy-update.log](preuves/d03/copy-update.log) |
| Reprise explicite de la migration livrée | 2 passages, mêmes montants, entrées métier conservées, SQL/ORM concordants | [copy-validation-final.log](preuves/d03/copy-validation-final.log) |
| Persistance et nettoyage | Nouvelle session après commit conforme ; seuls les 8 essais créés supprimés, copie vide comme à l'inventaire | [copy-reload.log](preuves/d03/copy-reload.log) |
| Conservation historique | Empreintes SHA-256 des preuves et du flow D-02 inchangées | [history-check.log](preuves/d03/history-check.log) |

La commande QA finale est `/bridge/labctl qa lab_rental --quick --tags /lab_rental:TestPreparation`, exécutée sur le module déjà installé. Elle couvre toute la suite métier actuelle (8 méthodes, avec sous-tests). L'installation initiale est prouvée dans la QA D-02 ; **aucune nouvelle installation sur base neuve n'est revendiquée pour D-03**. Le contrôle renforcé des données existantes est réalisé sur copie.

### Critères actuels

| Critère | Preuve | État |
|---|---|---|
| C1 : locations 3/4/5/6 j à 10 → 30/40/65/75 | test_rental_threshold + copie | OK |
| C2 : prêts 3/4/5/6 j → 30/40/50/60 | test_loans_excluded + copie | OK |
| C3 : zéro, gratuité de part et d'autre du seuil, décimales | test_zero_and_decimal_amounts | OK |
| C4 : durée 4→5→4, tarif, type et écritures en lot | test_days_recompute_both_directions, test_rate_recompute, test_kind_recompute_batch ; relectures SQL/ORM | OK |
| C5 : négatifs refusés en create/write, zéro admis | test_negative_inputs_rejected | OK |
| C6 rectifié : reprise D-02 et sans forfait, idempotence et entrées métier conservées | test_migration_existing_totals_idempotent + double migration sur copie + nouvelle session | OK |
| C7 : historique préservé, mémoire D-03, version et droits inchangés, release ouverte | diff et contrôle SHA-256 ; PROJECT.md/README.md | OK |

### État avant/après copie

Essais IDs 9–16 créés et commités **sous D-02 avant modification**, sauvegarde dans [copy-before.json](preuves/d03/copy-before.json).

| Type et durée, tarif 10 EUR | Avant / après update seul | Après reprise x2 / nouvelle session |
|---|---|---|
| Location 3 j | 30 | 30 |
| Location 4 j | 52 | 40 |
| Location 5 j | 62 | 65 |
| Location 6 j | 72 | 75 |
| Prêts 3/4/5/6 j | 30/40/50/60 | 30/40/50/60 |

Les entrées name/kind/days/daily_rate et IDs sont identiques. write_date est actualisé par le standard pour les totaux modifiés ; ce n'est pas une entrée métier. La tentative 1 rouge et son script sont conservés. Après son rollback, les scripts `validate_copy_v2.py` et `verify_copy_v2.py` ont réussi sans modification du compute ou du mécanisme de migration. Une reprise du graphe, sur deux autorisées, a été utilisée.

### Limites et reste à faire

- Manifest conservé à **19.0.1.0.0**. Migration non livrée `19.0.1.0.1/post-recompute-amount-total.py` réutilisée pour D-03, appelée explicitement sur copie. **Incrément de version et déclenchement automatique de migration à vérifier à /odoo-close avant livraison.**
- Recette complète de release (base neuve, tours, désinstallation) non exécutée dans cette tâche. Aucun écran modifié, aucune capture ou documentation client produite. Release ouverte, validation locale seulement, aucun déploiement.
- Dette de manifest préexistante : author absent, masquée hors périmètre par le lint ; warnings de transport déjà connus. Aucun warning de vue, aucun bloquant restant.
- Comparaison standard 19.1 toujours impossible, sources absentes.
- Candidate /odoo-feedback : la conservation des entrées métier n'implique pas celle des métadonnées d'audit ; une transaction de test unique peut masquer l'évolution de write_date.

Commit proposé (non exécuté, remplace la proposition D-02) : `[IMP] lab_rental: appliquer les frais de préparation D-03`.
