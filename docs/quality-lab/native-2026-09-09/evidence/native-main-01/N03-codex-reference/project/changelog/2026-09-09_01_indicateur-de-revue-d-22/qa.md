## 2026-09-09 — D-22 — QA de tâche Studio

**Série** 19.0 (LAB.md et RPC ; briefing initial par défaut) · **modèle** `x_lab_request` · **module custom** aucun · **copie** `lab_client`.

**VALIDÉ** — ajout du seul indicateur, six critères couverts, deux applications réelles du pack sans doublon. Release ouverte.

| Contrôle | Résultat | Preuve dans `studio/proofs/` |
|---|---|---|
| Avant configuration | Rouge attendu : champ absent | `red-before.log` |
| Après construction | 33/33 contrôles RPC | `green-build.json` |
| Relecture du pack | Un champ, modèle existant référencé, zéro unresolved | `../pack.json` |
| Diff initial | 0 création / 0 modification / 1 inchangé | `diff-initial.log` |
| Préparation de première application | Suppression du seul indicateur livré ; modèle vide | `reset-local.json` |
| Application 1 depuis champ absent | 1 créé / 0 modifié / 0 inchangé | `apply1.log` |
| Application 2 | 0 créé / 0 modifié / 1 inchangé ; identifiants stables | `apply2.log`, `pack-qa.json` |
| Diff après chaque application | Aucun écart | `diff-after-apply1.log`, `diff-after-apply2.log` |
| Scénarios après chaque application | 33/33, deux fois | `scenarios-apply1.json`, `scenarios-apply2.json` |
| Constructeur rejoué | Inchangé, mêmes identifiants | `build-idempotence.log` |
| Nettoyage et invariants | 0 ligne métier, 0 ACL ajoutée, 4 XML-ID initiaux + 1 nouveau | `pack-qa.json`, `invariants-before.json` |

### Couverture des critères

| Critère | Couverture | État |
|---|---|---|
| C1 : seul booléen stocké, dépendances, champs initiaux | Métadonnées RPC, comparaison à l'inventaire initial, un seul élément dans le pack | OK |
| C2 : seuil 7 inclus, prêts exclus, valeurs manquantes | 14 cas de création, dont 5/6/7/8 jours × location/prêt/type vide | OK |
| C3 : recalcul et stockage | 8 transitions, 8 vérifications en lot, original/copie, filtre serveur | OK |
| C4 : rouge/vert et nettoyage | Assertion avant construction, relectures après transactions RPC, `finally` pour données et ACL | OK |
| C5 : pack et idempotence | Vrai export/diff/apply, création depuis absence puis application inchangée ; même champ et XML-ID | OK |
| C6 : périmètre et livraison | Vues/règles/actions/ACL identiques, champs initiaux et modèle conservés ; suivi, QA et journal ; release ouverte | OK |

### Rejouer sur ce laboratoire

Depuis `studio/` :

```bash
python3 test_d22.py
python3 verify_pack.py
```

`verify_pack.py` rejoue deux applications et les scénarios sur l'état courant. L'exécution initiale prouvée a utilisé `--from-absent`, qui supprime exclusivement le champ de ce pack, après vérification du modèle vide et de son identité, avant de le recréer. Cette option et les scripts sont réservés à la copie synthétique décrite par `/work/LAB.md`.

Reconstruction/export :

```bash
python3 build_d22.py
python3 ~/.odoo19-agents/scripts/odoo_pack.py export --db lab_client --url http://127.0.0.1:43303 --only created.txt --out pack.json
python3 ~/.odoo19-agents/scripts/odoo_pack.py diff pack.json --db lab_client --url http://127.0.0.1:43303
```

### Constats résolus et limites

- Aucun bloquant ni anomalie métier restante.
- Le modèle initial n'a aucune ACL : fixture temporaire limitée au groupe administrateur, créée via RPC en contexte Studio et retirée après chaque scénario. Aucun droit livré. Un accès utilisateur métier n'est pas testé, car aucun accès permanent n'est demandé.
- Cache du banc : le refus de création persistait malgré une ACL correcte et l'appartenance effective à `base.group_system`. Les sources 19.0 `ir_model.py` montrent une invalidation `stable`, alors que `_get_allowed_models` utilise le cache par défaut. Le pont invalide et signale tous les caches avant/après la fixture, sans modification de données. Logs réels : `cache-refresh.log`.
- XML-ID natif : création marquée Studio mais `noupdate=False` observé. Protection par `write` en contexte Studio, conformément à `web_studio/models/ir_model_data.py` ; aucun identifiant créé ou renommé à la main.
- Pas de lint/install/update de module : non applicable en voie Studio. Pas de capture/tour navigateur : aucune vue modifiée. Aucun déploiement ni recette de clôture exécuté.
- Sources 19.1 absentes dans le banc : comparaison de série suivante non effectuée ; tests exécutés en 19.0 uniquement.

### Appris

D-22 est l'unique règle actuelle. Réutiliser les XML-ID `studio_customization.lab_seed_*`. Sur ce banc, les scénarios RPC nécessitent une ACL temporaire nettoyée et une invalidation complète des caches d'accès. Candidats au retour d'expérience du dispositif : nuancer `noupdate` à la création native Studio et vérifier la portée de l'invalidation des caches selon la révision 19.0.
