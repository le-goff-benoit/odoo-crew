# QA — VALIDÉ

Issue proposée pour la réception : `pass`.
Couverture déclarée : 12/12 critères couverts.

Source du contrat :
> changelog/2026\-09\-09\_01\_frais\-de\-preparation\-des\-locations/revue\_fonctionnelle\.md

SHA-256 de la source : `a846395461647c7233b71dda05335f77539553486c4dc5d2ed710e10dbdd3321`.
SHA-256 du contrat : `ebe8ae3fa71dc289110e941f7a60f7681f7e488011565b8dec2d6084da5c4480`.

## Critères et références

> Étant donné une location \(\`kind = rental\`\) de 4 jours à 10 EUR/jour, quand le montant est calculé, alors \`amount\_total\` vaut 52\.0 \(borne inclusive, Q1\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_runtime\.txt

SHA-256 : `a5c01c8c1b22ec1daa341f1f5ce3a8e717810ce5c6731bf1da7792f7c44aa609`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_high\_runtime\.md

SHA-256 : `ffed384fec801b9e21940124eafbc7a01b1ca3e4c77aaf6122c666dcd9dd9fda`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/copie\_client\_apres\.txt

SHA-256 : `591b5a109a540c7636f29bcbab2ae2edc770fb078de68e3f43cbc13dfd174b2b`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/copie\_client\_postconditions\.txt

SHA-256 : `7c3136e3f0e05e3eebe5e539cf80b4292821cb3d888c63a4e05d0346eef9c24a`.

> Étant donné une location de 3 jours à 10 EUR/jour, quand le montant est calculé, alors \`amount\_total\` vaut 30\.0 \(sous le seuil, pas de frais\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_runtime\.txt

SHA-256 : `a5c01c8c1b22ec1daa341f1f5ce3a8e717810ce5c6731bf1da7792f7c44aa609`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_high\_runtime\.md

SHA-256 : `ffed384fec801b9e21940124eafbc7a01b1ca3e4c77aaf6122c666dcd9dd9fda`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/copie\_client\_apres\.txt

SHA-256 : `591b5a109a540c7636f29bcbab2ae2edc770fb078de68e3f43cbc13dfd174b2b`.

> Étant donné une location de 7 jours à 10 EUR/jour, quand le montant est calculé, alors \`amount\_total\` vaut 82\.0 \(au\-dessus du seuil, frais appliqués une seule fois\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_runtime\.txt

SHA-256 : `a5c01c8c1b22ec1daa341f1f5ce3a8e717810ce5c6731bf1da7792f7c44aa609`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_high\_runtime\.md

SHA-256 : `ffed384fec801b9e21940124eafbc7a01b1ca3e4c77aaf6122c666dcd9dd9fda`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/copie\_client\_apres\.txt

SHA-256 : `591b5a109a540c7636f29bcbab2ae2edc770fb078de68e3f43cbc13dfd174b2b`.

> Étant donné un prêt \(\`kind = loan\`\) de 4 jours à 10 EUR/jour, quand le montant est calculé, alors \`amount\_total\` vaut 40\.0 \(prêts exclus, Q2\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_runtime\.txt

SHA-256 : `a5c01c8c1b22ec1daa341f1f5ce3a8e717810ce5c6731bf1da7792f7c44aa609`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_high\_runtime\.md

SHA-256 : `ffed384fec801b9e21940124eafbc7a01b1ca3e4c77aaf6122c666dcd9dd9fda`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/copie\_client\_apres\.txt

SHA-256 : `591b5a109a540c7636f29bcbab2ae2edc770fb078de68e3f43cbc13dfd174b2b`.

> Étant donné un prêt de 10 jours à 10 EUR/jour, quand le montant est calculé, alors \`amount\_total\` vaut 100\.0 \(aucun frais quelle que soit la durée\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_runtime\.txt

SHA-256 : `a5c01c8c1b22ec1daa341f1f5ce3a8e717810ce5c6731bf1da7792f7c44aa609`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_high\_runtime\.md

SHA-256 : `ffed384fec801b9e21940124eafbc7a01b1ca3e4c77aaf6122c666dcd9dd9fda`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/copie\_client\_apres\.txt

SHA-256 : `591b5a109a540c7636f29bcbab2ae2edc770fb078de68e3f43cbc13dfd174b2b`.

> Étant donné une location de 0 jour à 0 EUR/jour, quand le montant est calculé, alors \`amount\_total\` vaut 0\.0 \(aucun frais sur un enregistrement vide\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_runtime\.txt

SHA-256 : `a5c01c8c1b22ec1daa341f1f5ce3a8e717810ce5c6731bf1da7792f7c44aa609`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_high\_runtime\.md

SHA-256 : `ffed384fec801b9e21940124eafbc7a01b1ca3e4c77aaf6122c666dcd9dd9fda`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/copie\_client\_apres\.txt

SHA-256 : `591b5a109a540c7636f29bcbab2ae2edc770fb078de68e3f43cbc13dfd174b2b`.

> Étant donné une location de 5 jours à 0 EUR/jour, quand le montant est calculé, alors \`amount\_total\` vaut 12\.0 \(le forfait ne dépend pas du tarif\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_runtime\.txt

SHA-256 : `a5c01c8c1b22ec1daa341f1f5ce3a8e717810ce5c6731bf1da7792f7c44aa609`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_high\_runtime\.md

SHA-256 : `ffed384fec801b9e21940124eafbc7a01b1ca3e4c77aaf6122c666dcd9dd9fda`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/copie\_client\_apres\.txt

SHA-256 : `591b5a109a540c7636f29bcbab2ae2edc770fb078de68e3f43cbc13dfd174b2b`.

> Étant donné une location de 3 jours déjà enregistrée, quand \`days\` passe à 4, alors \`amount\_total\` stocké est recalculé et vaut 52\.0 \(le champ stocké suit la modification\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_runtime\.txt

SHA-256 : `a5c01c8c1b22ec1daa341f1f5ce3a8e717810ce5c6731bf1da7792f7c44aa609`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_high\_runtime\.md

SHA-256 : `ffed384fec801b9e21940124eafbc7a01b1ca3e4c77aaf6122c666dcd9dd9fda`.

> Étant donné une location de 5 jours, quand \`kind\` passe à \`loan\`, alors \`amount\_total\` stocké perd les 12 EUR \(le recalcul est symétrique\)\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_runtime\.txt

SHA-256 : `a5c01c8c1b22ec1daa341f1f5ce3a8e717810ce5c6731bf1da7792f7c44aa609`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_high\_runtime\.md

SHA-256 : `ffed384fec801b9e21940124eafbc7a01b1ca3e4c77aaf6122c666dcd9dd9fda`.

> Étant donné le montant d'une location, quand on le compare à D\-01, alors aucun montant proportionnel \(7 %\) n'apparaît : le forfait est fixe et vaut toujours 12\.0\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_runtime\.txt

SHA-256 : `a5c01c8c1b22ec1daa341f1f5ce3a8e717810ce5c6731bf1da7792f7c44aa609`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_high\_runtime\.md

SHA-256 : `ffed384fec801b9e21940124eafbc7a01b1ca3e4c77aaf6122c666dcd9dd9fda`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/copie\_client\_apres\.txt

SHA-256 : `591b5a109a540c7636f29bcbab2ae2edc770fb078de68e3f43cbc13dfd174b2b`.

> Étant donné la copie \`lab\_client\` après mise à jour du module, quand on compare les montants avant et après, alors seules les locations de 4 jours et plus ont augmenté, et de 12\.0 exactement\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/copie\_client\_avant\.txt

SHA-256 : `535333c894850fbde313f09903093baea4b1fc982d0635326bf1f305c85afbd4`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/copie\_client\_apres\.txt

SHA-256 : `591b5a109a540c7636f29bcbab2ae2edc770fb078de68e3f43cbc13dfd174b2b`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/copie\_client\_postconditions\.txt

SHA-256 : `7c3136e3f0e05e3eebe5e539cf80b4292821cb3d888c63a4e05d0346eef9c24a`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_client\_copy\.md

SHA-256 : `f551015ac51672dc3f2ef95ca91a6f0548b436b7197462224e2e234fb9839804`.

> Étant donné le module après la tâche, quand on l'inspecte, alors aucune vue, aucun droit et aucune dépendance n'ont été ajoutés\.

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/copie\_client\_postconditions\.txt

SHA-256 : `7c3136e3f0e05e3eebe5e539cf80b4292821cb3d888c63a4e05d0346eef9c24a`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/diff\.patch

SHA-256 : `52e036ac8bde6865c5e4365902124c5420a6ad9600d3163cc0848696d11428f2`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/lint\.txt

SHA-256 : `65d7d084166d8ddaa78303e6de00134787b716278a8a065ad6151bda55844dee`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/frais\-preparation/qa\_high\_static\.md

SHA-256 : `1ff85c06f96b8e96cc483ac1f4cc5d9f136e44406a00c7e4dcc8f23fb5ec250d`.

## Portée

Ce rapport vérifie le contrat, les statuts et les références. Les statuts restent déclaratifs : la pertinence métier des preuves exige une relecture. Aucun build, environnement ou contrôle supplémentaire n’est attesté par ce rendu.
La transition du flow est enregistrée séparément par complete.
