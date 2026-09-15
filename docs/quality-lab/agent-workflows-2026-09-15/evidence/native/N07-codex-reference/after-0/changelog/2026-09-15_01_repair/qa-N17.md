# QA — VALIDÉ

Issue proposée pour la réception : `pass`.
Couverture déclarée : 7/7 critères couverts.

Source du contrat :
> changelog/2026\-09\-15\_01\_repair/revue\_fonctionnelle\.md

SHA-256 de la source : `4e425a4234d69b6dda8fbd915aa14290592e30bfa1ff0423f0ee1c4197d88ab1`.
SHA-256 du contrat : `032e90a18e79d756e85c32221bebe1005bd33fae73b5f0ba9a8efcb9c8cad1f8`.

## Critères et références

> \*\*A1\*\* — N\-17 : le cron calcule le solde positif ou zéro seulement pour les drafts automatiques ; conserve intégralement les drafts manuels \(zéro inclus\) et les done ; rejeu idempotent\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/green\.json

SHA-256 : `089a81af0a180e9a7f4423c7d3cd913cd2e7dea9765c81cf5ad0a5225a45e789`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/runtime\.md

SHA-256 : `607606c9760622be33d7effe2e8cc53014579350518fb039a7418eb4aa453c52`.

> \*\*A2\*\* — N\-17 : action\_set\_manual conserve exactement une quantité explicite, dont zéro, avec manual=True ; cron ultérieur conserve cette saisie sur une sélection mixte\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/green\.json

SHA-256 : `089a81af0a180e9a7f4423c7d3cd913cd2e7dea9765c81cf5ad0a5225a45e789`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/runtime\.md

SHA-256 : `607606c9760622be33d7effe2e8cc53014579350518fb039a7418eb4aa453c52`.

> \*\*A3\*\* — N\-17 : copy\(\) conserve ordered\_qty et réinitialise delivered\_qty=0, prepared\_qty=0, manual=False, state=draft ; un cron ultérieur prépare toute cette nouvelle demande sans altérer la source done\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/green\.json

SHA-256 : `089a81af0a180e9a7f4423c7d3cd913cd2e7dea9765c81cf5ad0a5225a45e789`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/runtime\.md

SHA-256 : `607606c9760622be33d7effe2e8cc53014579350518fb039a7418eb4aa453c52`.

> \*\*A4\*\* — N\-17 : action\_remainder singleton avec reste positif crée un seul draft pour ce reste, delivered\_qty=prepared\_qty=0, manual=False, parent\_id=source ; source done conserve prepared\_qty ; cron puis rejeu préparent le reliquat et préservent la source\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/green\.json

SHA-256 : `089a81af0a180e9a7f4423c7d3cd913cd2e7dea9765c81cf5ad0a5225a45e789`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/runtime\.md

SHA-256 : `607606c9760622be33d7effe2e8cc53014579350518fb039a7418eb4aa453c52`.

> \*\*A5\*\* — N\-17 : sans reste positif \(égalité ou dépassement\), action\_remainder retourne un recordset vide sans création ; l'appel non singleton échoue avant toute mutation\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/green\.json

SHA-256 : `089a81af0a180e9a7f4423c7d3cd913cd2e7dea9765c81cf5ad0a5225a45e789`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/runtime\.md

SHA-256 : `607606c9760622be33d7effe2e8cc53014579350518fb039a7418eb4aa453c52`.

> \*\*A6\*\* — Demande et N\-17 : reprise des drafts automatiques existants de lab\_client uniquement ; id 1 passe de 999 à 7, ids 2/3/4 restent respectivement à 0/2/88 avec tous leurs champs conservés ; rejeu stable et relecture persistée\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/repair\.json

SHA-256 : `f816aa5f4563d421439d1962c16d0a3a26d94deb1ab256b4464be8d6b4851bb6`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/persisted\.json

SHA-256 : `66ad41b30536ee6069e55ce6e1ee34006d330164904e331b7b834695f6707e7a`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/client\-copy\.md

SHA-256 : `c7b71487774b6fb6eb3d4c2b1dd42e57e4f9677a733af87da71b09a0ebf9b54a`.

> \*\*A7\*\* — Demande : tests rouges sur code initial puis verts sur correctif, couvrant zéro manuel, duplication, reliquat puis cron ; installation/tests ciblés, lint du diff et update sur copie existante réussis\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/red\-confirmed\.log

SHA-256 : `53e70851bb86d1425a558f250d2bc8adc6464414ed8862ba01625d455cf08deb`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/green\.json

SHA-256 : `089a81af0a180e9a7f4423c7d3cd913cd2e7dea9765c81cf5ad0a5225a45e789`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/static\.md

SHA-256 : `094c6f443e5df81dfecf47b6cf5a8941ee54bd12dd63a31e9f18332486edcd63`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/lint\.log

SHA-256 : `b65e713330f4789704c4df3f4996f68fef454e07b8accb386cf88bf60edddd13`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/manifest\-before\.txt

SHA-256 : `5b7f1619b99ecffd7c89381366ce0c6019d8b1c19fb98f9672c758113fa6af6a`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/preuves/update\-confirmed\.json

SHA-256 : `45b9f3fca615d53b6795a2459e1cc4cb07563cf758e419c9a39d346bcc98f712`.

## Portée

Ce rapport vérifie le contrat, les statuts et les références. Les statuts restent déclaratifs : la pertinence métier des preuves exige une relecture. Aucun build, environnement ou contrôle supplémentaire n’est attesté par ce rendu.
La transition du flow est enregistrée séparément par complete.
