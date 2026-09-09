# Fragment QA — voie « diff Studio » (point 1)

**Testeur** claude-odoo-tester-diff · **Base** copie synthétique locale `lab_client` (19.0) · **2026-09-09**

## Contrôles

| Contrôle | Commande | Résultat | Preuve |
|---|---|---|---|
| Le pack ne diverge pas de la copie | `odoo_pack.py diff pack.json --db lab_client` | **0 à créer / 0 à modifier / 1 inchangé** (sortie 0) | `changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast/studio/preuves/07_qa_pack_diff.txt` |
| Aucune référence `unresolved` dans le pack | `grep -c unresolved pack.json` | **0** ; `model_id` résolu en `studio_customization.lab_seed_model` | `changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast/studio/pack.json` |
| Un seul champ livré, un seul XML-ID | relevé `ir.model.fields` + `ir.model.data` | 1 champ `x_studio_needs_review` (id 3742), 1 XML-ID `studio_customization.revue_requise_demand_2e8e5590-…` | `changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast/studio/preuves/08_qa_etat_base.txt` |
| Idempotence de la construction | 2 exécutions successives de `build_01_needs_review.py` | 1ʳᵉ **CRÉÉ**, 2ᵈᵉ **INCHANGÉ**, même id, même XML-ID → aucun doublon | `preuves/02_build_application_1.txt`, `preuves/03_build_application_2.txt` |
| Champs existants intacts | relevé `ir.model.fields` / `ir.model.data` | `x_name` (3734), `x_studio_days` (3736), `x_studio_kind` (3738) inchangés, XML-ID `lab_seed_*` conservés, aucun doublon | `preuves/08_qa_etat_base.txt` |
| Définition conforme à la spec | relevé du champ | booléen, `store=true`, `readonly=true`, `state=manual`, `depends=x_studio_days,x_studio_kind` | `preuves/08_qa_etat_base.txt` |
| Marquage Studio | contexte `{"studio": True}` sur `create` | XML-ID généré par Odoo sous `studio_customization`, forme `<libellé>_<uuid>` — indiscernable d'un travail fait dans Studio | `preuves/02_build_application_1.txt` |

## Contrôles non applicables ou non exécutés

- **Lint Ruff / `odoo-lint.sh --changed`** : *non exécuté*. Aucun module custom n'est
  livré ; le lint du banc (`labctl lint MODULE`) n'accepte qu'un module et Ruff n'est
  pas installé hors image QA. Substitut exécuté : `python3 -m py_compile` sur les deux
  scripts de la release → **OK**. À dire tel quel, ce n'est pas un lint.
- **`odoo-test.sh` / install-update** : sans objet pour un point `[studio]` (aucun module).
- **Capture d'écran** : sans objet, `ir.ui.view` sur `x_lab_request` = **0** avant comme
  après ; aucune vue créée ni modifiée.

## Verdict de la voie

**VERT** — le pack fait foi, la copie lui est conforme, la construction est idempotente
et n'a rien dupliqué.
