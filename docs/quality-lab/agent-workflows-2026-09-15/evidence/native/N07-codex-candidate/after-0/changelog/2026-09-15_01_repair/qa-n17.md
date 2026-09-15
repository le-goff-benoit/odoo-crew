# QA — VALIDÉ

Issue proposée pour la réception : `pass`.
Couverture déclarée : 7/7 critères couverts.

Source du contrat :
> changelog/2026\-09\-15\_01\_repair/revue\_fonctionnelle\.md

SHA-256 de la source : `9b678b572ff66d8eeaa854c32518deb910867e0d87a10c89f672d62efd8a03cf`.
SHA-256 du contrat : `cfab486ad7a6b758c9888a163c0170a93b9b3a66bb91cf0373d5cc27b4233fa2`.

## Critères et références

> \*\*A1\*\* — Le cron prépare seulement les drafts automatiques au restant positif ou zéro \(livraison égale/supérieure incluse\), conserve les drafts manuels et tous les done, et son rejeu conserve les valeurs\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\-vert\.json

SHA-256 : `2bbe820cdfe87ac2b097103b0e08a616e61645a94557c7535f53f8e22ac862e8`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/qa\-runtime\.md

SHA-256 : `de914542e3f768d20fcd43034990fe2e7c3e41edf7835c27757f5d183ccf07e8`.

> \*\*A2\*\* — action\_set\_manual enregistre la quantité et manual=True, y compris zéro ; un cron ultérieur conserve ces saisies\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\-vert\.json

SHA-256 : `2bbe820cdfe87ac2b097103b0e08a616e61645a94557c7535f53f8e22ac862e8`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/qa\-runtime\.md

SHA-256 : `de914542e3f768d20fcd43034990fe2e7c3e41edf7835c27757f5d183ccf07e8`.

> \*\*A3\*\* — copy\(\) conserve ordered\_qty et réinitialise delivered\_qty=0, prepared\_qty=0, manual=False, state=draft ; la source est inchangée et le cron prépare la nouvelle demande complète, y compris une source terminée/manuelle\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\-vert\.json

SHA-256 : `2bbe820cdfe87ac2b097103b0e08a616e61645a94557c7535f53f8e22ac862e8`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/qa\-runtime\.md

SHA-256 : `de914542e3f768d20fcd43034990fe2e7c3e41edf7835c27757f5d183ccf07e8`.

> \*\*A4\*\* — action\_remainder singleton positif crée un draft au restant exact, delivered\_qty=0, prepared\_qty=0, manual=False, parent\_id=source ; la source passe done sans écraser prepared\_qty\. Le cron suivant prépare le reliquat et laisse la source intacte\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\-vert\.json

SHA-256 : `2bbe820cdfe87ac2b097103b0e08a616e61645a94557c7535f53f8e22ac862e8`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/qa\-runtime\.md

SHA-256 : `de914542e3f768d20fcd43034990fe2e7c3e41edf7835c27757f5d183ccf07e8`.

> \*\*A5\*\* — action\_remainder retourne un recordset vide sans création lorsque le reste est nul ou négatif ; une sélection multiple est rejetée sans modification\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\-vert\.json

SHA-256 : `2bbe820cdfe87ac2b097103b0e08a616e61645a94557c7535f53f8e22ac862e8`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/qa\-runtime\.md

SHA-256 : `de914542e3f768d20fcd43034990fe2e7c3e41edf7835c27757f5d183ccf07e8`.

> \*\*A6\*\* — Sur lab\_client déjà installé, après update, la reprise transforme ID 1 de 999 à 7 et préserve intégralement les lignes ID 2 \(zéro manuel\), ID 3 \(manuel 2\) et ID 4 \(done 88\)\. Un rejeu ne change pas les résultats et aucune ligne n'est créée\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/reprise\.json

SHA-256 : `3e6e51a4e177f8172f6a4f2fa9a863003fce3b3d1ce8cbe6a6bcb26e50e309cb`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/rejeu\.json

SHA-256 : `a52689613ef199fc0c31d2ebceec2041ccc9c745c4e38986149072da64708a70`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/update\.log

SHA-256 : `3ea43d98ad65452e0b1423f22a47530ec9a78c3418f329f73d743fb68ab8542c`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/qa\-copie\.md

SHA-256 : `91fd61bd1582f94f85772392623ebf1a597dd7d2187623e3d2a2efe424a6dc52`.

> \*\*A7\*\* — Les tests ciblés sont capturés rouges avant correction puis verts après correction ; lint du diff, installation QA et update de la copie sont vérifiés\. La release reste ouverte et aucun déploiement n'est effectué\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\-vert\.json

SHA-256 : `2bbe820cdfe87ac2b097103b0e08a616e61645a94557c7535f53f8e22ac862e8`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/qa\-runtime\.md

SHA-256 : `de914542e3f768d20fcd43034990fe2e7c3e41edf7835c27757f5d183ccf07e8`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\-rouge\.log

SHA-256 : `9e9b51eddb7146041e69c5da28a0de2bd5d43b6af36cf92d68246dfeafcd64e3`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/lint\.log

SHA-256 : `3706218c70e10eac08da715ecdeb986e232e0ec67a9c4a99f8718a7610ac5522`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/lint\-diff\.log

SHA-256 : `08d9a812958b2d08d9a114cc4241bc86e1347b9f3130a6b0f4c7509384aefa26`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/dette\-manifest\.txt

SHA-256 : `874611838adb082d8941f57913f7371ac4b92208a574233d228bd64db240ff00`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/qa\-statique\.md

SHA-256 : `4917bc150f22bc2a373b7ad76da4b8a43aa318082db2287b501ab3776a58fa7b`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/update\.log

SHA-256 : `3ea43d98ad65452e0b1423f22a47530ec9a78c3418f329f73d743fb68ab8542c`.

## Portée

Ce rapport vérifie le contrat, les statuts et les références. Les statuts restent déclaratifs : la pertinence métier des preuves exige une relecture. Aucun build, environnement ou contrôle supplémentaire n’est attesté par ce rendu.
La transition du flow est enregistrée séparément par complete.
