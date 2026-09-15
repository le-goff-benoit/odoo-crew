# QA — VALIDÉ

Issue proposée pour la réception : `pass`.
Couverture déclarée : 12/12 critères couverts.

Source du contrat :
> changelog/2026\-09\-15\_01\_repair/revue\_fonctionnelle\.md

SHA-256 de la source : `570aef022585f63edbc688b0fbc73061e245fd00f62a647070510e7775e5100a`.
SHA-256 du contrat : `6d9170d7258f24b9d3f6388efe922244d83344a46ffe89d82a7caad0e354ac9d`.

## Critères et références

> C1 — Étant donné un draft automatique \(\`manual=False\`, ordered=10, delivered=3\), quand le cron tourne, alors \`prepared\_qty = 7\`\.

Statut déclaré : `covered`.

Fichier référencé :
> lab\_preparation/tests/test\_preparation\.py

SHA-256 : `cf4730cfd14522d4894423d6e861f84b3f0f05a56067f6347596939497ed6cff`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_rouge\_avant\_correction\.txt

SHA-256 : `95072a5e554b677ba7cd39aed363b577f368ca231c57c58692ab92555b2fc598`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\_base\_neuve\.txt

SHA-256 : `def94ad35c8d2b92a07142d15f4b8db997b57a72123b394b44acfe3bb0a10b79`.

> C2 — Étant donné un draft automatique avec \`delivered\_qty &gt; ordered\_qty\`, quand le cron tourne, alors \`prepared\_qty = 0\` \(jamais de négatif\)\.

Statut déclaré : `covered`.

Fichier référencé :
> lab\_preparation/tests/test\_preparation\.py

SHA-256 : `cf4730cfd14522d4894423d6e861f84b3f0f05a56067f6347596939497ed6cff`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_rouge\_avant\_correction\.txt

SHA-256 : `95072a5e554b677ba7cd39aed363b577f368ca231c57c58692ab92555b2fc598`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\_base\_neuve\.txt

SHA-256 : `def94ad35c8d2b92a07142d15f4b8db997b57a72123b394b44acfe3bb0a10b79`.

> C3 — Étant donné une saisie manuelle à \*\*zéro\*\* \(\`action\_set\_manual\(0\)\`\), alors \`manual=True\` et, après passage du cron, \`prepared\_qty\` vaut toujours 0\.

Statut déclaré : `covered`.

Fichier référencé :
> lab\_preparation/tests/test\_preparation\.py

SHA-256 : `cf4730cfd14522d4894423d6e861f84b3f0f05a56067f6347596939497ed6cff`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_rouge\_avant\_correction\.txt

SHA-256 : `95072a5e554b677ba7cd39aed363b577f368ca231c57c58692ab92555b2fc598`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\_base\_neuve\.txt

SHA-256 : `def94ad35c8d2b92a07142d15f4b8db997b57a72123b394b44acfe3bb0a10b79`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/parcours\_copie\_shell\.txt

SHA-256 : `36d42671e376a42e2a0ca58607d48fc94e6e51ee597e51e1c054dd98e4eaf976`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/parcours\_copie\_rpc\.txt

SHA-256 : `30338c9982cc41f4fa32aa62f244559521a314379dfc729872e6dbddd9178041`.

> C4 — Étant donné une saisie manuelle partielle \(2 sur 10\), quand le cron tourne, alors \`prepared\_qty = 2\` inchangé\.

Statut déclaré : `covered`.

Fichier référencé :
> lab\_preparation/tests/test\_preparation\.py

SHA-256 : `cf4730cfd14522d4894423d6e861f84b3f0f05a56067f6347596939497ed6cff`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_rouge\_avant\_correction\.txt

SHA-256 : `95072a5e554b677ba7cd39aed363b577f368ca231c57c58692ab92555b2fc598`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\_base\_neuve\.txt

SHA-256 : `def94ad35c8d2b92a07142d15f4b8db997b57a72123b394b44acfe3bb0a10b79`.

> C5 — Étant donné un enregistrement \`done\`, quand le cron tourne, alors aucun de ses champs ne change\.

Statut déclaré : `covered`.

Fichier référencé :
> lab\_preparation/tests/test\_preparation\.py

SHA-256 : `cf4730cfd14522d4894423d6e861f84b3f0f05a56067f6347596939497ed6cff`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_rouge\_avant\_correction\.txt

SHA-256 : `95072a5e554b677ba7cd39aed363b577f368ca231c57c58692ab92555b2fc598`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\_base\_neuve\.txt

SHA-256 : `def94ad35c8d2b92a07142d15f4b8db997b57a72123b394b44acfe3bb0a10b79`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/cohorte\_avant\.json

SHA-256 : `8aa795653c5aa9be1474ae05831db7c39df3f6bec72e7b56b3aeaf393e836a1b`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/cohorte\_apres\.json

SHA-256 : `134db9d35ffeb58a8f9ce47ab90ab2194f426c97de6e9a94f99e3c30ce00d000`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/write\_date\_apres\_reprise\.json

SHA-256 : `e917a491b32b8a2ec34fca5fe39b6579b55201149c372d9db4bacfd4a30b1798`.

> C6 — Étant donné deux passages consécutifs du cron, alors le second ne modifie aucune valeur \(idempotence\)\.

Statut déclaré : `covered`.

Fichier référencé :
> lab\_preparation/tests/test\_preparation\.py

SHA-256 : `cf4730cfd14522d4894423d6e861f84b3f0f05a56067f6347596939497ed6cff`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\_base\_neuve\.txt

SHA-256 : `def94ad35c8d2b92a07142d15f4b8db997b57a72123b394b44acfe3bb0a10b79`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/write\_date\_apres\_reprise\.json

SHA-256 : `e917a491b32b8a2ec34fca5fe39b6579b55201149c372d9db4bacfd4a30b1798`.

> C7 — Étant donné une préparation avec delivered/prepared/manual renseignés, quand on la duplique, alors la copie a \`ordered\_qty\` identique, \`delivered\_qty=0\`, \`prepared\_qty=0\`, \`manual=False\`, \`state='draft'\`\.

Statut déclaré : `covered`.

Fichier référencé :
> lab\_preparation/tests/test\_preparation\.py

SHA-256 : `cf4730cfd14522d4894423d6e861f84b3f0f05a56067f6347596939497ed6cff`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_rouge\_avant\_correction\.txt

SHA-256 : `95072a5e554b677ba7cd39aed363b577f368ca231c57c58692ab92555b2fc598`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\_base\_neuve\.txt

SHA-256 : `def94ad35c8d2b92a07142d15f4b8db997b57a72123b394b44acfe3bb0a10b79`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/parcours\_copie\_shell\.txt

SHA-256 : `36d42671e376a42e2a0ca58607d48fc94e6e51ee597e51e1c054dd98e4eaf976`.

> C8 — Étant donné une copie d'un enregistrement \`done\` avec saisie manuelle, alors la copie est \`draft\` et automatique, et le cron la traite normalement\.

Statut déclaré : `covered`.

Fichier référencé :
> lab\_preparation/tests/test\_preparation\.py

SHA-256 : `cf4730cfd14522d4894423d6e861f84b3f0f05a56067f6347596939497ed6cff`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_rouge\_avant\_correction\.txt

SHA-256 : `95072a5e554b677ba7cd39aed363b577f368ca231c57c58692ab92555b2fc598`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\_base\_neuve\.txt

SHA-256 : `def94ad35c8d2b92a07142d15f4b8db997b57a72123b394b44acfe3bb0a10b79`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/parcours\_copie\_shell\.txt

SHA-256 : `36d42671e376a42e2a0ca58607d48fc94e6e51ee597e51e1c054dd98e4eaf976`.

> C9 — Étant donné une préparation ordered=10 delivered=4 prepared=6, quand \`action\_remainder\(\)\`, alors un nouveau draft ordered=6, delivered=0, prepared=0, manual=False, parent\_id=source ; la source est \`done\` et garde \`prepared\_qty=6\`\.

Statut déclaré : `covered`.

Fichier référencé :
> lab\_preparation/tests/test\_preparation\.py

SHA-256 : `cf4730cfd14522d4894423d6e861f84b3f0f05a56067f6347596939497ed6cff`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_rouge\_avant\_correction\.txt

SHA-256 : `95072a5e554b677ba7cd39aed363b577f368ca231c57c58692ab92555b2fc598`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\_base\_neuve\.txt

SHA-256 : `def94ad35c8d2b92a07142d15f4b8db997b57a72123b394b44acfe3bb0a10b79`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/parcours\_copie\_shell\.txt

SHA-256 : `36d42671e376a42e2a0ca58607d48fc94e6e51ee597e51e1c054dd98e4eaf976`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/parcours\_copie\_rpc\.txt

SHA-256 : `30338c9982cc41f4fa32aa62f244559521a314379dfc729872e6dbddd9178041`.

> C10 — Étant donné une préparation intégralement livrée \(delivered &gt;= ordered\), quand \`action\_remainder\(\)\`, alors recordset vide, aucune ligne créée, source \`done\`, \`prepared\_qty\` intacte \(H1\)\.

Statut déclaré : `covered`.

Fichier référencé :
> lab\_preparation/tests/test\_preparation\.py

SHA-256 : `cf4730cfd14522d4894423d6e861f84b3f0f05a56067f6347596939497ed6cff`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_rouge\_avant\_correction\.txt

SHA-256 : `95072a5e554b677ba7cd39aed363b577f368ca231c57c58692ab92555b2fc598`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\_base\_neuve\.txt

SHA-256 : `def94ad35c8d2b92a07142d15f4b8db997b57a72123b394b44acfe3bb0a10b79`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/parcours\_copie\_shell\.txt

SHA-256 : `36d42671e376a42e2a0ca58607d48fc94e6e51ee597e51e1c054dd98e4eaf976`.

> C11 — Étant donné plusieurs enregistrements, quand \`action\_remainder\(\)\` est appelée sur le recordset, alors une erreur de singleton est levée\.

Statut déclaré : `covered`.

Fichier référencé :
> lab\_preparation/tests/test\_preparation\.py

SHA-256 : `cf4730cfd14522d4894423d6e861f84b3f0f05a56067f6347596939497ed6cff`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/tests\_vert\_base\_neuve\.txt

SHA-256 : `def94ad35c8d2b92a07142d15f4b8db997b57a72123b394b44acfe3bb0a10b79`.

> C12 — Étant donné la copie \`lab\_client\` après mise à niveau, alors id 1 vaut 7 et les ids 2, 3, 4 sont strictement inchangés \(valeurs du tableau §1\)\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/cohorte\_avant\.json

SHA-256 : `8aa795653c5aa9be1474ae05831db7c39df3f6bec72e7b56b3aeaf393e836a1b`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/cohorte\_apres\.json

SHA-256 : `134db9d35ffeb58a8f9ce47ab90ab2194f426c97de6e9a94f99e3c30ce00d000`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/write\_date\_apres\_reprise\.json

SHA-256 : `e917a491b32b8a2ec34fca5fe39b6579b55201149c372d9db4bacfd4a30b1798`.

## Portée

Ce rapport vérifie le contrat, les statuts et les références. Les statuts restent déclaratifs : la pertinence métier des preuves exige une relecture. Aucun build, environnement ou contrôle supplémentaire n’est attesté par ce rendu.
La transition du flow est enregistrée séparément par complete.
