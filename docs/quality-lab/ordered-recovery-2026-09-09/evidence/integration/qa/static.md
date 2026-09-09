# QA statique indépendante — 2026-09-09

**Module** `lab_qualification` · **série** 19.0 (origine : manifest, briefing-current.md fourni) · **mode** QA de tâche renforcée, voie statique.

**VALIDÉ pour cette voie.** Aucun défaut introduit identifié. Pas de correction du module.

La demande originale `run/project/changelog/2026-09-09_01_quantite-positive-a-la-confirmation/demande.md:8` impose zéro en brouillon et positivité à la confirmation ; lignes 10–14, tous les canaux et l'atomicité ; lignes 16–21, droits et données préservés. Revue, consolidation et les 12 critères lus avant le code. Le contrat est toujours celui lié : `c078392df6bee103253131cca51353e8516301a476efd75637a67ee54c9de1f2` ; source `ad64b892e52786539fbf08b9a4d70559e3125c424198e4b907cd10b35564c712`.

## Contrôles et preuves

| Contrôle | Résultat | Preuve |
|---|---|---|
| Diff humain depuis HEAD | 4 fichiers touchés, conforme au delta demandé | `reviewed-module-diff.log`, égalité byte à byte avec `../developer/module.diff` |
| Lint changé | Réutilisation du lint développeur, 19.0, 0 erreur / 0 avertissement, 4 fichiers | `../developer/lint.log:1`, `:15` ; aucune nouvelle exécution de lint |
| Fraîcheur | Tous les fichiers actuels égaux au snapshot vert, aucun fichier supplémentaire | `verification.json`, `verified_live_module_sha256`, contrôles au début et à la fin |
| Attentes rouge/vert | Tous les tests sont strictement identiques entre les deux passages | `verification.json`, archives `../developer/red/tests/` et `../developer/green/module/tests/` |
| Contrat | Source et structure du contrat vérifiées avec `odoo_coverage.contract` | `verification.json`, contrôle `contract unchanged from bound criteria` |

`models.py:8` conserve la non-négativité ; `models.py:9` ajoute `CHECK(state != 'confirmed' OR quantity > 0)` et un message explicite. Le bouton `models.py:28` conserve une écriture unique du recordset ; pas de boucle d'écritures, pas de sudo, pas de transformation historique. Le calcul `models.py:22` conserve les dépendances quantity/unit_price et l'affectation quantity × unit_price. L'invariant SQL porte donc tous les canaux ORM et non uniquement le bouton.

Précédent réellement relu : `/home/blegoff/odoo-sources/19.0/addons/stock/models/stock_storage_category.py:64` utilise `models.Constraint('CHECK(quantity > 0)', ...)`. Aucun écart de série. Manifest : dépendance web, sécurité avant vue, fichiers existants, aucune nouvelle dépendance. La version reste 19.0.1.0.0 pendant cette release ouverte ; le schéma effectif, pas cette version identique, atteste l'update.

ACL, vue, manifest, point d'entrée, anciens tests ORM et navigateur inchangés par hashes du bootstrap, archive initiale, snapshot vert et fichiers actuels. Les droits CRUD internes préexistants restent expressément demandés ; aucun groupe, ACL, règle, modèle ou champ nouveau. Pas de société dans ce modèle, donc aucune règle multi-société nouvellement requise. Aucun élargissement public/portail livré.

`tests/__init__.py:3` importe les nouveaux tests ; `tests/common.py:12` emploie `with_user`, non sudo ; assertions UID/su/groupe dans `tests/test_confirmation.py:27`, assertions explicites de conservation après savepoint et invalidation dans le helper `tests/common.py:14`. Les assertions proviennent des valeurs du contrat (0, 1, 3 ; montants 0, 10, 30).

Deux conseils non bloquants du lint : tri des imports de l'init et virgule de la sélection (préexistante). Le lint n'annonce aucune anomalie Odoo antérieure. Pas de finding bloquant, majeur ou mineur à imposer.

AC01–AC08 sont étayés statiquement mais requièrent les logs de `runtime.md` ; AC09 est également couvert par les hashes et la fixture non su ; AC11 par absence de reprise dans le diff ; AC12 par le lint et la fraîcheur des archives.
