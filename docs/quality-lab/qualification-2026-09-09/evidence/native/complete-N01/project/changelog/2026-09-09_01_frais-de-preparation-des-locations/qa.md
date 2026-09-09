# QA — release 2026-09-09_01

> ⚠️ **Le verdict du point 1 ci-dessous est PÉRIMÉ.** D-03 (09.09.2026) a remplacé D-02 dans cette
> même release : les montants qu'il atteste (52.0 à 4 jours, +12.0 sur la copie client) ne sont plus
> ceux que la release livre. Il est conservé intact comme historique, avec ses preuves ; **le verdict
> qui fait foi pour la release est celui du point 2**, plus bas. Ne pas le recopier dans le README de
> clôture ni dans la communication client.

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

---

## 2026-09-09 — Point 2 : frais de préparation révisés, 15 EUR à partir de 5 jours (D-03)

**Mode** QA de tâche, **niveau renforcé** — le champ `amount_total` est stocké, la reprise réécrit
des valeurs existantes, et pour la première fois **à la baisse**. Trois voies exécutées.

**Verdict : VALIDÉ.** Réception structurée des **14** critères de
`revue_fonctionnelle_point2.md` : rapport `../../.odoo-agents/flow-artifacts/frais-preparation-d03/qa_reception_point2.md`
(couverture `../../.odoo-agents/flow-artifacts/frais-preparation-d03/coverage.json`, contrat `e5f7e711`).

### Ce que ce point invalide

La QA du point 1 ne pouvait pas couvrir ce changement, et ce n'est pas une question de rejeu : ses
oracles eux-mêmes sont faux sous D-03 (elle atteste 52.0 pour une location de 4 jours, que D-03 fixe
à 40.0). Trois preuves du point 1 sont donc **périmées** et ne doivent plus être invoquées :
`copie_client_apres.txt`, `copie_client_postconditions.txt` et `coverage.json` du run
`frais-preparation`. Elles restent au dossier, non modifiées, comme trace de ce qui a été fait.

### Contrôles

| Contrôle | Commande | Résultat |
|---|---|---|
| Lint des fichiers touchés | `labctl lint lab_rental` | ✅ 0 erreur, 0 avertissement, 0 info |
| Installation base neuve + tests ciblés | `labctl qa lab_rental --quick --fresh --tags /lab_rental:TestPreparationFee` | ✅ `install=ok` · **12/12 tests** · ⏱ 23s |
| Mise à jour base existante + tests ciblés | `labctl qa lab_rental --quick --update --tags …` | ✅ `update=ok` · **12/12 tests** · ⏱ 8s |
| Logs | analyse `labctl qa` | ✅ 0 ERROR/CRITICAL, 0 test ignoré, 0 WARNING lié au module |
| Copie client `lab_client` — état de départ | `labctl shell etat_point2_avant.py` | ✅ module en 19.0.1.1.0, montants D-02 (52.0 / 152.0 / 12.0) |
| Mise à niveau de la copie client | `labctl update` | ✅ `Running upgrade [19.0.1.2.0>] post-migrate`, 0 ERROR |
| Copie client — état d'arrivée | `labctl shell etat_point2_apres.py` | ✅ 4 j : 52.0 → **40.0** (baisse) · 7 j : 152.0 → **155.0** · 5 j tarif nul : 12.0 → **15.0** · 3 j et les 2 prêts inchangés |
| Idempotence de la reprise | 2ᵉ `labctl update` **et** rappel du corps de la reprise | ✅ `STABLE_APRES_2E_UPDATE True []` et `REPRISE_REJOUEE_SANS_ECART True {}` |
| Non-régression du périmètre en base | postconditions sur `lab_client` | ✅ 0 vue, 0 action, 0 menu, 0 règle, accès inchangé, 7 champs, dépendance `base` seule |
| Contrôle XML-RPC réel | `labctl rpc` sur `lab.rental` | ✅ 4 j → **40.0**, 5 j → **65.0**, prêt 5 j → **50.0** ; enregistrements de test supprimés, copie rendue propre |

### Critères d'acceptation

**14/14 couverts.** Le détail critère par critère, avec chemins et empreintes SHA-256, est dans
`qa_reception_point2.md` et `coverage.json`. Les deux critères de reprise de données (C12, C13) sont
couverts par les mesures sur `lab_client`, pas par les tests unitaires : ceux-ci tournent sur base
neuve et ne prouvent rien sur les données déjà écrites.

### Réserve consignée sur l'idempotence

Le second `labctl update` **ne rejoue pas** le script de reprise : la version installée est déjà
19.0.1.2.0. Il prouve donc l'absence de dérive d'une mise à niveau ordinaire, pas l'idempotence de la
reprise. Celle-ci a été mesurée séparément, en rappelant le corps du script sur la copie
(`copie_client_idempotence.txt`) : aucun écart. C'est cette seconde mesure qui couvre C13.

### Ce que cette QA ne prouve pas

- Ni rendu visuel ni droits d'un autre utilisateur (limite déclarée du passage RPC) — sans objet, le
  module n'a ni vue ni groupe, mais c'est à la recette de clôture de le constater.
- La suite complète du module, la désinstallation et les tours : ils relèvent de `/odoo-close`.
- Le sort d'un client réel encore en 19.0.1.0.0 : il traverserait les deux reprises (19.0.1.1.0 puis
  19.0.1.2.0), toutes deux de purs recalculs. Chemin non exécuté ici, à jouer à la clôture.

### Dette antérieure, non introduite par ce diff

- 9 `no-space-after-block-comment` en voie « conseils » non bloquante (séparateurs `#=== … ===#`).
- `'author': 'Camptocamp'` au manifest, toujours **à confirmer** par l'humain à la clôture.
