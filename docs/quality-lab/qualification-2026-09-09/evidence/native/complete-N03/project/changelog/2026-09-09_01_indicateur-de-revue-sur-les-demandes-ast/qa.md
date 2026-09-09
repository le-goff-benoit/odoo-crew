# QA de la release

## 2026-09-09 — Point 1 · [studio] Indicateur `x_studio_needs_review` (D-22)

**Verdict : VALIDÉ.** Voie Studio, QA de tâche niveau **normal**.
Rapport de réception structuré : `qa_point1.md` (13/13 critères `covered`, contrat `534358c6d6cb`).

### Contrôles
| Contrôle | Commande | Résultat |
|---|---|---|
| Lint | — | **non exécuté, sans objet** : la voie Studio ne produit aucun code de module. Le projet a 0 module, et `labctl lint` s'applique à un module. Substitut exécuté sur les 5 scripts livrés : `python3 -m py_compile` → OK. Ruff n'a **pas** tourné. |
| Installation / mise à jour | — | **sans objet** : aucun module à installer ou mettre à jour (voie Studio, cf. `roles/studio.md`). |
| Pack vs copie | `odoo_pack.py diff pack.json --db lab_client` | **0 à créer / 0 à modifier / 1 inchangé** |
| Références du pack | inspection `pack.json` | **0 `unresolved`** (`model_id` → `studio_customization.lab_seed_model`) |
| Deux applications sans doublon | `test_point1_idempotence.py` | **VERT** — 2 × (build + apply), tous les compteurs identiques |
| Scénario RPC (définition, non-régression, périmètre) | `test_point1_rpc.py` | **VERT 25/25** — rouge avant la construction |
| Scénario ORM (comportement D-22) | `test_point1_orm.py` via `labctl shell` | **VERT 12/12** — rouge avant la construction |
| Écran | — | **aucune capture** : 0 vue sur `x_lab_request` avant comme après, aucune vue créée. La revue §10 prévoyait « rien de visible ». |
| Propreté de la copie | — | données « — recette » supprimées, **0 enregistrement restant** |

### Critères d'acceptation
| Critère | Couvert par | État |
|---|---|---|
| C1 à C6 — table de vérité D-22 (7 inclus, `rental` seul) | `studio/preuves/test_point1_orm.log` | ✅ |
| C7, C8 — recalcul au changement de `x_studio_days` / `x_studio_kind`, dans les deux sens | `studio/preuves/test_point1_orm.log` | ✅ |
| C9 — définition du champ et XML-ID `studio_customization` | `studio/preuves/test_point1_rpc.log` (V2, V3) | ✅ |
| C10 — champs d'origine réutilisés, aucun doublon | `studio/preuves/test_point1_rpc.log` (V4) | ✅ |
| C11 — deux applications sans doublon | `studio/preuves/test_point1_idempotence.log` | ✅ |
| C12 — `diff` sans écart | `studio/preuves/pack_diff.log` | ✅ |
| C13 — aucun droit, vue, automatisation, action serveur ou cron créé | `studio/preuves/test_point1_rpc.log` (V5) | ✅ |

### Ce qui n'est pas couvert, et pourquoi
- **Le comportement n'est pas prouvé en XML-RPC.** `x_lab_request` n'a aucun `ir.model.access`
  en base ; tout `create`/`read` d'un enregistrement est refusé, y compris à `admin`
  (`odoo/addons/base/models/ir_model.py:33`). D-22 et la demande interdisant tout changement
  de droits, aucune ACL n'a été créée. C1–C8 sont donc prouvés par l'ORM (superuser, valeurs
  relues en SQL après flush) ; la limite elle-même est vérifiée par le scénario RPC (V6).
  **Conséquence pour l'humain : en l'état, aucun utilisateur ne peut voir ce champ.**
- **Rendu visuel et droits d'un autre utilisateur** : non couverts (aucune vue, aucun autre
  utilisateur que `admin` en base).
- **Recette complète, désinstallation, mise à niveau, captures, guide** : à la clôture
  (`/odoo-close`), pas à la tâche.
- **Déploiement** : aucun. Le pack n'a été appliqué que sur la copie locale `lab_client`.
  Ni staging ni production — hors périmètre demandé.

### Dette antérieure constatée (non introduite par la tâche)
`x_lab_request` était déjà sans ACL et sans vue avant la tâche. À arbitrer hors de ce point.
