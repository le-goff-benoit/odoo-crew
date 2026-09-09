# QA — 2026-09-09 — D-12 — tâche sensible

**Module** lab_dispatch · **Série** 19.0 (manifest) · **Voie** module_high_risk · **Copie** lab_client synthétique.

## Verdict
**VALIDÉ SOUS RÉSERVE DE DETTE ANTÉRIEURE** : les 7 critères métier sont satisfaits, les tests exécutés sont verts, l'update et la reprise persistée puis rejouée sont prouvés. Aucune anomalie introduite identifiée. Le lint global reste en échec sur une clé `author` absente du manifest initial non modifié ; ce défaut est reproduit sur la base git de la release, sans incidence sur les contrôles exécutés. Il ne faut donc pas présenter le lint complet comme vert.

## Contrôles exécutés
| Contrôle | Résultat | Preuve |
|---|---|---|
| Test rouge avant correction | 7 échecs, 0 erreur technique, 0 ignoré | [test-rouge.log](preuves/test-rouge.log), [empreinte initiale](preuves/test-rouge.json) |
| Défaut sur copie, puis rollback | 999/777 deviennent 110/110 ; restauration vérifiée | [defaut-copie.log](preuves/defaut-copie.log) |
| Ruff, fichiers touchés | Vert, 3 fichiers, aucun conseil | [lint-developer.log](preuves/lint-developer.log) |
| Lint Odoo | Code 1 : `author` absent ; même erreur sur la base 53e6624dcbef3d8d8a5029b689165244a79ddd0c | [lint-base.log](preuves/lint-base.log) |
| Compilation Python / diff whitespace | Vert | compileall sur module et reprise ; git diff --check |
| Ruff du script de reprise | Vert, env fourni par le shell déclaré comme builtin | [lint-reprise.log](preuves/lint-reprise.log) |
| Installation / update QA et tests | install=ok, update=ok, 7/7 verts, 0 ignoré, 4 s | [test-vert.log](preuves/test-vert.log), [empreinte finale](preuves/test-vert.json) |
| Update sur copie existante | Code 0, registre chargé | [update-copie.log](preuves/update-copie.log), [empreinte](preuves/update-copie.json) |
| Reprise 1 commitée | id 1 : 999 → 20 ; id 2 : 777 conservé | [reprise-1.log](preuves/reprise-1.log), [empreintes module et script](preuves/reprise-1.json) |
| Reprise 2, session distincte | Aucun changement, write_date compris | [reprise-2.log](preuves/reprise-2.log), [empreintes](preuves/reprise-2.json) |
| Relecture indépendante | Valeurs persistées conformes, états et 4 lignes inchangés | [lecture-finale.log](preuves/lecture-finale.log), [comparaison automatique](preuves/idempotence.log) |

## Critères d'acceptation
| Critère | Preuve | État |
|---|---|---|
| C1 — annulées exclues | test_draft_excludes_cancelled, test_active_amounts ; copie 20 | OK |
| C2 — validés figés sans écriture | test_validated_snapshot_unchanged, test_validated_never_written ; snapshot et write_date originaux sur copie | OK |
| C3 — sélection mixte sans erreur | test_mixed_selection_internal_user | OK |
| C4 — vide / tout annulé / recordset vide | test_empty_and_all_cancelled | OK |
| C5 — reprise limitée aux brouillons existants | reprise-1, comparaison avec inventaire initial | OK |
| C6 — idempotence persistée | test_recalculate_idempotent ; reprise-2 et lecture finale dans des sessions distinctes | OK |
| C7 — droits inchangés / utilisateur interne | CSV inchangé, test mixte avec env.su=False | OK |

## Relecture et limites
Le filtre draft est exécuté avant l'accès aux lignes : les validés ne sont pas recalculés. Aucun sudo, SQL, changement de droits ou d'état. La reprise explicite est protégée par le nom de base lab_client ; aucun hook automatique n'est livré. Le manifest conserve 19.0.1.0.0 jusqu'à clôture.
Les 7 tests ciblés constituent la suite entière du module. Pas de parcours navigateur, de tours, de désinstallation ou de livrable client : aucun écran modifié, recette de clôture non demandée. Sources de la série suivante absentes du laboratoire : comparaison non exécutée, sans effet sur cette validation 19.0.
Avertissements du pont : --without-demo all converti en booléen et http-interface implicite ; aucune erreur d'exécution. La dette `author` reste visible et n'a pas été corrigée hors périmètre.

## Commandes reproductibles
- Tests : `/bridge/labctl qa lab_dispatch --quick --tags /lab_dispatch:TestRecalculate`.
- Update copie : `/bridge/labctl update`.
- Reprise locale : `/bridge/labctl shell /work/changelog/2026-09-09_01_recalcul-fiable-des-brouillons/reprise/recalculate_drafts.py`.
- Comparaison des preuves : `python3 changelog/2026-09-09_01_recalcul-fiable-des-brouillons/preuves/verify_idempotence.py`.

Les fragments des trois voies sont dans `.odoo-agents/flow-artifacts/dispatch-d12/`. Le test rouge garde volontairement l'empreinte du code initial ; seuls les fichiers test-vert/update-copie/reprise-1/reprise-2 valident le code final.

## Appris
D-12 remplace D-11 : ne jamais réparer les validés en recalculant leurs lignes. Un update du module ne corrige pas les totaux stockés existants : la reprise locale explicite est nécessaire.
