# Livraison développeur — 2026-09-09

Série **Odoo 19.0**, module `lab_qualification` ; développement de tâche terminé, réception QA indépendante encore attendue. Release ouverte. Le briefing fourni, la demande, la revue et la consolidation ont été lus avant le code. Rôle développeur c19 figé appliqué.

## Changement livré

- `models.py` : contrainte `models.Constraint` nommée `_confirmed_quantity_positive`, `CHECK(state != 'confirmed' OR quantity > 0)`, message anglais explicite. La contrainte de non-négativité existante demeure ; les objets de table précèdent maintenant les champs. Deux docstrings courtes ajoutées. Aucun changement au calcul ou au corps du bouton.
- `tests/common.py` : fixture `LabQualificationCommon(TransactionCase)` et utilisateur `base.group_user`. Le module dépend seulement de `web` et n'a pas de Common métier plus spécifique pertinent. Toutes les nouvelles opérations métier utilisent `with_user`, sans `sudo` ; `env.su == False` et l'UID distinct du superutilisateur sont vérifiés.
- `tests/test_confirmation.py` : 16 tests métier nouveaux ; `tests/__init__.py` les charge.
- Les quatre tests initiaux dans `test_quantity.py`, le test navigateur existant, la vue, l'ACL, le manifest et le point d'entrée sont identiques octet pour octet au baseline. Pas de nouveau groupe ni règle. Version conservée à `19.0.1.0.0` pendant la release ouverte ; aucun champ stocké nouveau. Aucun script de reprise.

Précédents consultés : `19.0/addons/stock/models/stock_storage_category.py:64` pour `models.Constraint`, `19.0/odoo/addons/base/tests/test_sql.py:181` pour `CheckViolation`, `19.0/odoo/orm/models.py:895` pour le vrai canal `load`, `19.0/odoo/tests/common.py:195` pour `new_test_user`. Sources Odoo en lecture seule. Options runtime vérifiées dans `19.0/odoo/tools/config.py`.

## Rouge authentique puis vert

Commande commune, sur **ordered_copy uniquement** :

```text
python3 integration/runtime.py test --tags '/lab_qualification:TestQuantity,/lab_qualification:TestConfirmation'
```

Le runtime fait `-u lab_qualification` et les tests ciblés dans un même passage. Aucun appel de test/update sur `ordered_seed`.

| Passage | Preuve archivée dans developer/ | Résultat Odoo effectivement lu |
|---|---|---|
| Rouge avant correction | `red/test-ordered_copy-20260909-190409-e2e7801f.log` + `.json` + `.tests.json` | **8 failed, 0 error(s) of 20 tests**, 20 noms démarrés |
| Vert après correction | `green/test-ordered_copy-20260909-190501-1a622b24.log` + `.json` + `.tests.json` | **0 failed, 0 error(s) of 20 tests**, les mêmes 20 noms démarrés |

Les huit échecs rouges sont ceux de création confirmé zéro explicite/défaut, import création/mise à jour à zéro, recordset mixte, écriture quantité zéro sur confirmé, écriture état confirmé sur zéro et bouton zéro. Ils montrent soit `CheckViolation not raised`, soit un ID d'import accepté à tort ; aucune erreur de banc. Les quatre anciens marqueurs métier sont présents dans les deux passages.

`red/initial-module/` et `red/initial-hashes.json` figent le module avant invariant ; `red/tests/` et `red/test-hashes.json` figent les attentes exactes lancées. Le modèle initial était byte-identique avant le lancement rouge. `green/module/` et `green/final-hashes.json` figent le résultat. `verification.json` atteste l'égalité des tests rouge/vert, des 20 noms démarrés et des fichiers initiaux préservés. Aucun changement d'attente après le rouge.

## Couverture métier

| Critère | Preuve |
|---|---|
| AC01 | `test_draft_zero_explicit_and_default`, `test_draft_write_zero` : défaut/explicite 0 et retour à 0 acceptés, montants relus à 0 |
| AC02 | `test_positive_boundary_confirmation` : 1 → confirmed/10 ; ancien `test_confirmation` : 3 → confirmed/30 |
| AC03 | `test_zero_confirmation_rejected` : refus puis relecture draft/0/0 après savepoint |
| AC04 | `test_mixed_confirmation_atomic` : création ordonnée positif 3 puis zéro 0, un recordset, refus puis relecture des deux lignes draft/3/30 et draft/0/0 |
| AC05 | Deux refus de création confirmé (quantité 0 et absente) avec comptage avant/après ; création confirmé/1 acceptée |
| AC06 | `test_write_state_zero_rejected`, `test_write_confirmed_quantity_zero_rejected`, `test_write_state_and_positive_quantity` : refus et conservation, édition simultanée valide, édition positive ultérieure |
| AC07 | `test_load_valid_records`, `test_load_create_zero_confirmed_rejected`, `test_load_update_zero_confirmed_rejected` : appels réels `load`, erreurs structurées et absence de création invalide ; mise à jour par `.id`, identité/nom/état/quantité/prix/montant conservés |
| AC08 | Anciens tests négatifs intacts + deux nouveaux tests sous utilisateur interne : -1 refusé en création et écriture, draft/3/30 relu |
| AC09 | Les 16 nouveaux tests utilisent l'utilisateur interne non su. Assertions explicites UID/su/groupe dans le nominal et su dans le refus bouton. Hashes ACL/vue identiques ; pas d'élargissement public/portail |
| AC10 | Inventaires ORM actuels des deux bases intégralement égaux aux inventaires initiaux, y compris IDs 1/2/3, noms, états, quantités, prix, montants et module. Contrainte SQL nouvelle effectivement présente dans ordered_copy seulement |
| AC11 | Aucun script de reprise ajouté, aucune transformation historique. Les lignes initiales valides sont identiques ; aucun confirmé invalide historique dans le jeu initial |
| AC12 | Rouge/vert, tests exacts, logs, lint, diff et inventaires livrés. Réception indépendante, consolidation des mémoires et réception du plan restent à l'orchestrateur |

## Mise à niveau et contrôles

`green/inventory-ordered_copy-20260909-190531-7a23ab3f.inventory.json` égale intégralement `evidence/inventory-ordered_copy-20260909-183801-79429f03.inventory.json`.

`green/inventory-ordered_seed-20260909-190542-67c057d8.inventory.json` égale intégralement `evidence/inventory-ordered_seed-20260909-183759-07173621.inventory.json`.

`green/sql-inventory-ordered_copy-20260909-190532-d7eea9bc.log` contient `lab_qualification_confirmed_quantity_positive` ; `green/sql-inventory-ordered_seed-20260909-190543-2f32c97a.log` ne la contient pas et conserve la contrainte initiale. La version manifest n'ayant pas changé, c'est ce contrôle du schéma qui distingue l'update réel de la copie et le schéma initial de la référence. Les inventaires sont des lectures ORM/SQL sans commit ni update de la référence.

Lint des **4 fichiers touchés** via le script c19 figé : `reference/scripts/odoo-lint.sh --changed HEAD integration/run/project/lab_qualification`. `developer/lint.log` : série 19.0, ruff bloquant OK, contrôles Odoo **0 erreur, 0 avertissement**, sortie 0. Deux conseils non bloquants (tri des imports de l'init, virgule finale de la sélection préexistante) sans effet métier.

`module.diff` comprend le modèle et les nouveaux tests. Les quatre fichiers livrés sont ajoutés à l'index Git, **sans commit**, pour éviter une dépendance à des fichiers non suivis. Aucun fichier de release, mémoire, plan ou flow modifié par le développeur.

## Limites et suite

Preuve sur copie **synthétique** restaurée, pas restauration client. Pas de navigateur exécuté, aucune nouvelle interface ni parcours non trivial. Pas de recette complète, pas de fermeture de release, pas de déploiement. Le jeu ne contient pas d'historique invalide : aucun comportement de mise à niveau sur un tel historique n'est revendiqué. Les logs SQL d'erreur des deux anciens tests négatifs sont attendus et accompagnés de leurs marqueurs de succès.

Le schéma et les ressources locales restent disponibles pour la QA ; aucun nettoyage de la base ou du réseau. Base et module libérés pour le rôle suivant. Aucun défaut de banc rencontré.

Message de commit proposé : `[FIX] lab_qualification: require positive quantity on confirmed records`.
