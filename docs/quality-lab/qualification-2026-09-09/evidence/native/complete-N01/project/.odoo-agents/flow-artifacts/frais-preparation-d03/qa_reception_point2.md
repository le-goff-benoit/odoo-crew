# QA — VALIDÉ

Issue proposée pour la réception : `pass`.
Couverture déclarée : 14/14 critères couverts.

Source du contrat :
> changelog/2026\-09\-09\_01\_frais\-de\-preparation\-des\-locations/revue\_fonctionnelle\_point2\.md

SHA-256 de la source : `7e666b30d7efd346f8f289606b52ea2f3afb5ca10289e84c4bc6cd1596a049d4`.
SHA-256 du contrat : `e5f7e7117eda0056bc300fbab6da574c584b3b096d8b9213f4cbf10ec0505a51`.

## Critères et références

> Étant donné une location \(\`kind = rental\`\) de 5 jours à 10 EUR/jour, quand le montant est calculé, alors \`amount\_total\` vaut 65\.0 \(nouvelle borne, inclusive\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\.txt

SHA-256 : `cee484fd82d3ee0c3b0bd30321869cb62c24009d2688f35ed5cf1c74c5a9788a`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\_update\.txt

SHA-256 : `417b9aaa825f5df222928a8e0013e8b99eb7b10017ef4c7c24af948c09a5cd7b`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/rpc\_seuil\.txt

SHA-256 : `2973779c053efff1614063dd8f5c87762553d9f89322779cf72722f63c679dfb`.

> Étant donné une location de 4 jours à 10 EUR/jour, quand le montant est calculé, alors \`amount\_total\` vaut 40\.0 : sous le nouveau seuil, plus aucun forfait — c'est le renversement de D\-02\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\.txt

SHA-256 : `cee484fd82d3ee0c3b0bd30321869cb62c24009d2688f35ed5cf1c74c5a9788a`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\_update\.txt

SHA-256 : `417b9aaa825f5df222928a8e0013e8b99eb7b10017ef4c7c24af948c09a5cd7b`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/rpc\_seuil\.txt

SHA-256 : `2973779c053efff1614063dd8f5c87762553d9f89322779cf72722f63c679dfb`.

> Étant donné une location de 3 jours à 10 EUR/jour, quand le montant est calculé, alors \`amount\_total\` vaut 30\.0\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\.txt

SHA-256 : `cee484fd82d3ee0c3b0bd30321869cb62c24009d2688f35ed5cf1c74c5a9788a`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\_update\.txt

SHA-256 : `417b9aaa825f5df222928a8e0013e8b99eb7b10017ef4c7c24af948c09a5cd7b`.

> Étant donné une location de 7 jours à 20 EUR/jour, quand le montant est calculé, alors \`amount\_total\` vaut 155\.0 \(forfait appliqué une seule fois\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\.txt

SHA-256 : `cee484fd82d3ee0c3b0bd30321869cb62c24009d2688f35ed5cf1c74c5a9788a`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\_update\.txt

SHA-256 : `417b9aaa825f5df222928a8e0013e8b99eb7b10017ef4c7c24af948c09a5cd7b`.

> Étant donné un prêt \(\`kind = loan\`\) de 5 jours à 10 EUR/jour, quand le montant est calculé, alors \`amount\_total\` vaut 50\.0 \(prêts exclus\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\.txt

SHA-256 : `cee484fd82d3ee0c3b0bd30321869cb62c24009d2688f35ed5cf1c74c5a9788a`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\_update\.txt

SHA-256 : `417b9aaa825f5df222928a8e0013e8b99eb7b10017ef4c7c24af948c09a5cd7b`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/rpc\_seuil\.txt

SHA-256 : `2973779c053efff1614063dd8f5c87762553d9f89322779cf72722f63c679dfb`.

> Étant donné un prêt de 10 jours à 10 EUR/jour, quand le montant est calculé, alors \`amount\_total\` vaut 100\.0 \(aucune durée ne rend un prêt payant\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\.txt

SHA-256 : `cee484fd82d3ee0c3b0bd30321869cb62c24009d2688f35ed5cf1c74c5a9788a`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\_update\.txt

SHA-256 : `417b9aaa825f5df222928a8e0013e8b99eb7b10017ef4c7c24af948c09a5cd7b`.

> Étant donné une location de 0 jour à 0 EUR/jour, quand le montant est calculé, alors \`amount\_total\` vaut 0\.0\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\.txt

SHA-256 : `cee484fd82d3ee0c3b0bd30321869cb62c24009d2688f35ed5cf1c74c5a9788a`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\_update\.txt

SHA-256 : `417b9aaa825f5df222928a8e0013e8b99eb7b10017ef4c7c24af948c09a5cd7b`.

> Étant donné une location de 5 jours à 0 EUR/jour, quand le montant est calculé, alors \`amount\_total\` vaut 15\.0 \(le forfait ne dépend pas du tarif\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\.txt

SHA-256 : `cee484fd82d3ee0c3b0bd30321869cb62c24009d2688f35ed5cf1c74c5a9788a`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\_update\.txt

SHA-256 : `417b9aaa825f5df222928a8e0013e8b99eb7b10017ef4c7c24af948c09a5cd7b`.

> Étant donné une location de 4 jours déjà enregistrée, quand \`days\` passe à 5, alors \`amount\_total\` stocké est recalculé et vaut 65\.0\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\.txt

SHA-256 : `cee484fd82d3ee0c3b0bd30321869cb62c24009d2688f35ed5cf1c74c5a9788a`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\_update\.txt

SHA-256 : `417b9aaa825f5df222928a8e0013e8b99eb7b10017ef4c7c24af948c09a5cd7b`.

> Étant donné une location de 6 jours, quand \`kind\` passe à \`loan\`, alors \`amount\_total\` stocké perd exactement 15\.0 \(recalcul symétrique\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\.txt

SHA-256 : `cee484fd82d3ee0c3b0bd30321869cb62c24009d2688f35ed5cf1c74c5a9788a`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\_update\.txt

SHA-256 : `417b9aaa825f5df222928a8e0013e8b99eb7b10017ef4c7c24af948c09a5cd7b`.

> Étant donné deux locations de même durée et de tarifs très différents, quand on retranche \`jours × tarif\`, alors le reste vaut 15\.0 dans les deux cas : le forfait n'est ni proportionnel \(D\-01, 7 %\) ni de 12\.0 \(D\-02\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\.txt

SHA-256 : `cee484fd82d3ee0c3b0bd30321869cb62c24009d2688f35ed5cf1c74c5a9788a`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/qa\_runtime\_update\.txt

SHA-256 : `417b9aaa825f5df222928a8e0013e8b99eb7b10017ef4c7c24af948c09a5cd7b`.

> Étant donné la copie \`lab\_client\` déjà porteuse des montants D\-02, quand le module est mis à niveau, alors la location de 4 jours redescend à 40\.0, celle de 7 jours passe à 155\.0, celle de 5 jours à tarif nul passe à 15\.0, et la location de 3 jours comme les deux prêts restent inchangés\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/copie\_client\_avant\.txt

SHA-256 : `7a1e767efbaf160f2984e17f7fe827070dfb95c0c2e101c0da0ec9b668c6cc2e`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/copie\_client\_update\.txt

SHA-256 : `1ab848722e9f07d637c1a05c63d8eada8a45a00bc96ac82c2c72114719bd669a`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/copie\_client\_apres\.txt

SHA-256 : `12f20a2ae33a0732e4013e50d51182c700079935058de71624876f8c5379c1f5`.

> Étant donné la copie \`lab\_client\`, quand la mise à niveau est rejouée une seconde fois, alors aucun montant ne change : la reprise est idempotente\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/copie\_client\_update2\.txt

SHA-256 : `ee10457df46a3e87b0037638b9ed28541b9f35f4a507d744c04d8e7749662a46`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/copie\_client\_postconditions\.txt

SHA-256 : `2665a2aa7ed6648b5cb330b2efcabbd743c331a5c352775d053adb93841a1525`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/copie\_client\_idempotence\.txt

SHA-256 : `d3c872773a009f7a82e35eb114828c6394f155dc21e102a491b3adabc43af3e5`.

> Étant donné le module après la tâche, quand on l'inspecte, alors aucune vue, aucun droit, aucun champ et aucune dépendance n'ont été ajoutés\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/copie\_client\_postconditions\.txt

SHA-256 : `2665a2aa7ed6648b5cb330b2efcabbd743c331a5c352775d053adb93841a1525`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/diff\.patch

SHA-256 : `3f278229546194a99c8df00d4873fd46322b0c2b4ce7117f19b0d1665723a756`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation\-d03/lint\.txt

SHA-256 : `65d7d084166d8ddaa78303e6de00134787b716278a8a065ad6151bda55844dee`.

## Portée

Ce rapport vérifie le contrat, les statuts et les références. Les statuts restent déclaratifs : la pertinence métier des preuves exige une relecture. Aucun build, environnement ou contrôle supplémentaire n’est attesté par ce rendu.
La transition du flow est enregistrée séparément par complete.
