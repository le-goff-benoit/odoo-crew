# QA scénarios Studio — PASS

Commande réelle : `python3 changelog/2026-09-09_01_indicateur-de-revue-d-22/studio/verify_pack.py --from-absent`.
Résultat : code 0 ; preuves dans `studio/proofs/` de la release.
- Pack appliqué depuis l'indicateur absent : 1 créé / 0 modifié / 0 inchangé.
- Seconde application : 0 créé / 0 modifié / 1 inchangé ; même ID de champ et même XML-ID.
- Diff après chaque application : 0 / 0 / 1.
- 33 contrôles RPC verts après chacune des applications ; constructucteur rejoué sans changement.
- Modèle et champs initiaux comparés à l'inventaire d'origine ; invariants de vues, règles, actions et ACL identiques ; 5 XML-ID Studio finaux (4 initiaux + 1 livré).
- Aucun enregistrement métier final ni ACL de recette ; accès create à nouveau refusé comme à l'origine.
- Aucun écran modifié : contrôle navigateur non applicable.
Critères C1 à C6 techniques couverts ; reste consolidation QA, suivi, journal.
