# QA — VALIDÉ

Issue proposée pour la réception : `pass`.
Couverture déclarée : 8/8 critères couverts.

Source du contrat :
> changelog/2026\-09\-09\_01\_interdiction\-des\-durees\-negatives\-sur\-le/revue\_fonctionnelle\.md

SHA-256 de la source : `1c21a476576bb9200de5f9921db78df1a351e6bb89870bba46ab1a744caff5e0`.
SHA-256 du contrat : `e34015f93922f231b04353290226591159774e945d86fd3e1518e982255d4128`.

## Critères et références

> Étant donné le module \`lab\_rental\` mis à jour sur \`lab\_client\`, quand on lit le code source du modèle, alors la contrainte \`days &gt;= 0\` est déclarée via \`models\.Constraint\('CHECK\(days &gt;= 0\)', \.\.\.\)\` \(pas \`\_sql\_constraints\`\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_high\_static/fragment\.md

SHA-256 : `cde123f3489832fddbedb2f3442bb3f817e756a6c1a329939bb33e825827c5a3`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_high\_static/logs/lint\.log

SHA-256 : `6af8dab6ba45a817336e4f99bf0cac24c1d6a1ad76d4bf3e5cad30a0e7f80863`.

> Étant donné la copie \`lab\_client\`, quand on met à jour le module \`lab\_rental\` \(\`/bridge/labctl update\`\), alors la mise à jour se termine sans erreur \(aucune ligne existante ne viole \`days &gt;= 0\`\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_client/logs/update\.log

SHA-256 : `2bf8fcf27346f003fc127cee6f23b48a22715415b85f5a8bcf5135d75b747a72`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_client/fragment\.md

SHA-256 : `81c59b8e7d47b1305a7268896190c27e4030add07fc00180593cf83d266c9fca`.

> Étant donné \`lab\_client\` via un appel XML\-RPC réel \(\`/bridge/labctl rpc\`\), quand on appelle \`create\` sur \`lab\.rental\` avec \`days=\-1\`, alors l'appel échoue \(\`Fault\`\) et le message renvoyé contient exactement la phrase « Le nombre de jours doit être positif ou nul\. »\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_client/rpc/01\_create\_negative\.json

SHA-256 : `2e2b68b240e2c0da0c64abe06b35aad0d2a8fb2968111cc602a2d67a1881f4ff`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_client/logs/01\_create\_negative\.log

SHA-256 : `c5d9384541b522a16db7358cb1a06594db7ebf6293aff0e1414479284810000a`.

> Étant donné un enregistrement \`lab\.rental\` existant valide \(\`days &gt;= 0\`\) créé en amont via XML\-RPC, quand on appelle \`write\` dessus avec \`days=\-1\` via XML\-RPC réel, alors l'appel échoue avec le même message que le critère précédent, et les valeurs de l'enregistrement \(\`days\`, \`daily\_rate\`, \`amount\_total\`\) restent inchangées après l'échec \(relecture par \`search\_read\` ou \`read\`\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_client/rpc/05\_write\_negative\.json

SHA-256 : `a7300226cbc83828f3308f9bcffb9663fb2bce8b8b20ce43cd57ae19602a9591`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_client/logs/05\_write\_negative\.log

SHA-256 : `c5d9384541b522a16db7358cb1a06594db7ebf6293aff0e1414479284810000a`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_client/logs/04\_read\_base\_before\.log

SHA-256 : `3b36dbc0679138246adb1ee31335b7c170ae95f023774d6b4b118a856ca67fa7`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_client/logs/06\_read\_base\_after\.log

SHA-256 : `3b36dbc0679138246adb1ee31335b7c170ae95f023774d6b4b118a856ca67fa7`.

> Étant donné \`lab\.rental\`, quand on crée ou modifie un enregistrement avec \`days=0\`, alors l'opération réussit \(via XML\-RPC réel\), sans erreur\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_client/logs/02\_create\_zero\.log

SHA-256 : `7d640eda7a8ac212452ef048c7c3e2f87f3c516715740d8d01542d92ea6ced99`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_client/logs/07\_write\_zero\.log

SHA-256 : `0be694460085656f05bf98a51c2e1aeacae073ef0282af69cb81ce8c1846633c`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_client/logs/08\_read\_zero\_after\.log

SHA-256 : `eb0b58e149462f36b6e6f9394c8da716850cdf71baf4fb56ebab3b11f9e30b3f`.

> Étant donné un enregistrement \`lab\.rental\` avec \`days\` et \`daily\_rate\` quelconques valides, quand on le lit après création ou modification, alors \`amount\_total == days \* daily\_rate\`\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_client/logs/04\_read\_base\_before\.log

SHA-256 : `3b36dbc0679138246adb1ee31335b7c170ae95f023774d6b4b118a856ca67fa7`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_client/logs/08\_read\_zero\_after\.log

SHA-256 : `eb0b58e149462f36b6e6f9394c8da716850cdf71baf4fb56ebab3b11f9e30b3f`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_high\_runtime/logs/qa\_fresh\.log

SHA-256 : `7a1fe39f02c3ace41fee4e8c7162bfd6b68b048e3bb3bc51e35a6135fe9f9ca3`.

> Étant donné une création \`lab\.rental\` valide suivie d'une tentative de \`write\(days=\-1\)\` refusée sur ce même enregistrement, quand on relit l'enregistrement, alors il existe toujours en base avec ses valeurs d'avant tentative \(aucune perte, aucun enregistrement partiel\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_client/rpc/06\_read\_base\_after\.json

SHA-256 : `fb607f0829b028c0eaa6bdc14639dc8b9af58bddc91210f3d40ad215fd39f0bd`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_client/logs/06\_read\_base\_after\.log

SHA-256 : `3b36dbc0679138246adb1ee31335b7c170ae95f023774d6b4b118a856ca67fa7`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_high\_runtime/logs/qa\_fresh\.log

SHA-256 : `7a1fe39f02c3ace41fee4e8c7162bfd6b68b048e3bb3bc51e35a6135fe9f9ca3`.

> Étant donné la suite de tests du module, quand on exécute \`/bridge/labctl qa lab\_rental\`, alors tous les tests passent, y compris les scénarios ci\-dessus couverts par un vrai appel RPC \(pas seulement des appels ORM internes\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_high\_runtime/logs/qa\_fresh\.log

SHA-256 : `7a1fe39f02c3ace41fee4e8c7162bfd6b68b048e3bb3bc51e35a6135fe9f9ca3`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_high\_runtime/logs/qa\_update\.log

SHA-256 : `a852ecc76153d07816d16fd1f20ac277cb622a1e28aa51241fdb178edb8c4e19`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_client/logs/01\_create\_negative\.log

SHA-256 : `c5d9384541b522a16db7358cb1a06594db7ebf6293aff0e1414479284810000a`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/contrainte\-jours\-positifs/qa\_client/logs/05\_write\_negative\.log

SHA-256 : `c5d9384541b522a16db7358cb1a06594db7ebf6293aff0e1414479284810000a`.

## Portée

Ce rapport vérifie le contrat, les statuts et les références. Les statuts restent déclaratifs : la pertinence métier des preuves exige une relecture. Aucun build, environnement ou contrôle supplémentaire n’est attesté par ce rendu.
La transition du flow est enregistrée séparément par complete.
