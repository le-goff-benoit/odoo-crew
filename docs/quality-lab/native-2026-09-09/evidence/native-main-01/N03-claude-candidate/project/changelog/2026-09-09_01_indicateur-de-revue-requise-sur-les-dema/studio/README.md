# Point 1 — Indicateur `x_studio_needs_review` (D-22)

Configuration en base, **aucun module**. Livrable de référence : `pack.json`.

## Ce qui a été créé

| Objet | Identifiant externe |
|---|---|
| `ir.model.fields` `x_lab_request.x_studio_needs_review` (booléen, calculé, stocké) | `studio_customization.revue_requise_demand_924627ca-0724-4389-b944-ba45837bd3c3` |

Rien d'autre : aucun droit, aucune vue, aucune automatisation, aucun cron.
Les champs `x_name`, `x_studio_days`, `x_studio_kind` sont intacts
(`lab_seed_*` inchangés) ; ils sont seulement lus par le calcul.

## Règle appliquée (D-22, `decisions/2026-09-08.md`)

```python
for record in self:
    record['x_studio_needs_review'] = record['x_studio_kind'] == 'rental' and record['x_studio_days'] >= 7
```

Seuil 7 **inclus** ; les prêts (`loan`) sont exclus quelle que soit la durée.

## Fichiers

| Fichier | Rôle |
|---|---|
| `pack.json` | le livrable : applicable par identifiant externe, idempotent |
| `created.txt` | ce que cette release a livré, distinct du Studio historique |
| `build_1_needs_review.py` | construction en contexte `studio=True`, idempotente (XML-RPC) |
| `rpc_common.py` | connexion XML-RPC partagée |
| `test_1_needs_review.py` | scénario XML-RPC : la configuration livrée (C8, C10, C11, C12) |
| `test_1_needs_review_orm.py` | scénario ORM superutilisateur : table de vérité D-22 (C1–C9) |
| `reprise_avant_1_needs_review.py` | préalable de recette : enregistrements antérieurs, pour C9 |

Deux chemins mènent au même état — le script de construction et l'application
du pack. Les deux ont été joués, et le second a servi de recette (voir `../qa.md`).

## Pourquoi deux scénarios et pas un seul en RPC

`x_lab_request` n'a **aucun** `ir.model.access` : hors superutilisateur, aucun
accès aux enregistrements n'est possible
(`odoo/addons/base/models/ir_model.py:2134-2167`). D-22 interdit de toucher aux
droits ; corriger cela n'est pas dans le périmètre de cette tâche. La
configuration se prouve donc en XML-RPC, la table de vérité en ORM
superutilisateur. Le scénario RPC constate la limite au lieu de la supposer :
si une ACL est ajoutée un jour, il joue aussi la table de vérité, sans
modification.

## Déploiement

**Non fait, et hors périmètre de la demande.** Le pack est prêt :

```bash
python3 ~/.odoo19-agents/scripts/odoo_pack.py diff  pack.json --instance <projet> staging
python3 ~/.odoo19-agents/scripts/odoo_pack.py apply pack.json --instance <projet> staging
```

Toujours `diff` avant `apply`, staging avant production, scénarios rejoués après.
