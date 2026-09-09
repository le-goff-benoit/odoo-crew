# Verdict QA indépendante — 2026-09-09

**Module** `lab_qualification` · **série** 19.0 (origine : manifest, briefing-current.md fourni) · **mode** QA de tâche renforcée sur copie synthétique.

**VALIDÉ au niveau des trois voies QA, prêt pour réception indépendante à la porte.** Aucun bloquant, majeur ou défaut métier identifié. Les obligations finales AC12 restent à accomplir : réception documentaire indépendante, publication exacte des deux mémoires, clôture du flow et réception du plan. **La tâche n'est pas déclarée terminée et la release reste ouverte.**

| Contrôle | Résultat | Origine de la preuve |
|---|---|---|
| Diff et lint | 4 fichiers, 0 erreur / 0 avertissement ; revue indépendante conforme | Revue QA fraîche ; lint développeur réutilisé |
| Installation | Installation initiale réussie avant restauration | Bootstrap historique réutilisé ; pas d'installation finale fraîche |
| Rouge | 8 échecs métier / 0 erreur / 20 tests, 2,852 s | Exécution développeur réutilisée |
| Update et vert | 0 échec / 0 erreur / 20 tests, 2,687 s | Exécution développeur réutilisée, mêmes attentes |
| Données et schéma | IDs1/2/3 et toutes valeurs conservés sur chaque DB ; CHECK nouvelle validée seulement sur copie | Lectures QA fraîches psql READ ONLY |
| Fraîcheur | Module actuel intégralement égal au snapshot testé ; attentes rouge/vert byte-identiques ; images identiques | 88 contrôles QA, `verification.json`, preuve publique `verification.evidence.json` |
| Navigateur / release complète | Non exécutés, hors périmètre de tâche convenu | Aucune capture, aucune certification de release |

## Couverture des 12 critères

Les textes exacts restent dans `run/project/changelog/2026-09-09_01_quantite-positive-a-la-confirmation/revue_fonctionnelle.md:110` à `:121`. Les identifiants de couverture liés sont C01–C12, correspondant à AC01–AC12. Les liens de tests détaillés et lignes du log vert sont dans `runtime.md`; la copie est dans `copy.md`.

| Critère | Résultat de réception QA | Preuve exacte principale |
|---|---|---|
| AC01 | Couvert : zéro explicite, défaut et write, montants relus | `tests/test_confirmation.py:12`, `:19` ; log vert :29–30 |
| AC02 | Couvert : bouton1→confirmed/10 et cas3→30 | `tests/test_confirmation.py:25`, `tests/test_quantity.py:35` ; log vert :37/:43 |
| AC03 | Couvert : bouton zéro refusé, relecture après rollback | `tests/test_confirmation.py:34` ; log vert :41 |
| AC04 | Couvert : recordset [3,0], refus intégral et conservation des deux | `tests/test_confirmation.py:44` ; log vert :34 |
| AC05 | Couvert : créations confirmed0/défaut refusées, confirmed1 acceptée | `tests/test_confirmation.py:58`, `:66`, `:74` ; log vert :26–28 |
| AC06 | Couvert : les deux writes invalides et les writes positifs, conservation | `tests/test_confirmation.py:79`, `:88`, `:97` ; log vert :38–40 |
| AC07 | Couvert : vrais load création/mise à jour, refus et conservation ; imports valides | `tests/test_confirmation.py:105`, `:117`, `:129` ; log vert :31–33 |
| AC08 | Couvert : négatifs refusés en create/write et quantité3/montant30 conservés | `tests/test_confirmation.py:142`, `:150` ; log vert :35–36/:45/:51 |
| AC09 | Couvert : interne non su nominal/refus ; hashes ACL/vue inchangés | `tests/common.py:12`, `tests/test_confirmation.py:27`, `:36` ; `verification.json` |
| AC10 | Couvert : vraie mise à niveau et comparaison live distincte des deux bases | Log vert :16/:62 ; `live-ordered_copy.log:1`, `live-ordered_seed.log:1`, `copy.md` |
| AC11 | Couvert sur le jeu initial valide : aucune reprise, aucune valeur transformée | `reviewed-module-diff.log`, inventaires live ; branche historique invalide absente, limite conservée |
| AC12 | Partie QA satisfaite : rouge/vert identiques, lint/update, preuves soumises. Réception à la porte et complétion finale encore en attente | Logs rouge :172/vert :62, `static.md`, `verification.json` ; conditions contractuelles `revue_fonctionnelle.md:135` |

« Log vert » désigne exactement `../developer/green/test-ordered_copy-20260909-190501-1a622b24.log` ; « log rouge », `../developer/red/test-ordered_copy-20260909-190409-e2e7801f.log`. Les chemins de tests ci-dessus sont relatifs au module `integration/run/project/lab_qualification`.

## Portée, anomalies et suite

Aucune anomalie bloquante. Aucun test Odoo ni lint répété par la QA. Les erreurs SQL des anciens tests négatifs sont attendues et suivies de marqueurs de succès ; les deux incidents du vérificateur QA sont exposés dans `copy.md` sans les imputer au module. Les preuves génériques QA ne portent aucun faux bilan Odoo.

La nouvelle lecture QA concerne uniquement les bases synthétiques autorisées, en READ ONLY. Pas de navigateur nouveau, pas de recette complète, pas de modification du module/release/mémoires/flow/plan, pas de nettoyage. Aucun succès d'upgrade sur un historique invalide non présent dans la fixture n'est revendiqué.

L'orchestrateur doit fusionner ces fragments et leurs preuves sans transformer la réutilisation des tests en nouvelle exécution, puis obtenir la réception indépendante à la porte avant publication mémoire et réception du plan. Le contrat `revue_fonctionnelle.md:135` dit : « Ces obligations AC12 demeurent requises pour déclarer la tâche terminée ; elles ne sont pas présentées comme déjà réalisées dans les preuves QA qui les précèdent. »

À transmettre dans la mémoire après réception : quantité entière, zéro brouillon conservé, invariant confirmé strictement positif multicanal ; vraie CHECK validée sur copie synthétique ; préservation distincte de référence et copie ; preuves backend locales, pas recette complète ni donnée client.
