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
