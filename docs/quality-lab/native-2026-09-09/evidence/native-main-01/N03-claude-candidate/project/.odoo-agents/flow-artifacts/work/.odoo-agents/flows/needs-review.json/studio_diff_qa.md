# Fragment QA — diff du pack Studio

```
Comparaison de /work/changelog/2026-09-09_01_indicateur-de-revue-requise-sur-les-dema/studio/pack.json avec http://127.0.0.1:50691 / lab_client (aucune écriture) :
0 / 0 / 1 à créer / à modifier / inchangés sur http://127.0.0.1:50691 / lab_client
```

**Aucun écart** entre le pack versionné et la copie `lab_client` : 0 à créer,
0 à modifier, 1 inchangé. Aucune référence `unresolved` dans le pack
(`model_id` pointe sur `studio_customization.lab_seed_model`).

Contrôle de forme des scripts livrés (pas de module, donc pas de
`odoo-lint.sh --changed` : le lint de module ne s'applique pas ici) :
- `build_1_needs_review.py` : compilation OK
- `reprise_avant_1_needs_review.py` : compilation OK
- `rpc_common.py` : compilation OK
- `test_1_needs_review.py` : compilation OK
- `test_1_needs_review_orm.py` : compilation OK
