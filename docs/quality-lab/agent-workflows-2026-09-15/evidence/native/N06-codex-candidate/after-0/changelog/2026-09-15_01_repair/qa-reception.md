# QA — VALIDÉ

Issue proposée pour la réception : `pass`.
Couverture déclarée : 6/6 critères couverts.

Source du contrat :
> changelog/2026\-09\-15\_01\_repair/revue\_fonctionnelle\.md

SHA-256 de la source : `d6dd687ee1a9ee48fad98d55aef11e95bf2544491a5fdccfa3f45fd409594bfe`.
SHA-256 du contrat : `26a129052046bf49145001a4b5e64da1bbc13fd862904f430a8f658cb6eac6fa`.

## Critères et références

> C1 — Seuls les membres de self en draft dans env\.company sont réparés, même avec deux sociétés autorisées ; sélection mixte admise ; brouillon non sélectionné et sélection vide sans effet\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/green\.json

SHA-256 : `2cfdd0c6ee8706b2abdc885dc91b8e718a3331b634fa5a9580bf091c6fd07d96`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/qa\-runtime\.md

SHA-256 : `bdff4791ca85c672257ebe81f831a9da86699346114912f8c594c7294f9c9ee4`.

> C2 — Tri date\_document puis id, séquences 100,200,… ; snapshot\_total somme quantity\*price uniquement des lignes cancelled=False ; ligne vide/annulée, égalité de dates et petit écart non arrondi couverts\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/green\.json

SHA-256 : `2cfdd0c6ee8706b2abdc885dc91b8e718a3331b634fa5a9580bf091c6fd07d96`.

Fichier référencé :
> lab\_register/tests/test\_repair\.py

SHA-256 : `6e9b0a15c1c99df3ebef859f72c2bfe3c95cb548c0b68d427c0665787641a55f`.

> C3 — Les issued conservent state, sequence, snapshot\_total, reference ; autres sociétés et lignes inchangées, y compris métadonnées de modification ; changement de société active testé\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/green\.json

SHA-256 : `2cfdd0c6ee8706b2abdc885dc91b8e718a3331b634fa5a9580bf091c6fd07d96`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/repair\-verified\.json

SHA-256 : `c7bd1a055fa6314af9e33b27d097a1581b4e375d0b0637d0f61035737a4b6fd1`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/before\.json

SHA-256 : `7ec347841bae7ec721d0164390cafb8c85f4c1fb262a0f8b8bb35bbe4b063195`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/after\.json

SHA-256 : `01fb543383634de34c8dab80289c021e05a0273cba1dc295df83e0504389ed36`.

> C4 — Utilisateur interne ordinaire sans sudo : succès dans ses droits ; refus AccessError sur écriture et lecture interdites, postconditions inchangées ; ACL et règles existantes inchangées\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/green\.json

SHA-256 : `2cfdd0c6ee8706b2abdc885dc91b8e718a3331b634fa5a9580bf091c6fd07d96`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/copy\-rights\-v2\.json

SHA-256 : `12aa08e9b379133d3dd0917b7dbc3fe767bfd9341ae4637db609126bb66dc39e`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/static\-comparison\.txt

SHA-256 : `7650438762db859ea8093b0fdbf260861a4bc1a233fabaa1c3011f800f93b886`.

> C5 — Reprise persistée des deux brouillons historiques de société initiale 1 : id 1 = 100/20, id 2 = 200/15 ; références, issued id 3 et société 2 id 4 préservés\. Second passage : valeurs et write\_date stables et zéro appel write\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/repair\-authorized\.json

SHA-256 : `8a5ced6267129a91a247f425281d69e490b7fbcc350b8344116ce9a66abae54f`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/repair\-verified\.json

SHA-256 : `c7bd1a055fa6314af9e33b27d097a1581b4e375d0b0637d0f61035737a4b6fd1`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/qa\-client\.md

SHA-256 : `2a29d0259f96999b6e1de5eabdc9192f379416731d5e3a21c6ac963cf892d41d`.

> C6 — Test rouge sur ancien code puis vert sur correctif, lint du diff, install/tests ciblés et update lab\_client prouvés ; ancienne QA explicitement invalidée pour cette portée ; revue, QA et journal publiés ; release ouverte\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/red\.log

SHA-256 : `1cc7c39217012730991bbedcf03e5ca82ce3bdce53c626e9f6e69a3b88efda40`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/business\-before\.py

SHA-256 : `b24cfe215ce52d95a64fe963125bba0b883ef185f8062c58bf918ba72193bd02`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/green\.json

SHA-256 : `2cfdd0c6ee8706b2abdc885dc91b8e718a3331b634fa5a9580bf091c6fd07d96`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/update\.log

SHA-256 : `c34d5e39cb36ab4911f1a5158d1b3f09c0d71b53b3e112e05760cb11ecc3b5ea`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/copy\-rights\-v2\.json

SHA-256 : `12aa08e9b379133d3dd0917b7dbc3fe767bfd9341ae4637db609126bb66dc39e`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/lint\.log

SHA-256 : `148811d3bcd17b86197f2010f618736a2163fdde8aca15a56ad5bf2673b535b7`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/lint\-diff\.log

SHA-256 : `67318e71032ad04cbc232dbad3b5057373d28474640dc71cdf172d65597d7689`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/static\-comparison\.txt

SHA-256 : `7650438762db859ea8093b0fdbf260861a4bc1a233fabaa1c3011f800f93b886`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/qa\.md

SHA-256 : `7b68221e179245384aaa766d5a175e1700d0630de81f3992f89ec70c4f2ce191`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/reception\-documentaire\.md

SHA-256 : `5485de1adbe0231131a6299a142f8377382e8b2cbec98840f76011b5850a5931`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/publication\.json

SHA-256 : `48cd9fbe36aac26521bfe8127c04144e2e79cc425023dcd606991fa6c6aa9a0a`.

Fichier référencé :
> \.odoo\-agents/JOURNAL\.md

SHA-256 : `3f50d3917aaf0b26d049c83efb6d31e48c9625fdc4a8c105ccf8727e959cbfb2`.

## Portée

Ce rapport vérifie le contrat, les statuts et les références. Les statuts restent déclaratifs : la pertinence métier des preuves exige une relecture. Aucun build, environnement ou contrôle supplémentaire n’est attesté par ce rendu.
La transition du flow est enregistrée séparément par complete.
