# QA d'exécution indépendante — 2026-09-09

**Module** `lab_qualification` · **série** 19.0 (origine : manifest, briefing fourni) · **mode** QA de tâche renforcée, voie runtime.

**VALIDÉ pour cette voie.** Les exécutions Odoo ci-dessous sont celles du développeur, réutilisées après revue indépendante de leurs assertions, logs, commandes, images et hashes. **Zéro nouveau test Odoo exécuté par la QA** ; aucun besoin concret de répétition ou d'élargissement n'a été trouvé.

## Exécutions réutilisées

La commande `python3 integration/runtime.py test --tags '/lab_qualification:TestQuantity,/lab_qualification:TestConfirmation'` lance effectivement `-u lab_qualification --test-enable` sur **ordered_copy**. Le `.json` de chaque passage conserve argv, image immutable, code de sortie et durée. Les deux logs archivés sont identiques aux originaux sous `integration/evidence/`.

| Contrôle | Résultat | Preuve originale |
|---|---|---|
| Installation initiale | Réutilisée : module initial installé avant dump/restauration | `../evidence/run-ordered_seed-20260909-183746-71a5184a.log:150`, `:153` ; aucune nouvelle installation finale revendiquée |
| Rouge authentique | 8 échecs / 0 erreur / 20 tests, sortie 1, 2,852 s | `../developer/red/test-ordered_copy-20260909-190409-e2e7801f.log:172`, `.json`, `.tests.json` |
| Update + vert | 0 échec / 0 erreur / 20 tests, sortie 0, 2,687 s | `../developer/green/test-ordered_copy-20260909-190501-1a622b24.log:16`, `:62`, `.json`, `.tests.json` |
| Sélection effective | Les mêmes 20 noms démarrés, 16 nouveaux + 4 initiaux ; pas de skip | Log vert lignes 26–58 ; vérification indépendante du parseur dans `verification.json` |
| Logs | Aucune erreur de vue, aucun warning, aucun module ignoré | Log vert ; seules erreurs SQL attendues des 2 anciens tests négatifs, lignes 46–56 |
| Environnement | Image Odoo identique aux argv rouge/vert, PostgreSQL enregistré actif, image et label propriétaire conformes | `live-odoo-image.log`, `live-container.log`, `verification.json` |

Les huit rouges sont des absences de `CheckViolation` pour créations confirmé zéro explicite/défaut, bouton zéro, recordset mixte, écriture d'état et écriture de zéro sur confirmé ; les deux imports acceptent à tort des IDs (log rouge lignes 65–77). Ce sont de vrais contre-exemples métier, pas des erreurs de banc. Dans le vert, les erreurs SQL des anciens tests négatifs sont suivies de leurs marqueurs `QUALIFICATION_PASS negative_create` (ligne 50) et `negative_write` (ligne 56), puis du bilan 20/20. La ligne de statistiques « 24 tests » à la ligne 61 n'est pas le nombre de méthodes démarrées ; le bilan Odoo et les 20 noms sont l'oracle retenu.

## Assertions relues indépendamment

Sources des tests : `run/project/lab_qualification/tests/`, sous la racine integration.

| AC | Assertion et opération exactes | Nom démarré / ligne du log vert | État |
|---|---|---|---|
| AC01 | `test_confirmation.py:12` crée zéro explicite et défaut ; `:19` écrit zéro ; helper flush/invalidation/relecture | `TestConfirmation.test_draft_zero_explicit_and_default` :30 ; `test_draft_write_zero` :29 | Couvert |
| AC02 | `:25` UID distinct de SUPERUSER_ID, su False, groupe interne ; bouton sur 1 et relecture confirmed/1/10. Ancien `test_quantity.py:35` confirme 3, montant 30 | `test_positive_boundary_confirmation` :37 ; `TestQuantity.test_confirmation` :43 | Couvert |
| AC03 | `:34` bouton zéro dans savepoint, exception attendue, relecture draft/0/0 après rollback | `test_zero_confirmation_rejected` :41 | Couvert |
| AC04 | `:44` création ordonnée [3, 0], un appel sur recordset, rejet et relecture des deux lignes draft/3/30 et draft/0/0 après rollback | `test_mixed_confirmation_atomic` :34 | Couvert |
| AC05 | `:58`, `:66` create confirmé zéro explicite/défaut refusés, comptage avant/après ; `:74` create confirmé/1 accepté | `test_create_confirmed_zero_rejected` :28 ; `test_create_confirmed_default_zero_rejected` :26 ; `test_create_confirmed_positive` :27 | Couvert |
| AC06 | `:79`, `:88` refus écriture état puis quantité zéro ; valeurs antérieures relues. `:97` écriture simultanée confirmed/1 puis quantité3 acceptées | `test_write_state_zero_rejected` :40 ; `test_write_confirmed_quantity_zero_rejected` :38 ; `test_write_state_and_positive_quantity` :39 | Couvert |
| AC07 | `:105` vrai `load` création draft0/confirmed1 accepté ; `:117` vrai `load` confirmé0 rejeté, aucun ID invalide ; `:129` vrai `load` mise à jour `.id` vers0 rejetée, identité, nom et valeurs conservés | `test_load_valid_records` :33 ; `test_load_create_zero_confirmed_rejected` :31 ; `test_load_update_zero_confirmed_rejected` :32 | Couvert |
| AC08 | `:142`, `:150` refus -1 création/écriture sous utilisateur interne, conservation draft/3/30 ; anciens tests inchangés | `test_negative_create_internal_user` :35 ; `test_negative_write_internal_user_preserved` :36 ; anciens négatifs :45/:51 | Couvert |
| AC09 | `common.py:12` with_user commun aux nouveaux cas ; `test_confirmation.py:27` UID/su/groupe et `:36` su False sur refus ; ACL/vue inchangées | `test_positive_boundary_confirmation` :37 ; `test_zero_confirmation_rejected` :41 ; `static.md` | Couvert |

Le helper `common.py:14` appelle flush_all puis invalidate_recordset avant de relire état, quantité, prix et montant : les simples caches visuels ne constituent pas la preuve. Les savepoints entourent la mutation rejetée, après flush de la fixture, et la relecture intervient après la sortie du savepoint. Le cas mixte contient la ligne positive avant la ligne nulle ; aucune valeur initiale ne reste partiellement modifiée. L'import utilise réellement `load` et son `.id`, avec ses erreurs structurées, pas un substitut `create`.

AC10–AC11 : complétés par `copy.md`. AC12 : preuves de tests, contre-exemples, lint, update et revue QA prêtes pour la réception indépendante ; obligations finales de mémoire/plan encore à accomplir.

Pas de navigateur nouveau, de capture, de désinstallation ou de recette complète : périmètre fixé par `revue_fonctionnelle.md:78`, `:104`, `:127`. Le test navigateur préexistant reste inchangé et n'a pas été sélectionné. Aucun succès de navigateur n'est revendiqué.
