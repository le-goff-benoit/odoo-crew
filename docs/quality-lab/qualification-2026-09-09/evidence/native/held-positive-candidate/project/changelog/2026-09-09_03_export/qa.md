# QA — VALIDÉ

Issue proposée pour la réception : `pass`.
Couverture déclarée : 3/3 critères couverts.

Source du contrat :
> changelog/2026\-09\-09\_03\_export/revue\_fonctionnelle\.md

SHA-256 de la source : `d3bfd8559adda7c54500735bf66e2ad5f6ee6f6ac496e30ffe0dae51c06169b7`.
SHA-256 du contrat : `8113e97bc7d5e7ff817cd242dafc9e47f5d47d95689daffc22c7001c18172965`.

## Critères et références

> \*\*P1\*\* — Le CSV comporte exactement les identifiants 811, 821, 823 sans doublon et un total de quantité 12\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_03\_export/runtime\.md

SHA-256 : `6cc759e02f91d2b80f0ebedf6395c063ed6fd4b63a012a74e5df4ef2f3da614a`.

Fichier référencé :
> changelog/2026\-09\-09\_03\_export/export\.csv

SHA-256 : `4a42711a893b0f066eae27f556c538cafcce5ee8e4dfa4ba0ba1e6120cfe8eec`.

Fichier référencé :
> changelog/2026\-09\-09\_03\_export/client\.md

SHA-256 : `d46160badafde18a937302d89e36baa960f5771945cd74bc89ed565b48d96183`.

> \*\*P2\*\* — Les libellés contenant une virgule et les accents sont préservés après lecture par un vrai parseur CSV UTF\-8\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_03\_export/runtime\.md

SHA-256 : `6cc759e02f91d2b80f0ebedf6395c063ed6fd4b63a012a74e5df4ef2f3da614a`.

Fichier référencé :
> changelog/2026\-09\-09\_03\_export/export\.csv

SHA-256 : `4a42711a893b0f066eae27f556c538cafcce5ee8e4dfa4ba0ba1e6120cfe8eec`.

Fichier référencé :
> changelog/2026\-09\-09\_03\_export/client\.md

SHA-256 : `d46160badafde18a937302d89e36baa960f5771945cd74bc89ed565b48d96183`.

> \*\*P3\*\* — Installation, mise à jour et lint ciblé réussissent sans régression\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-09\_03\_export/static\.md

SHA-256 : `2920871fa67142db4e727d2af024f0dd521594f70b8424305075507f80689080`.

Fichier référencé :
> changelog/2026\-09\-09\_03\_export/runtime\.md

SHA-256 : `6cc759e02f91d2b80f0ebedf6395c063ed6fd4b63a012a74e5df4ef2f3da614a`.

Fichier référencé :
> changelog/2026\-09\-09\_03\_export/client\.md

SHA-256 : `d46160badafde18a937302d89e36baa960f5771945cd74bc89ed565b48d96183`.

## Portée

Ce rapport vérifie le contrat, les statuts et les références. Les statuts restent déclaratifs : la pertinence métier des preuves exige une relecture. Aucun build, environnement ou contrôle supplémentaire n’est attesté par ce rendu.
La transition du flow est enregistrée séparément par complete.
