# QA — VALIDÉ

Issue proposée pour la réception : `pass`.
Couverture déclarée : 12/12 critères couverts.

Source du contrat :
> changelog/2026\-09\-15\_01\_repair/revue\_fonctionnelle\.md

SHA-256 de la source : `63b37562d6c1072e4a947dcb0a40a36983e81993c318c2772e39532961e11684`.
SHA-256 du contrat : `39bbb7d6723898a72c972e5d511e19b952a0b4ad83879b081355c1aee3eee90e`.

## Critères et références

> \*\*C1\*\* — Étant donné une préparation \`draft\` non manuelle \(\`ordered=10\`, \`delivered=3\`\), quand le cron passe, alors \`prepared\_qty = 7\`\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.log

SHA-256 : `f55fea85d9d6b3a537e9b3f4d51256312335a63805c5fd957af10de21e1c9907`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.json

SHA-256 : `78518532d5adf6746da6d116bf42f7a661a67d3b939b4681fda01100c31bfc6d`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_rouge\.log

SHA-256 : `61c82eda1fe2520c1781868ea58c5f2fc551f619af5cde5d8d5fc4077ea7b127`.

> \*\*C2\*\* — Étant donné \`delivered &gt; ordered\` \(\`ordered=10\`, \`delivered=12\`\), quand le cron passe, alors \`prepared\_qty = 0\` et jamais une valeur négative\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.log

SHA-256 : `f55fea85d9d6b3a537e9b3f4d51256312335a63805c5fd957af10de21e1c9907`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.json

SHA-256 : `78518532d5adf6746da6d116bf42f7a661a67d3b939b4681fda01100c31bfc6d`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_rouge\.log

SHA-256 : `61c82eda1fe2520c1781868ea58c5f2fc551f619af5cde5d8d5fc4077ea7b127`.

> \*\*C3\*\* — Étant donné \`action\_set\_manual\(0\)\`, alors \`prepared\_qty = 0\` \*\*et\*\* \`manual = True\` ; quand le cron passe ensuite, alors \`prepared\_qty\` reste 0\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.log

SHA-256 : `f55fea85d9d6b3a537e9b3f4d51256312335a63805c5fd957af10de21e1c9907`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.json

SHA-256 : `78518532d5adf6746da6d116bf42f7a661a67d3b939b4681fda01100c31bfc6d`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_rouge\.log

SHA-256 : `61c82eda1fe2520c1781868ea58c5f2fc551f619af5cde5d8d5fc4077ea7b127`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/rpc\_c3\_read\.json

SHA-256 : `3200c251e6fd0c19ebaa3bccb994a0b054beac3a3d4409e886c7f78d05db2541`.

> \*\*C4\*\* — Étant donné \`action\_set\_manual\(2\)\` sur \`ordered=10, delivered=3\`, quand le cron passe, alors \`prepared\_qty\` reste 2\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.log

SHA-256 : `f55fea85d9d6b3a537e9b3f4d51256312335a63805c5fd957af10de21e1c9907`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.json

SHA-256 : `78518532d5adf6746da6d116bf42f7a661a67d3b939b4681fda01100c31bfc6d`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_rouge\.log

SHA-256 : `61c82eda1fe2520c1781868ea58c5f2fc551f619af5cde5d8d5fc4077ea7b127`.

> \*\*C5\*\* — Étant donné une préparation \`done\` non manuelle avec \`prepared\_qty = 88\`, quand le cron passe, alors \`prepared\_qty\` reste 88 et l'état reste \`done\`\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.log

SHA-256 : `f55fea85d9d6b3a537e9b3f4d51256312335a63805c5fd957af10de21e1c9907`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.json

SHA-256 : `78518532d5adf6746da6d116bf42f7a661a67d3b939b4681fda01100c31bfc6d`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_rouge\.log

SHA-256 : `61c82eda1fe2520c1781868ea58c5f2fc551f619af5cde5d8d5fc4077ea7b127`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/cohorte\_apres\.txt

SHA-256 : `07ca85c7e72e831ae15c19cf79cd73ce843aebf2ef26173fa6540fff17769ac1`.

> \*\*C6\*\* — Étant donné le cron joué deux fois de suite sur la même base, alors le second passage ne change aucune valeur \(idempotence\)\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.log

SHA-256 : `f55fea85d9d6b3a537e9b3f4d51256312335a63805c5fd957af10de21e1c9907`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.json

SHA-256 : `78518532d5adf6746da6d116bf42f7a661a67d3b939b4681fda01100c31bfc6d`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/cron\_declenche\.txt

SHA-256 : `34cd917957b6207a013706d5987183f2be6b04ed78422979310adcb2febd0e23`.

> \*\*C7\*\* — Étant donné une préparation \`done\` avec \`delivered=4\`, \`prepared=88\`, \`manual=True\`, quand elle est dupliquée, alors la copie a \`ordered\_qty\` identique, \`delivered\_qty = 0\`, \`prepared\_qty = 0\`, \`manual = False\`, \`state = 'draft'\`, et l'original est inchangé\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.log

SHA-256 : `f55fea85d9d6b3a537e9b3f4d51256312335a63805c5fd957af10de21e1c9907`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.json

SHA-256 : `78518532d5adf6746da6d116bf42f7a661a67d3b939b4681fda01100c31bfc6d`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_rouge\.log

SHA-256 : `61c82eda1fe2520c1781868ea58c5f2fc551f619af5cde5d8d5fc4077ea7b127`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/rpc\_c7\_read\.json

SHA-256 : `78995dc9d44773daa24b8a64529a250e6aab808961b891234cf82825aeeff278`.

> \*\*C8\*\* — Étant donné \`ordered=10\`, \`delivered=3\`, \`prepared=5\`, quand \`action\_remainder\(\)\` est appelée, alors un \`draft\` est créé avec \`ordered\_qty = 7\`, \`delivered\_qty = 0\`, \`prepared\_qty = 0\`, \`manual = False\`, \`parent\_id\` = la source ; la source passe \`done\` avec \`prepared\_qty\` toujours à 5\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.log

SHA-256 : `f55fea85d9d6b3a537e9b3f4d51256312335a63805c5fd957af10de21e1c9907`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.json

SHA-256 : `78518532d5adf6746da6d116bf42f7a661a67d3b939b4681fda01100c31bfc6d`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_rouge\.log

SHA-256 : `61c82eda1fe2520c1781868ea58c5f2fc551f619af5cde5d8d5fc4077ea7b127`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/rpc\_c8\_read\.json

SHA-256 : `2556baa73379a29ecaad2a090da449288cba5ce4224913432583cdf655fa9536`.

> \*\*C9\*\* — Étant donné \`ordered=10\`, \`delivered=10\` \(puis \`delivered=12\`\), quand \`action\_remainder\(\)\` est appelée, alors elle retourne un recordset vide, aucun enregistrement n'est créé et la source n'est pas modifiée \(H1\)\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.log

SHA-256 : `f55fea85d9d6b3a537e9b3f4d51256312335a63805c5fd957af10de21e1c9907`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.json

SHA-256 : `78518532d5adf6746da6d116bf42f7a661a67d3b939b4681fda01100c31bfc6d`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_rouge\.log

SHA-256 : `61c82eda1fe2520c1781868ea58c5f2fc551f619af5cde5d8d5fc4077ea7b127`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/rpc\_c9\_read\.json

SHA-256 : `1e758dafa039758229da32fcf85801ce37744cd4458fbd9db9063d51291f51ae`.

> \*\*C10\*\* — Étant donné \`action\_remainder\(\)\` appelée sur deux enregistrements à la fois, alors une erreur de singleton est levée\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.log

SHA-256 : `f55fea85d9d6b3a537e9b3f4d51256312335a63805c5fd957af10de21e1c9907`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.json

SHA-256 : `78518532d5adf6746da6d116bf42f7a661a67d3b939b4681fda01100c31bfc6d`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/rpc\_c10\_remainder\.json

SHA-256 : `8b3b6034f5239bd08600307db321b1e89f8fd8875d827e76d9f2ac278a90a586`.

> \*\*C11\*\* — Étant donné une action planifiée déclarée pour ce modèle, alors elle existe en base et cible \`\_cron\_prepare\` \(H3\)\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.log

SHA-256 : `f55fea85d9d6b3a537e9b3f4d51256312335a63805c5fd957af10de21e1c9907`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\.json

SHA-256 : `78518532d5adf6746da6d116bf42f7a661a67d3b939b4681fda01100c31bfc6d`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_rouge\.log

SHA-256 : `61c82eda1fe2520c1781868ea58c5f2fc551f619af5cde5d8d5fc4077ea7b127`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/cron\_declenche\.txt

SHA-256 : `34cd917957b6207a013706d5987183f2be6b04ed78422979310adcb2febd0e23`.

> \*\*C12\*\* — Étant donné la copie \`lab\_client\` et sa cohorte, quand le module est mis à niveau, alors id 1 passe de 999 à 7 et les ids 2, 3, 4 gardent 0, 2 et 88 ; l'état de 4 reste \`done\`\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/cohorte\_avant\.txt

SHA-256 : `e28a4705023d8789e5cd1bfda66117c8958c5330611952f9b785ba77b280de49`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/cohorte\_apres\.txt

SHA-256 : `07ca85c7e72e831ae15c19cf79cd73ce843aebf2ef26173fa6540fff17769ac1`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/update\_reprise\_rejouee\.log

SHA-256 : `2c6777926e5644c1928cc7269bf1ca36ca89bee583d877ab770c94fa6abfa06c`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/cohorte\_apres\_rejeu\.txt

SHA-256 : `a8ec39455d11a647e3cacf9dabb75c042b3f04d5b68c64a149715ca2f95295cb`.

## Portée

Ce rapport vérifie le contrat, les statuts et les références. Les statuts restent déclaratifs : la pertinence métier des preuves exige une relecture. Aucun build, environnement ou contrôle supplémentaire n’est attesté par ce rendu.
La transition du flow est enregistrée séparément par complete.
