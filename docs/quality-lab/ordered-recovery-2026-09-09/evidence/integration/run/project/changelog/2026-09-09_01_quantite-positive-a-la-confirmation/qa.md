# QA — VALIDÉ

Issue proposée pour la réception : `pass`.
Couverture déclarée : 12/12 critères couverts.

Source du contrat :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/revue\_fonctionnelle\.md

SHA-256 de la source : `ad64b892e52786539fbf08b9a4d70559e3125c424198e4b907cd10b35564c712`.
SHA-256 du contrat : `c078392df6bee103253131cca51353e8516301a476efd75637a67ee54c9de1f2`.

## Critères et références

> \*\*AC01 — Brouillon zéro\*\* \(demande 8–9\) : étant donné une création au brouillon avec quantité explicite 0, puis une création sans quantité, quand elles sont enregistrées, alors elles sont acceptées avec quantité 0 et montant 0 ; une écriture de zéro sur un brouillon reste permise\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/result\.md

SHA-256 : `854405212bc1231681bdc3bac62f132ecfbd9f3a9faf8cce1544ab1f9a52425c`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/verification\.evidence\.json

SHA-256 : `ebe5226eb7f7311ed813f2bdeb5fcfb772ef84ba659684d48d8f166d0c07510e`.

> \*\*AC02 — Borne positive et bouton\*\* \(9–10\) : étant donné un brouillon quantité 1, prix 10, quand \`action\_confirm\(\)\` est appelé, alors il devient confirmé, quantité 1 et montant 10\. Le cas positif initial quantité 3 reste fonctionnel avec montant 30\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/result\.md

SHA-256 : `854405212bc1231681bdc3bac62f132ecfbd9f3a9faf8cce1544ab1f9a52425c`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/verification\.evidence\.json

SHA-256 : `ebe5226eb7f7311ed813f2bdeb5fcfb772ef84ba659684d48d8f166d0c07510e`.

> \*\*AC03 — Bouton zéro\*\* \(9–10\) : étant donné un brouillon quantité 0, quand le bouton est appelé, alors l'opération est refusée et, après rollback/savepoint et relecture, il reste brouillon, quantité 0, montant 0\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/result\.md

SHA-256 : `854405212bc1231681bdc3bac62f132ecfbd9f3a9faf8cce1544ab1f9a52425c`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/verification\.evidence\.json

SHA-256 : `ebe5226eb7f7311ed813f2bdeb5fcfb772ef84ba659684d48d8f166d0c07510e`.

> \*\*AC04 — Confirmation groupée atomique\*\* \(11–12\) : étant donné des brouillons quantité 3 et 0, quand leur recordset est confirmé en une opération, alors elle échoue ; après annulation et relecture, les deux états et leurs quantités/montants restent initiaux\. Placer la ligne positive avant la nulle rend observable une implémentation erronée qui traiterait les lignes successivement\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/result\.md

SHA-256 : `854405212bc1231681bdc3bac62f132ecfbd9f3a9faf8cce1544ab1f9a52425c`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/verification\.evidence\.json

SHA-256 : `ebe5226eb7f7311ed813f2bdeb5fcfb772ef84ba659684d48d8f166d0c07510e`.

> \*\*AC05 — Créations directes\*\* \(9–10\) : étant donné une création directe \`confirmed\`, quand la quantité vaut 0 ou est omise \(défaut 0\), alors elle est refusée et aucun nouvel enregistrement invalide ne subsiste ; quantité 1 doit être acceptée\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/result\.md

SHA-256 : `854405212bc1231681bdc3bac62f132ecfbd9f3a9faf8cce1544ab1f9a52425c`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/verification\.evidence\.json

SHA-256 : `ebe5226eb7f7311ed813f2bdeb5fcfb772ef84ba659684d48d8f166d0c07510e`.

> \*\*AC06 — Écritures directes\*\* \(9–10, 12–13\) : écrire l'état \`confirmed\` sur un brouillon à zéro, ou écrire quantité 0 sur un confirmé positif, est refusé ; les valeurs précédentes persistent après annulation\. Une écriture simultanée état confirmé/quantité 1 est acceptée\. Modifier la quantité d'un confirmé vers une autre valeur positive reste possible\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/result\.md

SHA-256 : `854405212bc1231681bdc3bac62f132ecfbd9f3a9faf8cce1544ab1f9a52425c`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/verification\.evidence\.json

SHA-256 : `ebe5226eb7f7311ed813f2bdeb5fcfb772ef84ba659684d48d8f166d0c07510e`.

> \*\*AC07 — Import réel par ORM\*\* \(10\) : via \`load\`, importer un nouveau confirmé à zéro et mettre à jour un confirmé existant vers zéro produit des erreurs, sans donnée invalide persistante ; un import de brouillon à zéro et un import de confirmé positif réussissent\. Préserver l'identité et les valeurs antérieures du confirmé après l'import refusé\. Un test \`create\` seul ne valide pas ce critère\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/result\.md

SHA-256 : `854405212bc1231681bdc3bac62f132ecfbd9f3a9faf8cce1544ab1f9a52425c`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/verification\.evidence\.json

SHA-256 : `ebe5226eb7f7311ed813f2bdeb5fcfb772ef84ba659684d48d8f166d0c07510e`.

> \*\*AC08 — Négatifs préexistants\*\* \(13–14\) : les créations et écritures de quantité \-1 restent refusées ; après une écriture rejetée sur une ligne quantité 3/prix 10, relire quantité 3 et montant 30\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/result\.md

SHA-256 : `854405212bc1231681bdc3bac62f132ecfbd9f3a9faf8cce1544ab1f9a52425c`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/verification\.evidence\.json

SHA-256 : `ebe5226eb7f7311ed813f2bdeb5fcfb772ef84ba659684d48d8f166d0c07510e`.

> \*\*AC09 — Droits et écran\*\* \(16–17\) : aucun changement d'ACL, règles, groupes ou vue ; un utilisateur interne non superutilisateur peut préparer et confirmer une ligne positive et rencontre le même refus pour zéro\. Aucun élargissement pour public/portail n'est introduit\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/result\.md

SHA-256 : `854405212bc1231681bdc3bac62f132ecfbd9f3a9faf8cce1544ab1f9a52425c`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/verification\.evidence\.json

SHA-256 : `ebe5226eb7f7311ed813f2bdeb5fcfb772ef84ba659684d48d8f166d0c07510e`.

> \*\*AC10 — Mise à niveau de la copie\*\* \(18–21\) : après update sur \`ordered\_copy\`, les IDs 1/2/3 et tous leurs noms, états, quantités, prix et montants égalent l'inventaire initial ; la nouvelle règle est réellement active\. Un inventaire distinct confirme \`ordered\_seed\` inchangée et encore au module initial\. Ne pas qualifier cette preuve de restauration client\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/result\.md

SHA-256 : `854405212bc1231681bdc3bac62f132ecfbd9f3a9faf8cce1544ab1f9a52425c`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/verification\.evidence\.json

SHA-256 : `ebe5226eb7f7311ed813f2bdeb5fcfb772ef84ba659684d48d8f166d0c07510e`.

> \*\*AC11 — Historique et effets interdits\*\* \(20\) : ni script de reprise ni update ne transforme automatiquement un confirmé invalide, ni ne modifie les lignes initiales valides\. Si une anomalie historique est constatée, la réception en rend compte et n'annonce pas une mise à niveau validée sans règle active\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/result\.md

SHA-256 : `854405212bc1231681bdc3bac62f132ecfbd9f3a9faf8cce1544ab1f9a52425c`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/verification\.evidence\.json

SHA-256 : `ebe5226eb7f7311ed813f2bdeb5fcfb772ef84ba659684d48d8f166d0c07510e`.

> \*\*AC12 — Preuves de livraison\*\* \(23–25\) : archiver au moins un nouveau contre\-exemple métier rouge exécuté sur le code initial, puis les mêmes attentes vertes après correction et les scénarios couvrant AC01–AC11 ; lint des fichiers touchés, update et tests ciblés réellement exécutés ; preuves soumises à réception indépendante à la porte QA\. La publication mémoire et la réception du plan suivent cette porte, selon les conditions de complétion ci\-dessous\. La release reste ouverte et aucun bilan ne prétend à une recette complète\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/result\.md

SHA-256 : `854405212bc1231681bdc3bac62f132ecfbd9f3a9faf8cce1544ab1f9a52425c`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_quantite\-positive\-a\-la\-confirmation/preuves/qa/verification\.evidence\.json

SHA-256 : `ebe5226eb7f7311ed813f2bdeb5fcfb772ef84ba659684d48d8f166d0c07510e`.

## Portée

Ce rapport vérifie le contrat, les statuts et les références. Les statuts restent déclaratifs : la pertinence métier des preuves exige une relecture. Aucun build, environnement ou contrôle supplémentaire n’est attesté par ce rendu.
La transition du flow est enregistrée séparément par complete.
