# QA scénarios Studio — PASS
Odoo 19.0, copie synthétique lab_client, compte RPC du banc ; action temporaire avec sudo documenté car modèle sans ACL.
Commande : `python3 changelog/2026-09-09_01_indicateur-de-revue-d-22/studio/test_pack_d22.py --recreate-added-field` (exit 0).
- Champ du pack retiré seul pour rejouer une création réelle ; premier apply : 1 créé/0 modifié ; deuxième : 0 créé/0 modifié/1 inchangé.
- Diff nul après chaque application ; scénarios relus côté serveur : 9 créations, 6 transitions unitaires, 2 écritures en lot, 2 recherches sur champ stocké, nettoyage.
- Snapshots avant/après : identité stable après premier apply, pas de duplication ; autres champs, XML-ID historiques, vues, ACL, actions et automatisations conservés.
- 3 lignes créées champ absent : rental 7=True, loan 8=False, rental 6=False à la relecture après pack ; sources inchangées.
- Nettoyage final : zéro demande comme à l'origine, zéro action temporaire, quatre XML-ID initiaux inchangés et un seul nouveau XML-ID de champ.
Preuves : studio/proofs/{apply-1.log,apply-2.log,diff-1.log,diff-2.log,scenarios-1.log,scenarios-2.log,before-pack.json,after-pack.json,preexisting-result.json,cleanup.json}.
C1 à C6 couverts côté configuration locale. Aucun écran modifié, pas de capture requise. Accès métier non testé, aucune restauration/déploiement/recette de clôture.
