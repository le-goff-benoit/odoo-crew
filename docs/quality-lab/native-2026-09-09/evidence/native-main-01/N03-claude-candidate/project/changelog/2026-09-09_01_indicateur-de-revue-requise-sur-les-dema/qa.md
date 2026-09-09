# QA — release « Indicateur de revue requise sur les demandes »

## 2026-09-09 — Point 1 · [studio] `x_studio_needs_review` sur `x_lab_request`

**Mode** QA de tâche (niveau normal — ni droits, ni compta, ni facturation, ni
données existantes : 0 enregistrement métier au départ). La recette complète
reste à la clôture (`/odoo-close`).
**Verdict : VALIDÉ.**

### Contrôles

| Contrôle | Commande | Résultat | Preuve |
|---|---|---|---|
| Forme des scripts livrés | `python3 -m py_compile` sur les 5 fichiers | OK (pas de module → `odoo-lint.sh --changed` sans objet) | `flow-artifacts/…/studio_diff_qa.md` |
| Scénarios **rouges avant** configuration | `test_1_needs_review.py`, `…_orm.py` | ROUGE, motif attendu (champ absent) | `qa/1_rpc_avant.log`, `qa/1_orm_avant.log` |
| Construction idempotente | `build_1_needs_review.py` ×3 | 1 création puis « déjà conforme », `created.txt` +0 | `qa/1_build_1..4.log` |
| Pack — export | `odoo_pack.py export --only created.txt` | 1 enregistrement, 0 référence `unresolved` | `studio/pack.json` |
| Pack — **deux applications sans doublon** | `apply` ×2 depuis un état sans le champ | 1 créé, puis 0/0/1 inchangé | `qa/1_pack_double_application.log` |
| Pack — diff | `odoo_pack.py diff` | 0 à créer / 0 à modifier / 1 inchangé | `qa/1_pack_diff_*.log`, fragment diff |
| Absence de doublon en base | relevé `ir.model.fields` + `ir.model.data` | 1 champ, 1 identifiant externe, 4 champs `x_` au total | `qa/1_etat_final.log` |
| Scénario XML-RPC (configuration) | `python3 test_1_needs_review.py` | **VERTE — 12/12** | `qa/1_rpc_apres.log` |
| Scénario ORM (table de vérité D-22) | `labctl shell test_1_needs_review_orm.py` | **VERTE — 16/16** | `qa/1_orm_apres.log` |
| Écran | — | aucune vue modifiée, aucune vue sur le modèle → aucune capture requise | revue §10 |

Les deux scénarios ont été rejoués une seconde fois, indépendamment, sur l'état
reconstruit par le seul `pack.json` : verts tous les deux
(`flow-artifacts/…/studio_scenario_qa.md`). Les données de recette sont
supprimées ; la copie `lab_client` ne garde que le champ livré.

### Critères d'acceptation de la revue

| Critère | Couvert par | État |
|---|---|---|
| C1 location 7 j (seuil inclus) → vrai | scénario ORM | ✅ |
| C2 location 6 j → faux | scénario ORM | ✅ |
| C3 location 30 j → vrai | scénario ORM | ✅ |
| C4 prêt 7 j et 30 j → faux | scénario ORM | ✅ |
| C5 sans type / 0 j / −3 j → faux | scénario ORM | ✅ |
| C6 bascule du type recalcule | scénario ORM | ✅ |
| C7 bascule de la durée recalcule | scénario ORM | ✅ |
| C8 valeur stockée et cherchable | scénario ORM (colonne SQL + `search`) et RPC (`store=True`) | ✅ |
| C9 reprise des enregistrements antérieurs | scénario ORM, 3 enregistrements créés avant le champ | ✅ |
| C10 identifiant externe `studio_customization`, `noupdate`, créé par Odoo | scénario RPC | ✅ (voir réserve levée ci-dessous) |
| C11 champs existants inchangés (`lab_seed_*`) | scénario RPC | ✅ |
| C12 seconde exécution du build sans doublon | build ×3 + relevé | ✅ |
| C13 seconde application du pack sans changement | `apply` ×2 + `diff` | ✅ |

**12/13 au premier passage, 13/13 après une reprise.** Aucun critère laissé de côté.

### Reprise n°1 — `noupdate` à la création

Le premier passage a rendu C10 rouge : l'identifiant externe créé sortait avec
`studio=True` mais `noupdate=False`, alors que les quatre `lab_seed_*` déjà en
base sont à `noupdate=True`.

Vérification dans les sources plutôt que dans le souvenir :
`web_studio/models/ir_model_data.py:12-17` ne pose que `studio` à la
**création** ; `noupdate` n'est posé qu'au **`write`** suivant (lignes 19-25),
que Studio déclenche lui-même par `data.write({})` dans
`create_studio_model_data` (`web_studio/models/ir_model.py:62`) dès qu'on
retouche l'objet. Le script de construction rejoue exactement cet appel, en
contexte `studio=True`, pour converger vers l'état protégé. C10 vert ensuite.

C'est une correction du contrôle **et** du livrable : la documentation de rôle
résume « marqué `studio` et `noupdate` », ce qui n'est vrai qu'après une
écriture. Leçon candidate (voir `JOURNAL.md`).

### Réserves — hors périmètre, à arbitrer par l'humain

1. **`x_lab_request` n'a aucun `ir.model.access` ni `ir.rule`.** Hors
   superutilisateur, aucun accès n'est possible
   (`odoo/addons/base/models/ir_model.py:2134-2167`) : concrètement, **aucun
   utilisateur réel ne peut voir l'indicateur aujourd'hui**. D-22 interdit de
   toucher aux droits, donc rien n'a été fait ici. C'est un préalable à toute
   mise en service, pas un défaut introduit par cette tâche.
2. **Aucun écran** ne porte le champ (le modèle n'a aucune vue). L'indicateur
   est utilisable en filtre et en regroupement dès qu'un écran existera.
3. **Aucun déploiement.** Le pack n'a été appliqué que sur la copie locale
   `lab_client`, conformément à la demande.
