# QA — À REPRENDRE

Issue proposée pour la réception : `retry`.
Couverture déclarée : 1/2 critères couverts.

Source du contrat :
> changelog/2026\-09\-09\_04\_import/revue\_fonctionnelle\.md

SHA-256 de la source : `d8ec90b9c3566c0d99d89aaa2cf6ad8e928192e8db918ec19b785e13103fc20c`.
SHA-256 du contrat : `ee9dc64377de5ac8b0aefb78510e0c6e97df08111e070d34b98e4dabc5b70b45`.

## Critères et références

> \*\*I1\*\* — Installation, mise à jour et lint ciblé réussissent sans régression\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_04\_import/static\.md

SHA-256 : `4eb5bf510f5d83e94fa4443119ee1ba57c053030a9108e1ae106f5c894079556`.

Fichier référencé :
> changelog/2026\-09\-09\_04\_import/runtime\.md

SHA-256 : `7fc13c6b369e5ad321e61f81d6c6a200ce4ab2bacfadc3521b611cead7418282`.

> \*\*J73\*\* — Si la ligne 5 est invalide, le message reçu indique la ligne 5, aucune ligne du lot n'est conservée et les huit étiquettes préexistantes gardent exactement leurs identifiants et valeurs\.

Statut déclaré : `failed`.

Fichier référencé :
> changelog/2026\-09\-09\_04\_import/runtime\.md

SHA-256 : `7fc13c6b369e5ad321e61f81d6c6a200ce4ab2bacfadc3521b611cead7418282`.

Fichier référencé :
> changelog/2026\-09\-09\_04\_import/client\.md

SHA-256 : `187d9dd06cf9f2dee3cfe9521f971a2fff9b933537c33b125d79659f4e4c19e1`.

Fichier référencé :
> changelog/2026\-09\-09\_04\_import/static\.md

SHA-256 : `4eb5bf510f5d83e94fa4443119ee1ba57c053030a9108e1ae106f5c894079556`.

## Portée

Ce rapport vérifie le contrat, les statuts et les références. Les statuts restent déclaratifs : la pertinence métier des preuves exige une relecture. Aucun build, environnement ou contrôle supplémentaire n’est attesté par ce rendu.
La transition du flow est enregistrée séparément par complete.
