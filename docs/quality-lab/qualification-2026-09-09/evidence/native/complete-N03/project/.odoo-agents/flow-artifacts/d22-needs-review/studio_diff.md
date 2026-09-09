# Fragment QA — voie diff Studio (point 1)

Rôle : odoo-tester, mode `graph-lane-studio-diff`. Lecture seule sur `lab_client`.

| Contrôle | Commande | Résultat |
|---|---|---|
| Pack vs copie | `odoo_pack.py diff pack.json --db lab_client` | **0 à créer / 0 à modifier / 1 inchangé** — aucun écart |
| Références non résolues | inspection de `pack.json` | **0 `unresolved`** — la seule référence, `model_id`, pointe `{"ref": "studio_customization.lab_seed_model"}` |
| Contenu du pack | inspection | 1 enregistrement, `ir.model.fields`, aucun identifiant numérique |
| Périmètre du pack | `created.txt` | 1 ligne, 1 XML-ID — la release ne livre que ce champ, distinct du Studio historique `lab_seed_*` |
| Idempotence (C11) | `test_point1_idempotence.py` | **VERT** : 2 × (build + apply) ; champs du modèle 10 → 10, champs `needs_review` 1 → 1, XML-ID `studio_customization` 5 → 5, valeurs de sélection 2 → 2 ; `created.txt` sans doublon |
| Écart après idempotence (C12) | `odoo_pack.py diff` final | **0 / 0 / 1** |

Preuves : `studio/preuves/pack_diff.log`, `studio/preuves/test_point1_idempotence.log`

**Verdict de la voie : VERT.**
