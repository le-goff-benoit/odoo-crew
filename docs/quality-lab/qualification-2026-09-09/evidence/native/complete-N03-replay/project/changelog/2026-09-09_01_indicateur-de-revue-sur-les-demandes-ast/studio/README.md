# Point 1 — [studio] Indicateur de revue sur `x_lab_request`

Voie **Studio / configuration en base** (aucun module custom). Décision **D-22**
(`decisions/2026-09-08.md`) : revue requise si `x_studio_kind == 'rental'`
**ET** `x_studio_days >= 7` (seuil inclus) ; les prêts (`loan`) sont exclus.

## Livrables

| Fichier | Rôle |
|---|---|
| `build_01_needs_review.py` | construction idempotente en contexte `studio=True` (`--dry-run` disponible) |
| `test_01_needs_review.py` | scénario RPC rejouable — crée ses données « — recette », relit côté serveur, nettoie |
| `pack.json` | pack versionné, applicable par identifiant externe |
| `created.txt` | l'identifiant externe livré par CETTE release |
| `preuves/` | sorties réelles conservées (avant / applications / après / pack) |

## Ce qui a été créé

Un seul objet, sur le modèle existant `x_lab_request` :

- `x_studio_needs_review` — booléen, **stocké**, calculé, lecture seule, `state = manual`
- `depends = x_studio_days,x_studio_kind`
- code du calcul (safe_eval, mode exec, sur `self`) :

```python
for record in self:
    record['x_studio_needs_review'] = (record['x_studio_days'] or 0) >= 7 and record['x_studio_kind'] == 'rental'
```

XML-ID relevé (créé par Odoo lui-même, contexte `studio`) :
`studio_customization.revue_requise_demand_2e8e5590-3d9c-4448-bdda-83f7970c31eb`

Les champs `x_name`, `x_studio_days`, `x_studio_kind` sont **réutilisés tels quels** :
ni renommés, ni recréés, ni dupliqués. Leurs XML-ID `studio_customization.lab_seed_*`
sont inchangés (contrôlé par C7). `model_id` du pack pointe vers
`studio_customization.lab_seed_model` : le modèle existant, pas un nouveau.

## Rejouer

```bash
cd changelog/<release>/studio
python3 build_01_needs_review.py          # idempotent ; --dry-run pour voir sans écrire
python3 test_01_needs_review.py           # sortie 0 = tout vert
python3 ~/.odoo19-agents/scripts/odoo_pack.py diff pack.json \
    --url http://127.0.0.1:46503 --db lab_client --login admin --password admin
```

Cible par défaut : copie synthétique locale `lab_client`. Surcharge par
`ODOO_URL`, `ODOO_DB`, `ODOO_LOGIN`, `ODOO_PASSWORD`.

## Limites assumées

- Pas de test Python : la preuve est le scénario RPC (limite de la voie Studio).
- Le passage RPC ne prouve ni le rendu visuel ni les droits d'un autre utilisateur.
  Sans objet ici : aucune vue n'existe sur ce modèle, aucun droit n'est touché.
- **Aucun déploiement** : rien n'a été appliqué en staging ni en production.
  Le `pack.json` est prêt pour `odoo_pack.py diff` puis `apply`, sous décision humaine.
