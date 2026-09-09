# QA — VALIDÉ

Issue proposée pour la réception : `pass`.
Couverture déclarée : 5/5 critères couverts.

Source du contrat :
> changelog/2026\-09\-09\_01\_revue\-des\-locations\-d\-22/revue\_fonctionnelle\.md

SHA-256 de la source : `81529f30669e23ec521c00ed791d44fefbc25439fe5c2ccfc26b27bfb6308f06`.
SHA-256 du contrat : `6edc453031f3063d5dcea80f7f3f1c0dbec3d5dfffb325caacb6ac3bba5ee56d`.

## Critères et références

> A1 — Ajouter seulement le booléen stocké calculé x\_studio\_needs\_review sur x\_lab\_request, avec dépendances x\_studio\_days et x\_studio\_kind ; réutiliser x\_name et ces deux champs sans les renommer ni les recréer\. \(Demande originale, D\-22\)

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/needs\-review/studio\_diff\.md

SHA-256 : `c9a4c0605e5ec11c675fba2dc548980a9c7eb4fbdde301b6c1b1f41380aa99d6`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/needs\-review/studio\_diff\.log

SHA-256 : `a43d6999a04484a20e2cca176f2e3aa156ca1c72fc33137064c7f2b03e803268`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_revue\-des\-locations\-d\-22/studio/pack\.json

SHA-256 : `6507bfae09677745a3e6d549a96e36cffb57f0f7a4767d0c4a386917909b49a8`.

> A2 — Relecture serveur : rental à 6 jours est faux, à 7 et au\-delà vrai ; loan à 7 et au\-delà reste faux ; les modifications de chacun des deux champs recalculent la valeur\. \(D\-22\)

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/needs\-review/studio\_runtime\.md

SHA-256 : `6ec55a6f3d60b7d2a2ca18037fb51e435651efc09124d985f0431ec9d3186dd7`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/needs\-review/studio\_runtime\.log

SHA-256 : `1e27a48083572f9c6bc7e4d829d0ccded5ebd63f274a6e6d72b059c1d98bf920`.

> A3 — Livrer pack Studio versionné et scénarios RPC rejouables, rouge avant et vert après, avec nettoyage ; deux applications du pack sans doublon, diff final nul et aucune référence unresolved\. \(Demande originale ; preuve rouge/vert et diff : protocole Studio\)

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/needs\-review/studio\_runtime\.md

SHA-256 : `6ec55a6f3d60b7d2a2ca18037fb51e435651efc09124d985f0431ec9d3186dd7`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/needs\-review/studio\_runtime\.log

SHA-256 : `1e27a48083572f9c6bc7e4d829d0ccded5ebd63f274a6e6d72b059c1d98bf920`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_revue\-des\-locations\-d\-22/studio/red\-before\.log

SHA-256 : `11f9cd0e806b1a4209f788c84df4b1dc5d47054d0fbf41282b31a520556c3465`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/needs\-review/versioning\.log

SHA-256 : `082f35a7e6b2a00ffe82877dabfe9b28532de4bfb9dbd76217c48fbab99a77d8`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/needs\-review/studio\_diff\.md

SHA-256 : `c9a4c0605e5ec11c675fba2dc548980a9c7eb4fbdde301b6c1b1f41380aa99d6`.

> A4 — Aucun écran, envoi, droit ou champ existant modifié, aucun module custom ni déploiement ; tests limités à la copie synthétique locale\. \(Demande originale, D\-22\)

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/needs\-review/studio\_diff\.md

SHA-256 : `c9a4c0605e5ec11c675fba2dc548980a9c7eb4fbdde301b6c1b1f41380aa99d6`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/needs\-review/implementation\.md

SHA-256 : `b627e137b06981ed9bbaafd3e1e6cdab6eb90b9bca549c7bb76364f58a1edd59`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/needs\-review/studio\_runtime\.md

SHA-256 : `6ec55a6f3d60b7d2a2ca18037fb51e435651efc09124d985f0431ec9d3186dd7`.

> A5 — Terminer QA et journal, mémoire fidèle à D\-22 et à la validation locale ; release laissée ouverte\. \(Demande originale, D\-22\)

Statut déclaré : `covered`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/needs\-review/lifecycle\.md

SHA-256 : `cb3caa505e92a55151a0c7395a925e37072865f9907307713c4fc7cd0d4285e4`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_revue\-des\-locations\-d\-22/reception/PROJECT\-propose\.md

SHA-256 : `f8c44f66a70a6e20aac1d42499c9d2927176350da58788f8df132ad8f6298664`.

Fichier référencé :
> changelog/2026\-09\-09\_01\_revue\-des\-locations\-d\-22/reception/JOURNAL\-propose\.md

SHA-256 : `efff3d3382ce941624a31ce521604b3beb78e45eb16af2b1227dccdbaa96d7d4`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/needs\-review/studio\_diff\.md

SHA-256 : `c9a4c0605e5ec11c675fba2dc548980a9c7eb4fbdde301b6c1b1f41380aa99d6`.

Fichier référencé :
> \.odoo\-agents/flow\-artifacts/needs\-review/studio\_runtime\.md

SHA-256 : `6ec55a6f3d60b7d2a2ca18037fb51e435651efc09124d985f0431ec9d3186dd7`.

## Portée

Ce rapport vérifie le contrat, les statuts et les références. Les statuts restent déclaratifs : la pertinence métier des preuves exige une relecture. Aucun build, environnement ou contrôle supplémentaire n’est attesté par ce rendu.
La transition du flow est enregistrée séparément par complete.
