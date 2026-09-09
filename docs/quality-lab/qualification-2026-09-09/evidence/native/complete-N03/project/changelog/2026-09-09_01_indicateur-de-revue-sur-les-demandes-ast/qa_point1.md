# QA — VALIDÉ

Issue proposée pour la réception : `pass`.
Couverture déclarée : 13/13 critères couverts.

Source du contrat :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/revue\_fonctionnelle\.md

SHA-256 de la source : `3e5127f51cccfb1c70c2137450e6032ec0a6b8e5d831b8bfb83930b1d7dcaed2`.
SHA-256 du contrat : `534358c6d6cbe3c073d320ef2a6d1c0388abaef577b247c4f7a6ea63d973f955`.

## Critères et références

> C1 — Étant donné une demande \`x\_studio\_days = 7\` et \`x\_studio\_kind = 'rental'\`, quand elle est créée, alors \`x\_studio\_needs\_review\` relu depuis le serveur vaut \`True\` \(seuil inclusif, D\-22 Q1\)\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/test\_point1\_orm\.log

SHA-256 : `721bf4bba39ba087a556fd026003cbbd96f4ef0fa7d5310e35db968d3cce5f76`.

> C2 — Étant donné une demande \`x\_studio\_days = 30\` et \`x\_studio\_kind = 'rental'\`, quand elle est créée, alors \`x\_studio\_needs\_review\` vaut \`True\`\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/test\_point1\_orm\.log

SHA-256 : `721bf4bba39ba087a556fd026003cbbd96f4ef0fa7d5310e35db968d3cce5f76`.

> C3 — Étant donné une demande \`x\_studio\_days = 6\` et \`x\_studio\_kind = 'rental'\`, quand elle est créée, alors \`x\_studio\_needs\_review\` vaut \`False\`\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/test\_point1\_orm\.log

SHA-256 : `721bf4bba39ba087a556fd026003cbbd96f4ef0fa7d5310e35db968d3cce5f76`.

> C4 — Étant donné une demande \`x\_studio\_days = 7\` et \`x\_studio\_kind = 'loan'\`, quand elle est créée, alors \`x\_studio\_needs\_review\` vaut \`False\` \(prêts exclus, D\-22 Q2\)\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/test\_point1\_orm\.log

SHA-256 : `721bf4bba39ba087a556fd026003cbbd96f4ef0fa7d5310e35db968d3cce5f76`.

> C5 — Étant donné une demande \`x\_studio\_days = 30\` et \`x\_studio\_kind = 'loan'\`, quand elle est créée, alors \`x\_studio\_needs\_review\` vaut \`False\`\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/test\_point1\_orm\.log

SHA-256 : `721bf4bba39ba087a556fd026003cbbd96f4ef0fa7d5310e35db968d3cce5f76`.

> C6 — Étant donné une demande sans \`x\_studio\_kind\` et \`x\_studio\_days = 0\`, quand elle est créée, alors \`x\_studio\_needs\_review\` vaut \`False\`\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/test\_point1\_orm\.log

SHA-256 : `721bf4bba39ba087a556fd026003cbbd96f4ef0fa7d5310e35db968d3cce5f76`.

> C7 — Étant donné une demande à \`False\`, quand \`x\_studio\_days\` passe de 6 à 7, alors le champ stocké est recalculé à \`True\` sans autre intervention ; et l'inverse \(7 → 6\) le repasse à \`False\`\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/test\_point1\_orm\.log

SHA-256 : `721bf4bba39ba087a556fd026003cbbd96f4ef0fa7d5310e35db968d3cce5f76`.

> C8 — Étant donné une demande à \`True\`, quand \`x\_studio\_kind\` passe de \`rental\` à \`loan\`, alors le champ stocké est recalculé à \`False\`\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/test\_point1\_orm\.log

SHA-256 : `721bf4bba39ba087a556fd026003cbbd96f4ef0fa7d5310e35db968d3cce5f76`.

> C9 — Le champ est en base \`boolean\`, \`state = manual\`, \`store = True\`, \`readonly = True\`, \`depends = x\_studio\_days,x\_studio\_kind\`, et porte un XML\-ID sous \`studio\_customization\` — lu par XML\-RPC\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/test\_point1\_rpc\.log

SHA-256 : `95096ad9f97c10d6368c68667a24d586c3693bc2f809b74ec7da3c5a29e46417`.

> C10 — \`x\_name\`, \`x\_studio\_days\`, \`x\_studio\_kind\` ont les mêmes \`id\` et les mêmes XML\-ID \`lab\_seed\_\*\` qu'avant la tâche ; aucun champ dupliqué n'existe sur \`x\_lab\_request\` \(un seul champ dont le nom contient \`needs\_review\`\)\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/test\_point1\_rpc\.log

SHA-256 : `95096ad9f97c10d6368c68667a24d586c3693bc2f809b74ec7da3c5a29e46417`.

> C11 — Le script de construction et \`odoo\_pack\.py apply\` sont \*\*idempotents\*\* : deux applications successives ne créent aucun doublon et le nombre de champs du modèle est identique après la seconde\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/test\_point1\_idempotence\.log

SHA-256 : `751a880adf8b76f151a2f83195ab62a6c4b9a37b7abb572dc660bd716bd6e8ef`.

> C12 — \`odoo\_pack\.py diff pack\.json\` ne rapporte \*\*aucun\*\* écart après application\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/pack\_diff\.log

SHA-256 : `bb866876aab5aefb7f1c11d0c3d0473d970f9134bdcffdda20e9d77b042b5f93`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/test\_point1\_idempotence\.log

SHA-256 : `751a880adf8b76f151a2f83195ab62a6c4b9a37b7abb572dc660bd716bd6e8ef`.

> C13 — Aucun \`ir\.model\.access\`, \`ir\.rule\`, \`ir\.ui\.view\`, \`base\.automation\`, \`ir\.actions\.server\` ni \`ir\.cron\` n'a été créé ou modifié sur \`x\_lab\_request\` par la tâche\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/test\_point1\_rpc\.log

SHA-256 : `95096ad9f97c10d6368c68667a24d586c3693bc2f809b74ec7da3c5a29e46417`.

## Portée

Ce rapport vérifie le contrat, les statuts et les références. Les statuts restent déclaratifs : la pertinence métier des preuves exige une relecture. Aucun build, environnement ou contrôle supplémentaire n’est attesté par ce rendu.
La transition du flow est enregistrée séparément par complete.
