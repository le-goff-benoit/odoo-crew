# QA de la release

## 2026-09-09 — Point 1 · [studio] Indicateur `x_studio_needs_review` sur `x_lab_request`

**Verdict : VALIDÉ** (QA de tâche · voie Studio · copie synthétique locale `lab_client`, 19.0).
Rapport de réception généré depuis la couverture : `changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast/qa_rapport_point1.md`
(10/10 critères `covered`, issue `pass`). Couverture :
`.odoo-agents/flow-artifacts/lab-needs-review/coverage.json`.

### Contrôles

| Contrôle | Résultat |
|---|---|
| `odoo_pack.py diff pack.json` sur la copie | **0 à créer / 0 à modifier / 1 inchangé** |
| Pack sans référence `unresolved` | **0** ; `model_id` → `studio_customization.lab_seed_model` |
| Deux applications du script de construction | **CRÉÉ** puis **INCHANGÉ** — 1 champ, 1 XML-ID, aucun doublon |
| Scénarios RPC (`test_01_needs_review.py`), rejoués par le testeur | **9/9 vert**, sortie 0 |
| Scénario discriminant (rouge avant / vert après) | ROUGE 0/1 avant, VERT 9/9 après |
| Champs existants `x_name`, `x_studio_days`, `x_studio_kind` | ids et XML-ID `lab_seed_*` inchangés |
| Données de recette | 0 résidu (`x_lab_request` vide après passage) |
| Écran | **sans objet** — `ir.ui.view` sur le modèle = 0 avant et après |
| Lint Ruff / `odoo-lint.sh --changed` | **non exécuté** — aucun module custom ; substitut `py_compile` OK (voir ci-dessous) |
| `odoo-test.sh` install/update/tests | **sans objet** pour un point `[studio]` |

### Critères d'acceptation

| Critère | Couvert par | État |
|---|---|---|
| C1 définition du champ | relevé serveur + cas C1 du scénario | ✅ |
| C2 location 7 j → True (seuil inclus) | scénario, cas C2 | ✅ |
| C3 location 6 j → False, 30 j → True | scénario, cas C3 | ✅ |
| C4 prêt exclu à 7 j et 30 j | scénario, cas C4 | ✅ |
| C5 genre vide, durée 0 ou négative → False | scénario, cas C5 | ✅ |
| C6 recalcul sur modification des deux champs | scénario, cas C6 | ✅ |
| C7 champs existants intacts, aucun doublon | relevé `ir.model.fields` / `ir.model.data` + cas C7 | ✅ |
| C8 idempotence, un champ et un XML-ID | deux applications + relevé final | ✅ |
| C9 pack exporté, diff sans écart, sans `unresolved` | export + diff + pack | ✅ |
| C10 XML-ID relevé dans `created.txt`, marqué Studio | `created.txt` + relevé | ✅ |

### Réserves — ce qui n'a pas été contrôlé

1. **Pas de lint Ruff.** Le point ne livre aucun module Python ; le lint du banc n'accepte
   qu'un module et Ruff n'est pas installé hors image QA. Seul `python3 -m py_compile` a
   été passé sur les deux scripts de la release (OK). Ce n'est pas un lint : je le dis
   plutôt que de le maquiller.
2. **Rien n'est déployé.** Aucune application en staging ni en production ; c'est le
   périmètre demandé. Le pack reste à `diff` puis `apply` sous décision humaine.
3. **RPC ne prouve ni l'écran ni les droits d'un autre utilisateur.** Sans objet ici
   (0 vue, aucun droit touché), mais à retenir si une tâche ultérieure expose le champ.
4. **Dette antérieure** : aucune relevée sur ce périmètre.

Aucun défaut introduit, aucun critère non satisfait. **Réception : pass.**
