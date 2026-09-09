# QA copie synthétique — VALIDÉ
Autorisation explicite de la demande et LAB.md ; seule copie lab_client, aucune production.
Preuves de la release :
- `update-copie.log` : mise à niveau réelle du module installé, registre chargé sans erreur (environ 3 s).
- `reprise-1.log` : brouillon 1, 999 → 20 ; une écriture snapshot_total uniquement ; commit.
- `reprise-2.log` : même script dans un nouveau shell, zéro écriture ; mêmes valeurs et write_date ; commit.
- `relecture-apres-commit.log` : troisième shell indépendant en lecture seule.
- `idempotence.txt` : vérificateur exécuté, identité des états, lignes, total et date du validé avant/après confirmée. Validé 2 : 777 inchangé.
Script borné par assertion de base, domaine de brouillons, interception des écritures et contrôles avant commit. Critères 5–6 couverts. Données synthétiques existantes conservées, seul total erroné repris.
