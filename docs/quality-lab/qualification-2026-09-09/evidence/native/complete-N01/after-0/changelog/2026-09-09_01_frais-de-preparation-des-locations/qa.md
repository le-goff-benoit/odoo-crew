# QA — release 2026-09-09_01

## 2026-09-09 — Point 1 : frais de préparation 12 EUR sur les locations de 4 jours et plus (D-02)

**Mode** QA de tâche, **niveau renforcé** (le champ `amount_total` est stocké : la mise à niveau
réécrit des valeurs d'enregistrements existants). Trois voies exécutées.

**Verdict : VALIDÉ.** Réception structurée des 12 critères : `qa_rapport_tache1.md`
(couverture `../../.odoo-agents/flow-artifacts/frais-preparation/coverage.json`, contrat `ebe8ae3f`).

| Contrôle | Commande | Résultat |
|---|---|---|
| Lint des fichiers touchés | `labctl lint lab_rental` | ✅ 0 erreur, 0 avertissement |
| Installation base neuve + tests ciblés | `labctl qa lab_rental --quick --fresh --tags /lab_rental:TestPreparationFee` | ✅ `install=ok` · 10/10 tests · ⏱ 15s |
| Mise à jour base existante + tests ciblés | `labctl qa lab_rental --quick --update --tags …` | ✅ `update=ok` · 10/10 tests · ⏱ 4s |
| Logs | analyse `labctl qa` | ✅ 0 ERROR/CRITICAL, 0 test ignoré, 0 WARNING lié au module |
| Mise à niveau de la copie client `lab_client` | `labctl update` | ✅ `post-migrate 19.0.1.1.0` exécuté, 3 lignes sur 7 recalculées, +12.0 exactement |
| Idempotence de la reprise | 2ᵉ `labctl update` | ✅ aucun montant ne dérive |
| Non-régression du périmètre en base | postconditions sur `lab_client` | ✅ 0 vue, 0 action, 0 menu, 0 règle, accès inchangé, champs inchangés |
| Contrôle XML-RPC réel (création) | `labctl rpc` sur `lab.rental` | ✅ location de 4 jours créée → `amount_total = 52.0` |

Fragments détaillés : `../../.odoo-agents/flow-artifacts/frais-preparation/qa_high_static.md`,
`qa_high_runtime.md`, `qa_client_copy.md`.

### Ce que la QA a trouvé et qui a changé le code

**La mise à niveau seule ne corrigeait pas les données existantes.** Après `-u` avec le nouveau
calcul mais sans reprise, « Location 4 jours » restait à 40.0 sur `lab_client` : modifier le corps
d'un compute ne réécrit pas un champ stocké. La fonctionnalité aurait été verte en test et fausse
sur tout l'historique du client. Corrigé par `migrations/19.0.1.1.0/post-migrate.py`, ce qui a imposé
de monter la version du manifest **maintenant** au lieu de la clôture — le nom du dossier de
migration est la version cible. À reprendre à la clôture : ne pas remonter la version une seconde
fois si `19.0.1.1.0` reste la version livrée.

### Réserves et dette

| Point | Nature | Décision |
|---|---|---|
| `__manifest__.py` sans clé `author` | **dette antérieure**, bloquait le lint (WARNING présent dans tous les logs de démarrage avant la tâche) | corrigée en passant (`'author': 'Camptocamp'`), le diff touchait déjà le manifest. À confirmer : « Camptocamp » est-il le bon auteur pour ce projet ? |
| 9 × `no-space-after-block-comment` | conseil ruff non bloquant, imputable aux marqueurs `#=== SECTION ===#` du diff | conservés : c'est la forme d'Odoo lui-même (`addons/sale/models/sale_order.py:52`) et celle du référentiel |
| `amount_total` en `Float` et non `Monetary` | signalé en revue (risque n°3) | hors périmètre : D-02 fixe une monnaie unique EUR ; passer en `Monetary` imposerait un champ devise et un écran |
| Pas de contrainte de positivité sur `days` / `daily_rate` | signalé en revue (risque n°4) | hors périmètre : ce serait un changement d'écran de saisie, exclu par la demande |
| Aucune capture, aucun guide | conforme | interdits en QA de tâche ; la release reste ouverte, `/odoo-close` les produira |

### Ce qui n'est pas couvert à ce stade
Rendu visuel et comportement pour un utilisateur non-admin : non prouvés (le passage RPC ne les
couvre pas). Sans objet pour cette tâche — aucune vue ni aucun droit ne change, ce qui est vérifié
en base — mais c'est la recette navigateur de `/odoo-close` qui l'attestera pour la release.
