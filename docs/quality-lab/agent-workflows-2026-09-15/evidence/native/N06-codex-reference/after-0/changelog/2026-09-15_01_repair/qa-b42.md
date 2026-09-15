# QA — VALIDÉ

Issue proposée pour la réception : `pass`.
Couverture déclarée : 7/7 critères couverts.

Source du contrat :
> changelog/2026\-09\-15\_01\_repair/revue\_fonctionnelle\.md

SHA-256 de la source : `937da0c169766fe9d670e11fbe711d49bc9b25964f07f79b99e2be5d1304d6b6`.
SHA-256 du contrat : `56ac90ce7e3ddf9ab2d57dbedd719a2e5655ce9bbe55c5f4aa5accd385d06822`.

## Critères et références

> \*\*A1\*\* — Sous utilisateur interne multi\-société, une sélection mixte ne répare que les draft de self dans env\.company ; un brouillon non sélectionné et les autres sociétés restent strictement inchangés, même si accessibles\. Changer de société active inverse le périmètre ; sélection vide sans effet\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/green\.log

SHA-256 : `84c3a2079cf72687fd1a50a079aa68f05a40257a0b2eddab6b4f3c534d5aa378`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/qa\-runtime\.md

SHA-256 : `5f33f455a2c9d58169a35eaa8f028a2c66d7e95e46b266284f37c124b5c4d7e2`.

Fichier référencé :
> lab\_register/tests/test\_repair\.py

SHA-256 : `0cb156820a97bbcb34cf42059efd3627bdfbc627fd8884c2822541892cd003bb`.

> \*\*A2\*\* — Tri date\_document puis id, séquences 100/200 et suivantes ; snapshot\_total exclut les lignes annulées, vaut zéro sans ligne active, et conserve la précision non arrondie\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/green\.log

SHA-256 : `84c3a2079cf72687fd1a50a079aa68f05a40257a0b2eddab6b4f3c534d5aa378`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/qa\-runtime\.md

SHA-256 : `5f33f455a2c9d58169a35eaa8f028a2c66d7e95e46b266284f37c124b5c4d7e2`.

Fichier référencé :
> lab\_register/tests/test\_repair\.py

SHA-256 : `0cb156820a97bbcb34cf42059efd3627bdfbc627fd8884c2822541892cd003bb`.

> \*\*A3\*\* — Les issued sélectionnés conservent strictement state, sequence, snapshot\_total, reference ; aucune ligne ni champ hors correction ne change\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/green\.log

SHA-256 : `84c3a2079cf72687fd1a50a079aa68f05a40257a0b2eddab6b4f3c534d5aa378`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/repair\-first\.log

SHA-256 : `2f3f56c68bc6dfa357c86da5a47963afcf7ad24ed3b859407222b7613f2c72f9`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/qa\-copy\.md

SHA-256 : `1368f8689e6bf4ca33ed0959fd8f456a95f89b858edf51ce591bfaa77e69f16e`.

> \*\*A4\*\* — ACL/règles inchangées ; utilisateur ordinaire non sudo autorisé testé, utilisateur limité refusé sur une société interdite, absence de droit d'écriture refusée sans mutation\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/green\.log

SHA-256 : `84c3a2079cf72687fd1a50a079aa68f05a40257a0b2eddab6b4f3c534d5aa378`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/repair\-first\.log

SHA-256 : `2f3f56c68bc6dfa357c86da5a47963afcf7ad24ed3b859407222b7613f2c72f9`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/code\.diff

SHA-256 : `0dfd3b88ef0f370d850fa274d8b5ef1fea765d5f3b7665b539c7bbf84b354b5b`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/qa\-static\.md

SHA-256 : `6f55eb397e52b8079f37397ba4a470ed6a0149a0e7cf2bbce87e97d0cba09647`.

> \*\*A5\*\* — Test de régression rouge conservé sur le code initial puis mêmes tests verts sur code corrigé ; lint du diff, installation QA et update sur copie déjà installée exécutés\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/red\.log

SHA-256 : `f090bf1e4636364caa4c0e986d82ee4ac33b585f1eb27c3f7a6ce52b4d9c68df`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/business\-before\.py

SHA-256 : `b24cfe215ce52d95a64fe963125bba0b883ef185f8062c58bf918ba72193bd02`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/green\.log

SHA-256 : `84c3a2079cf72687fd1a50a079aa68f05a40257a0b2eddab6b4f3c534d5aa378`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/lint\.log

SHA-256 : `8cb67d1ddcc9bedad0692ce7af6610fb678e8d66642bffc9fdfd111f8d7264e2`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/lint\-diff\.log

SHA-256 : `67318e71032ad04cbc232dbad3b5057373d28474640dc71cdf172d65597d7689`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/manifest\-before\.txt

SHA-256 : `bb42b811dc5a4ec413ac69ac76db21ffc1305b264fabf3d9c7de9acaf7a0a2af`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/update\.log

SHA-256 : `9f5b3cf21d5f78be16ef61a516247e98d10c47ff649b1b46e88da127ce06bd8c`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/qa\-static\.md

SHA-256 : `6f55eb397e52b8079f37397ba4a470ed6a0149a0e7cf2bbce87e97d0cba09647`.

> \*\*A6\*\* — Reprise persistée uniquement des brouillons historiques 1 et 2 : 100/20 et 200/15 ; émis 3 et société 2 ID 4 intacts\. Deuxième passage idempotent, valeurs et write\_date stables, aucune écriture ORM au rejeu dans le test instrumenté\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/repair\-first\.log

SHA-256 : `2f3f56c68bc6dfa357c86da5a47963afcf7ad24ed3b859407222b7613f2c72f9`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/repair\-second\.log

SHA-256 : `e4d1b441b52d828713ddf148cb5a4c57ef5002afdc1c0e659f0b2614f4f5e23d`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/replay\-comparison\.json

SHA-256 : `99d1ad8757ea4965583ce4dcf3826f2c531fe797d0a00de60fb4145d1ad9a87f`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/repair\_local\.py

SHA-256 : `95c83cd6306ab150477bfc0488a142ebfd5193f8eeb7257e440b6be8ac681d97`.

> \*\*A7\*\* — Ancienne QA relue avec portée invalidée pour cette tâche ; revue, QA courante et journal publiés, release laissée ouverte, limites explicites\.

Statut déclaré : `covered`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/qa\.md

SHA-256 : `afad9695a82e13fdd57700911056f27cdc536bd6bb63cc3e3c3817c4d3f374c0`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/revue\_fonctionnelle\.md

SHA-256 : `937da0c169766fe9d670e11fbe711d49bc9b25964f07f79b99e2be5d1304d6b6`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/publication\.json

SHA-256 : `17d6ef6fc88822cdb747eecf0543634b7987afc6250db4e7dc0bb875bb8c81ff`.

Fichier référencé :
> changelog/2026\-09\-15\_01\_repair/proofs/reception\.md

SHA-256 : `fdea49c4646436baf8822ebcfcf7a1f72dd35afa580559584b31f76f17f45578`.

Fichier référencé :
> \.odoo\-agents/JOURNAL\.md

SHA-256 : `8ca3c1aef13846fbbd7acc3ca1daa1825d7e6a26dd669d386b6d459f78dbaa62`.

## Portée

Ce rapport vérifie le contrat, les statuts et les références. Les statuts restent déclaratifs : la pertinence métier des preuves exige une relecture. Aucun build, environnement ou contrôle supplémentaire n’est attesté par ce rendu.
La transition du flow est enregistrée séparément par complete.
