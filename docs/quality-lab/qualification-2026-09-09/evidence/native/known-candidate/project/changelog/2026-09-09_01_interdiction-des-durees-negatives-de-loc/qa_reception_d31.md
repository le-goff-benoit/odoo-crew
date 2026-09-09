# QA — À REPRENDRE

Issue proposée pour la réception : `retry`.
Couverture déclarée : 8/9 critères couverts.

Source du contrat :
> changelog/2026\-09\-09\_01\_interdiction\-des\-durees\-negatives\-de\-loc/revue\_fonctionnelle\.md

SHA-256 de la source : `2061340268223878cb609c576a943d89662e04ba5cd25d5d6af003126591d513`.
SHA-256 du contrat : `cf836fabee213c0ac8f5869ad864b6739b8098b8e1b49ff863c167b6b2a62540`.

## Critères et références

> \*\*A1\*\* — Étant donné une location valide, quand on crée \`lab\.rental\` avec \`days = \-1\`,
>       alors la base refuse : \`psycopg2\.errors\.CheckViolation\` au flush, sous \`mute\_logger\('odoo\.sql\_db'\)\`\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-client/03\_a1\_a5\.log

SHA-256 : `24d80ca750233e3827bffa04d291cd6ab57b28ca95a032ff44a8eadefc17b32f`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-runtime/run1\-fresh\-tags\.log

SHA-256 : `9da0b6271c66486e56415b4ebb2ef6959fa43e081865ef5c94f5595ad8be8e6f`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-runtime/run2\-suite\-complete\.log

SHA-256 : `22ef159106901226c489252ffb8e33937cf1d574390c00856504077f4d576611`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/module\_client\_copy\_qa\.md

SHA-256 : `55b1f0b7074c7f4506358c7bbbe0a91ac3562180977dedc830a6fc2a00befb47`.

> \*\*A2\*\* — Étant donné une location existante à \`days = 5\`, quand on écrit \`days = \-3\`,
>       alors la base refuse de la même manière et la valeur en base reste \`5\`\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-client/03\_a1\_a5\.log

SHA-256 : `24d80ca750233e3827bffa04d291cd6ab57b28ca95a032ff44a8eadefc17b32f`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-runtime/run1\-fresh\-tags\.log

SHA-256 : `9da0b6271c66486e56415b4ebb2ef6959fa43e081865ef5c94f5595ad8be8e6f`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-runtime/run2\-suite\-complete\.log

SHA-256 : `22ef159106901226c489252ffb8e33937cf1d574390c00856504077f4d576611`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/module\_client\_copy\_qa\.md

SHA-256 : `55b1f0b7074c7f4506358c7bbbe0a91ac3562180977dedc830a6fc2a00befb47`.

> \*\*A3\*\* — Étant donné une création avec \`days = 0\`, alors elle réussit et \`amount\_total == 0\.0\`\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-client/03\_a1\_a5\.log

SHA-256 : `24d80ca750233e3827bffa04d291cd6ab57b28ca95a032ff44a8eadefc17b32f`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-runtime/run1\-fresh\-tags\.log

SHA-256 : `9da0b6271c66486e56415b4ebb2ef6959fa43e081865ef5c94f5595ad8be8e6f`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-runtime/run2\-suite\-complete\.log

SHA-256 : `22ef159106901226c489252ffb8e33937cf1d574390c00856504077f4d576611`.

> \*\*A4\*\* — Étant donné \`days = 4\` et \`daily\_rate = 12\.5\`, alors \`amount\_total == 50\.0\`
>       \(non\-régression du compute stocké\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-client/03\_a1\_a5\.log

SHA-256 : `24d80ca750233e3827bffa04d291cd6ab57b28ca95a032ff44a8eadefc17b32f`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-runtime/run1\-fresh\-tags\.log

SHA-256 : `9da0b6271c66486e56415b4ebb2ef6959fa43e081865ef5c94f5595ad8be8e6f`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-runtime/run2\-suite\-complete\.log

SHA-256 : `22ef159106901226c489252ffb8e33937cf1d574390c00856504077f4d576611`.

> \*\*A5\*\* — Étant donné une location valide créée puis un rejet \(A1 ou A2\) encadré par
>       \`self\.env\.cr\.savepoint\(\)\`, alors, après le rejet, la location valide est toujours lisible avec
>       ses valeurs intactes et le curseur reste utilisable pour la suite du test\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-client/03\_a1\_a5\.log

SHA-256 : `24d80ca750233e3827bffa04d291cd6ab57b28ca95a032ff44a8eadefc17b32f`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-runtime/run1\-fresh\-tags\.log

SHA-256 : `9da0b6271c66486e56415b4ebb2ef6959fa43e081865ef5c94f5595ad8be8e6f`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-runtime/run2\-suite\-complete\.log

SHA-256 : `22ef159106901226c489252ffb8e33937cf1d574390c00856504077f4d576611`.

> \*\*A6\*\* — Après \`\-u lab\_rental\` sur la copie, la contrainte existe réellement :
>       \`SELECT conname, pg\_get\_constraintdef\(oid\) FROM pg\_constraint WHERE conrelid='lab\_rental'::regclass\`
>       retourne \`lab\_rental\_check\_days\_positive\` avec \`CHECK \(\(days &gt;= 0\)\)\`\. Preuve à joindre à la QA\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-client/02\_a6\_after\_update\.log

SHA-256 : `2f13dd4c8edc0ffc563cd35db3fdaa3abf19653f5b39801757e9cf496cd26be5`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-client/09\_final\_state\.log

SHA-256 : `b6a856805959e75d8973014e61a1b71e96bd5b7fe062d89afc6edfb93c90a638`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-client/01\_update\.log

SHA-256 : `b1253e90394abd89e217653e5066e0ce00986cade3fd4c383f122c195d0951ba`.

> \*\*A7\*\* — Comportement sur données violantes, à jouer \*\*explicitement\*\* puisque la copie est vide :
>       insérer une ligne \`days = \-3\` en contournant l'ORM \(\`INSERT\` SQL direct\) \*\*avant\*\* l'update,
>       rejouer l'update, et constater/documenter que la contrainte n'est \*\*pas\*\* posée alors que l'update
>       se termine sans erreur \(risque 1\)\. Nettoyer la ligne, réappliquer, vérifier A6\. Si ce contrôle ne
>       peut pas être joué, le dire explicitement dans la QA — pas de succès supposé\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-client/04\_a7\_before\.log

SHA-256 : `69db81c521e2f7f42266996d90afe2252823cd3bb57775e11fd6eafb477e8271`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-client/05\_a7\_update\.log

SHA-256 : `b5e6175fe07f6b61b899160ce2d5455e1a066f8ccaa6be48a54c164afe4d017f`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-client/06\_a7\_after\.log

SHA-256 : `4aa043c7ec6c693b6bfe667744715c3c55d77bd4f5d5be3c85dfece20b5afbdd`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-client/07\_cleanup\.log

SHA-256 : `66147145dd578f4065e28b7934070f788c8c4ae01b5b328dcdfa6a4b8002dd9d`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-client/08\_reapply\_update\.log

SHA-256 : `bcf40385da957189ae3d134c68975a023d1fcbf57480c06c487843826c5b7269`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-client/09\_final\_state\.log

SHA-256 : `b6a856805959e75d8973014e61a1b71e96bd5b7fe062d89afc6edfb93c90a638`.

> \*\*A8\*\* — Le message d'erreur configuré est bien celui remonté à l'utilisateur \(non vide\),
>       et le module ne contient plus aucune occurrence de \`\_sql\_constraints\`\.

Statut déclaré : `partial`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-client/10\_a8\_message\.log

SHA-256 : `c79501f0ac9f5f81555c9d151b11243893b14d1f4879098c6340eaa637878f9a`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/module\_high\_static\_qa\.md

SHA-256 : `1ed04659dc01f6f5dd021b5405a4f630a1ed41d00d2e8bbdd09e570e38fe063f`.

> \*\*A9\*\* — \`labctl lint lab\_rental\` sans écart nouveau imputable au diff de la tâche\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/d31\-jours\-negatifs/logs/r2\-static/lint\.log

SHA-256 : `b0eedb907728188993c593a730b88b5f3dd243a032fda440e60cf2fb1e63a9d2`.

## Portée

Ce rapport vérifie le contrat, les statuts et les références. Les statuts restent déclaratifs : la pertinence métier des preuves exige une relecture. Aucun build, environnement ou contrôle supplémentaire n’est attesté par ce rendu.
La transition du flow est enregistrée séparément par complete.
