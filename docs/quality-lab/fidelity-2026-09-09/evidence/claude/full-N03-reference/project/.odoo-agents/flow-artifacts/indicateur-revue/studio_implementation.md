# Preuve — `studio_implementation` (run `indicateur-revue`)

Rôle `odoo-studio`. Release `/work/changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes`.
Cible unique : copie locale `lab_client` (`http://127.0.0.1:60113`). Aucune instance déclarée,
aucun `apply`, aucun déploiement, aucun module, aucune vue, aucune automatisation, aucun droit touché.

## 1. Ce qui a été créé

Un seul enregistrement, créé en contexte `{"studio": True}` — l'identifiant externe a donc été
forgé par Odoo lui-même (`web_studio/models/studio_mixin.py`), pas à la main :

| Modèle | id | XML-ID relevé | `studio` | `noupdate` |
|---|---|---|---|---|
| `ir.model.fields` | 3740 | `studio_customization.a_revoir_demande_ast_e1e7a054-72be-4a7e-b1ce-2a9ad372c735` | `True` | `True` |

Attributs posés : `name = x_studio_needs_review`, `ttype = boolean`, `state = manual`,
`store = True`, `field_description = "À revoir"`, `depends = "x_studio_days,x_studio_kind"`,
`readonly = True`, `model_id` → `studio_customization.lab_seed_model`.

`created.txt` contient cette seule ligne. Le Studio historique (`lab_seed_*`) n'est ni exporté,
ni modifié.

## 2. Le `compute` retenu, et pourquoi

```python
for record in self:
    record['x_studio_needs_review'] = record['x_studio_days'] >= 7 and record['x_studio_kind'] == 'rental'
```

- Écrit pour `safe_eval(..., mode="exec")` avec les seuls globaux `datetime`, `dateutil`, `time`,
  `self` (`~/odoo-sources/19.0/odoo/addons/base/models/ir_model.py:39-52`) : aucun import, aucun
  `search`, aucun accès à `env.cr`, aucune écriture hors du champ calculé.
- Boucle `for record in self:` explicite et accès par clé `record['...']` — la forme que produit
  l'éditeur Studio ; le calcul reste correct en multi-enregistrements.
- D-22 littérale : seuil `>= 7` (7 inclus, H2) et égalité sur la **valeur technique** `rental`
  (H3, risque n°3 de la revue), jamais sur le libellé « Location ».
- `x_studio_days` non renseigné vaut `0` en base : `0 >= 7` est faux, donc indicateur faux sans
  garde supplémentaire (H4). `x_studio_kind` absent vaut `False`, `False == 'rental'` est faux (H5
  de la table §7). Aucune contrainte ajoutée : hors périmètre.
- `and` renvoie `False` (booléen) quand la première branche est fausse : pas de valeur hybride
  stockée dans une colonne booléenne.

## 3. Limites Studio rencontrées

- **Aucune limite bloquante** : la règle est une comparaison d'entier et une égalité de chaîne,
  largement dans l'enveloppe `safe_eval`. Pas de JS, pas de surcharge, pas d'appel externe.
- **Pas de test Python** : la preuve est le scénario RPC `test_1.py`, rouge avant / vert après.
- **Écart constaté avec la revue (§4 point 10 et H5)** : la revue annonçait que
  `_onchange_compute` (`ir_model.py:763-765`) rendrait le champ `readonly` automatiquement. C'est
  **faux pour une création RPC** : un `onchange` ne joue que dans le formulaire de l'éditeur
  Studio. Le premier passage a donc produit `readonly = False` (`logs/probe_readonly.log`).
  J'ai posé `readonly = True` explicitement dans `build_1.py` pour que le champ livré soit
  identique à ce que l'éditeur Studio aurait produit et conforme à H5.
- **Corollaire à savoir** : même `readonly = True` n'interdit pas une écriture RPC directe sur le
  champ — `readonly` est une contrainte d'interface. La sonde le montre : un
  `write({'x_studio_needs_review': True})` a été **accepté** et la valeur relue valait `True`
  (`logs/probe_readonly.log`). La garantie fonctionnelle vient du recalcul sur `depends`, qui
  écrase toute valeur posée à la main dès que l'une des deux sources bouge — pas d'un refus.
  Une interdiction stricte exigerait une automatisation levant `UserError`, hors périmètre.

## 4. Résultats réels

| Contrôle | Commande | Résultat | Log |
|---|---|---|---|
| Scénario **avant** configuration | `python3 test_1.py` | **ROUGE**, sortie 1, « le champ n'existe pas » | `studio/logs/test_1_avant_rouge.log` |
| Configuration | `python3 build_1.py` | `CREE ir.model.fields 3740` + XML-ID relevé | `studio/logs/build_1.log` |
| Rejeu de la configuration | `python3 build_1.py` | `INCHANGE ... : deja conforme` (idempotent) | `studio/logs/build_1_rejeu.log` |
| Pose de `readonly` | `python3 build_1.py` | `MAJ ... : readonly` | `studio/logs/build_1_readonly.log` |
| Scénario **après** configuration | `python3 test_1.py` | **VERT — 21 contrôles passés**, sortie 0, nettoyage complet (0 enregistrement restant) | `studio/logs/test_1_apres_vert.log` |
| Export du pack | `odoo_pack.py export --only created.txt` | `1 enregistrement(s) de 1 modèle(s) → pack.json`, aucun `unresolved` | `studio/logs/export.log` |
| Diff du pack | `odoo_pack.py diff pack.json` | `0 / 0 / 1 à créer / à modifier / inchangés` | `studio/logs/diff.log` |
| Non-régression avant/après | comparaison `before.json` / relecture | `fields`, `selection_values`, `acl_295`, toutes ACL, `ir.rule`, `ir.ui.view`, `base.automation`, `record_count` : **inchangés** ; seul champ ajouté `x_studio_needs_review` ; seul XML-ID ajouté celui du §1 | `studio/logs/non_regression.log` |

Couverture du scénario (21 contrôles) : définition du champ (unicité, `ttype`, `state`, `store`,
`depends` exactement les deux sources) ; table de vérité à la création — `rental` 6/7/12,
`loan` 7/30, `rental` sans jours, type absent, ni type ni jours ; recalcul à l'écriture de
`x_studio_days` puis de `x_studio_kind` dans les deux sens ; **stockage réel** prouvé par
`search [('x_studio_needs_review','=',True)]` et par son complément exact sur le jeu d'essai.
Toutes les valeurs sont relues côté serveur après écriture ; les données d'essai sont nommées
« — recette » et supprimées, le scénario vérifie lui-même qu'il ne reste rien.

Le pack (`pack.json`) contient **un seul** enregistrement, référence `model_id` par
`{"ref": "studio_customization.lab_seed_model"}` (aucun identifiant numérique, aucun
`unresolved`), et porte `noupdate: true` comme l'`ir.model.data` créé par Studio.

## 5. Fichiers

- `/work/changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes/studio/before.json`
- `/work/changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes/studio/build_1.py`
- `/work/changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes/studio/test_1.py`
- `/work/changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes/studio/created.txt`
- `/work/changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes/studio/pack.json`
- `/work/changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes/studio/logs/` (9 journaux, sorties réelles)

## 6. Ce qui reste à la QA

- **Double application du pack** et contre-épreuve d'idempotence (critères §8) : je ne l'ai pas
  jouée, conformément au périmètre. Point de vigilance : l'`ir.model.data` porte `noupdate = True`
  (marquage Studio standard) — la seconde application doit retrouver l'enregistrement par XML-ID,
  conserver l'`id` 3740 et ne pas créer de doublon ; vérifier aussi que les attributs ne sont pas
  silencieusement ignorés du fait du `noupdate`.
- Relecture des `id` et attributs de `x_name` (3734), `x_studio_days` (3736), `x_studio_kind`
  (3738) et de l'ACL 295 **après** la seconde application, contre `before.json`.
- Rejeu de `test_1.py` après la seconde application (il est autonome et nettoie derrière lui).
- Arbitrage à porter à l'orchestrateur : l'écart §3 sur `readonly` corrige une affirmation de la
  revue fonctionnelle (§4 point 10). Je n'ai pas modifié `revue_fonctionnelle.md`.
