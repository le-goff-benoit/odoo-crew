# Odoo 19.0 — copie synthétique locale prête

Dossier définitif : `/tmp/odoo-ordered-recovery-20260909/integration`.
Projet : `run/project`. Briefing effectué par `prepare` du runner figé avant toute copie de code : `run/briefing.md` ; config : `run/project/.odoo-agents/config` (`ODOO_SERIES=19.0`).

Le module INITIAL `lab_qualification` 19.0.1.0.0 est installé. Aucun ajout de règle ni de test métier nouveau à cette étape. L'archive `evidence/initial-module.tar.gz` et les hashes dans `evidence/bootstrap-result.json` figent ce baseline.

`ordered_seed` contient exactement les IDs 1/2/3 : draft quantité 0 prix 10 montant 0 ; draft quantité 3 prix 10 montant 30 ; confirmed quantité 3 prix 10 montant 30. `ordered_copy` provient d'un vrai `pg_dump -Fc` / `pg_restore --exit-on-error`, avec conservation vérifiée des IDs et valeurs. Le dump et les inventaires ORM/SQL sont conservés dans `evidence/`. Ce sont exclusivement des données synthétiques, pas une restauration client.

Réseau interne : `ordered-recovery-d015b7aa5705`. PostgreSQL : `ordered-recovery-d015b7aa5705-pg`. Aucun port publié. Données PostgreSQL en tmpfs, Odoo éphémère nommé et étiqueté, module monté readonly. Les IDs d'images locales et tous les noms exacts sont dans `resources.json`. Aucun téléchargement d'image. Le seul mot de passe est la constante publique `synthetic-lab-only`.

Les quatre tests ORM initiaux ont été réellement exécutés : `evidence/test-ordered_copy-20260909-183809-32609ec5.tests.json`, résumé Odoo `0 failed, 0 error(s) of 4 tests`, quatre noms de tests démarrés et quatre marqueurs métier. Aucun test Chrome requis/exécuté pour cette commande backend.

## Commandes depuis tout répertoire

```bash
python3 /tmp/odoo-ordered-recovery-20260909/integration/runtime.py test --tags '/lab_qualification:TestQuantity,/lab_qualification:TestConfirmation'
python3 /tmp/odoo-ordered-recovery-20260909/integration/runtime.py update
python3 /tmp/odoo-ordered-recovery-20260909/integration/runtime.py inventory --db ordered_copy
python3 /tmp/odoo-ordered-recovery-20260909/integration/runtime.py inventory --db ordered_seed
python3 /tmp/odoo-ordered-recovery-20260909/integration/runtime.py shell --script /chemin/script.py
```

`--db` vaut `ordered_copy` par défaut et accepte seulement `ordered_seed` / `ordered_copy`. `run` installe le module ; `update` met à niveau ; `test` met à niveau et exécute les tags explicitement sélectionnés ; `shell` lit un fichier Python ou stdin. Les écritures shell nécessitent `env.cr.commit()` explicite. Préserver `ordered_seed` comme référence : toutes les prochaines écritures/update/tests sur `ordered_copy`.

Chaque commande archive arguments, code de sortie, durée et log sous un nom unique. `test` produit aussi `.tests.json`, exige un résumé Odoo non vide et des noms de tests réellement démarrés ; restitue un code non nul si échec ou absence de tests. Le testeur doit encore vérifier les noms/nombre/marqueurs attendus du nouveau contrat métier. Le runner historique `assess()` et ses attentes Chrome ne sont pas utilisés comme oracle.

Exécuter les appels de ce runtime séquentiellement : module, base et registre des ressources sont partagés entre développeur et QA dans ce seul banc.

Nettoyage final exclusivement ciblé sur les noms enregistrés et après contrôle du label propriétaire :

```bash
python3 /tmp/odoo-ordered-recovery-20260909/integration/runtime.py cleanup
```

Les ressources restent vivantes pour l'épreuve ; le cleanup final n'a pas encore été exécuté. Le bootstrap aurait nettoyé automatiquement en cas d'exception. La suppression de PostgreSQL efface le tmpfs ; le dump archivé reste disponible. L'orchestrateur conserve seul l'écriture de la release, du flow et du journal.
