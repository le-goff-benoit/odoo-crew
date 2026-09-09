# Preuve — studio_implementation (point 1)

Base : `lab_client` (copie synthétique locale), XML-RPC `http://127.0.0.1:48687`, admin.

## Livré
| Objet | Valeur |
|---|---|
| Champ | `x_lab_request.x_studio_needs_review` — booléen, `manual`, `store=True`, `readonly=True` |
| `depends` | `x_studio_days,x_studio_kind` |
| `compute` | boucle `for record in self:` + affectation par clé (safe_eval, mode exec) |
| XML-ID | `studio_customization.revue_requise_demand_07727582-796e-43d5-a494-4c149b785c9b` (créé par Odoo en contexte `studio=True`, non fabriqué à la main) |
| Créé par | `studio/build_point1.py` (idempotent, clé naturelle modèle + nom) |

Champs existants réutilisés tels quels : `x_name`, `x_studio_days`, `x_studio_kind` — non renommés, non recréés, XML-ID `lab_seed_*` intacts.
Rien d'autre créé : 0 ACL, 0 `ir.rule`, 0 vue, 0 automatisation, 0 action serveur.

## Rouge avant / vert après
| Scénario | Avant construction | Après construction |
|---|---|---|
| `test_point1_rpc.py` | ROUGE (V1 : champ absent) | VERT (18/18) |
| `test_point1_orm.py` | ROUGE (précondition : champ absent du registre) | VERT (12/12) |

## Pack
`studio/pack.json` — 1 enregistrement, `model_id` résolu en `{"ref": "studio_customization.lab_seed_model"}`, **aucune référence `unresolved`**.

## Limite rencontrée et non contournée
`x_lab_request` n'a **aucun** `ir.model.access` en base. Tout `create`/`read` d'un enregistrement est refusé en XML-RPC, y compris à `admin` (`ir_model.py:33`). D-22 et la demande interdisent tout changement de droits : **aucune ACL n'a été créée**. Le comportement est donc prouvé par l'ORM (`/bridge/labctl shell`, superuser, valeurs relues en SQL après flush) et la limite elle-même est prouvée par le scénario RPC (V6), pas supposée.

Preuves : `studio/preuves/*.log`
