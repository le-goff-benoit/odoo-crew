# QA — VALIDÉ

Issue proposée pour la réception : `pass`.
Couverture déclarée : 10/10 critères couverts.

Source du contrat :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/revue\_fonctionnelle\.md

SHA-256 de la source : `6a737c51d5e92a4589ebba8938548bab2e08de1c5ba61eec1d58882760085909`.
SHA-256 du contrat : `1ad2d824f6adb9ef798da4903c2bc606fbe288ccb731811b86e7c2c4ad993fff`.

## Critères et références

> C1 — Le champ \`x\_studio\_needs\_review\` existe sur \`x\_lab\_request\` : type booléen, \`store = True\`, \`compute\` renseigné, \`depends = x\_studio\_days,x\_studio\_kind\`, \`readonly = True\`, état \`manual\`\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/08\_qa\_etat\_base\.txt

SHA-256 : `bba1db70a5058b8423da2bfdb4fb82874069344dfa80f28264ac753d65849178`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/09\_qa\_scenario\_rejeu\.txt

SHA-256 : `403e8d92604e1a56172c57e29503cdf505f2e94884efcca3028f469963bc9bee`.

> C2 — Une location de 7 jours \(\`x\_studio\_kind = 'rental'\`, \`x\_studio\_days = 7\`\) donne \`x\_studio\_needs\_review = True\` après relecture serveur \(seuil inclus\)\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/09\_qa\_scenario\_rejeu\.txt

SHA-256 : `403e8d92604e1a56172c57e29503cdf505f2e94884efcca3028f469963bc9bee`.

> C3 — Une location de 6 jours donne \`False\` ; une location de 30 jours donne \`True\`\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/09\_qa\_scenario\_rejeu\.txt

SHA-256 : `403e8d92604e1a56172c57e29503cdf505f2e94884efcca3028f469963bc9bee`.

> C4 — Un prêt \(\`loan\`\) donne \`False\` à 7 jours comme à 30 jours\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/09\_qa\_scenario\_rejeu\.txt

SHA-256 : `403e8d92604e1a56172c57e29503cdf505f2e94884efcca3028f469963bc9bee`.

> C5 — Un genre vide et une durée nulle ou négative donnent \`False\` \(pas d'erreur\)\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/09\_qa\_scenario\_rejeu\.txt

SHA-256 : `403e8d92604e1a56172c57e29503cdf505f2e94884efcca3028f469963bc9bee`.

> C6 — Le recalcul suit la modification : passer une demande de 6 à 7 jours la fait basculer à \`True\` ; repasser \`rental\` en \`loan\` la fait revenir à \`False\`\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/09\_qa\_scenario\_rejeu\.txt

SHA-256 : `403e8d92604e1a56172c57e29503cdf505f2e94884efcca3028f469963bc9bee`.

> C7 — Les champs existants \`x\_name\`, \`x\_studio\_days\`, \`x\_studio\_kind\` sont inchangés \(mêmes ids, mêmes XML\-ID \`lab\_seed\_\*\`\) et aucun doublon n'a été créé\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/08\_qa\_etat\_base\.txt

SHA-256 : `bba1db70a5058b8423da2bfdb4fb82874069344dfa80f28264ac753d65849178`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/09\_qa\_scenario\_rejeu\.txt

SHA-256 : `403e8d92604e1a56172c57e29503cdf505f2e94884efcca3028f469963bc9bee`.

> C8 — Le script de construction est idempotent : deux applications successives laissent exactement un champ \`x\_studio\_needs\_review\` et un seul XML\-ID\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/02\_build\_application\_1\.txt

SHA-256 : `8517a34d355a53c9c968bfe653131ea5a594c5b38bd56ffaecf464067bebc8f2`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/03\_build\_application\_2\.txt

SHA-256 : `e9e0c2e01940e08f6bc9513d067cc665866b8f97727355d4acbcc3f6a68f4a19`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/08\_qa\_etat\_base\.txt

SHA-256 : `bba1db70a5058b8423da2bfdb4fb82874069344dfa80f28264ac753d65849178`.

> C9 — Le pack \`pack\.json\` est exporté, \`odoo\_pack\.py diff\` ne rapporte aucun écart sur la copie, et il ne contient aucune référence \`unresolved\`\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/pack\.json

SHA-256 : `ae83f479b6e2b7b4c0b96ab52da303ed02342391aeae2331b9854ce08be9fb7d`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/05\_pack\_export\.txt

SHA-256 : `28e8da43952e874be96cf06b7d10f0c7c3ff8c200728b9bf9104efcc02712119`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/07\_qa\_pack\_diff\.txt

SHA-256 : `c911526d51470a987215b9662d28b6806c8d83f631acfc3d38af6153923a6620`.

> C10 — Le XML\-ID créé est relevé dans \`created\.txt\`, sous \`studio\_customization\`, marqué Studio\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/created\.txt

SHA-256 : `0f79438b3193d4e37fb462e4bc944e6b1081b1d99e835a4c56a56cc9d1b9e077`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_indicateur\-de\-revue\-sur\-les\-demandes\-ast/studio/preuves/08\_qa\_etat\_base\.txt

SHA-256 : `bba1db70a5058b8423da2bfdb4fb82874069344dfa80f28264ac753d65849178`.

## Portée

Ce rapport vérifie le contrat, les statuts et les références. Les statuts restent déclaratifs : la pertinence métier des preuves exige une relecture. Aucun build, environnement ou contrôle supplémentaire n’est attesté par ce rendu.
La transition du flow est enregistrée séparément par complete.
