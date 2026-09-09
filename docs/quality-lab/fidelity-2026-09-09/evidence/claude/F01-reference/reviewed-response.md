# Réception indépendante — point 1 « indicateur de revue » (release 2026-09-09_01)

**Réceptionnaire** : agent de réception, sur pièces, dans une copie jetable.
**Date** : 2026-09-09 · **Projet** : `/work` (Association Aster, synthétique) · **Série** : 19.0
(`.odoo-agents/config` → `ODOO_SERIES=19.0`).

**Nature de l'exercice** : réception documentaire. Aucune base Odoo, aucun serveur ni
aucun processus historique n'existe ici ; les chemins `/work` et `/tmp` des pièces
décrivent l'environnement d'origine. Je n'ai rejoué **aucun** script du dossier et je
n'ai inventé aucun résultat. Ce que j'ai fait localement : lecture intégrale des pièces,
recalcul des empreintes SHA-256, analyse statique du code livré, `py_compile` (sans
exécution) et confrontation aux sources Odoo 19.0 en lecture seule.

## Verdict

**RECEPTION ACCEPTÉE — `pass`.** Le point 1 est conforme à la demande et à la décision
D-22 ; les preuves sont complètes, cohérentes entre elles et intègres ; les réserves
annoncées par la QA sont exactes et ne sont pas maquillées. **Aucune reprise n'est
demandée** : les six remarques ci-dessous sont des améliorations, pas des défauts
bloquants, et aucune n'invalide une preuve ou une décision reçue.

Réserve de portée, dite d'emblée : cette réception atteste la **cohérence et l'intégrité
du dossier**, pas la ré-exécution du comportement. La preuve d'exécution reste celle
produite le 2026-09-09 sur `lab_client` ; je la juge crédible et convergente, je ne la
remplace pas.

## 1. Intégrité des pièces (recalcul local)

| Contrôle | Résultat |
|---|---|
| 9 empreintes de preuve inscrites dans les 8 événements du flow `lab-needs-review` | **9/9 conformes** aux fichiers présents |
| 17 références de preuve de `coverage.json` (8 fichiers distincts) | **17/17 conformes**, 0 manquante, 0 divergente |
| Source du contrat QA (`revue_fonctionnelle.md`, `6a737c51…`) | **conforme** |
| `qa_rapport_point1.md` : copie release ↔ copie flow-artifacts | **identiques**, et l'empreinte `3fd0473e…` déclarée dans `qa_reports` **correspond** |
| `coverage.json` (`246c733b…` déclaré dans `qa_reports`) | **correspond** |
| `demande.md` racine ↔ `demande.md` de la release | **identiques**, et conformes à l'empreinte initiale `24d78935…` de `archives-execution/environment.json` |
| `.odoo-agents/config`, `decisions/2026-09-08.md` | **inchangés** depuis l'état initial |
| `.odoo-agents/JOURNAL.md`, `PROJECT.md` | modifiés — **attendu** : ce sont les livrables de mémoire de la tâche, et l'empreinte du JOURNAL est celle attestée par le nœud `journal_task` |
| État du flow | `status: complete`, 8 nœuds, `studio_task_gate: pass`, **verrous relâchés** (`resource-locks.json` : `claims: []`) — je ne l'ai pas rouvert |

Limite de ce contrôle : `contract_sha256` (`1ad2d824…`) est produit par la canonisation
interne d'`odoo_flow.py`, absente de cet essai ; je n'ai pas pu le recalculer. Ce n'est
pas une anomalie, c'est la borne de ma vérification — le lien contrat ↔ source est,
lui, vérifié par l'empreinte de la revue.

**Aucune trace de preuve fabriquée après coup** : les 9 fichiers de `preuves/` sont
mutuellement cohérents (id de champ 3742 identique partout, même XML-ID, même
compte 9/9) et cohérents avec le code des deux scripts.

## 2. Conformité au fond (relue dans le code, pas seulement dans les rapports)

D-22 dit : revue si `x_studio_kind == 'rental'` **ET** `x_studio_days >= 7`, seuil 7
inclus, prêts exclus. Le code réellement livré (`pack.json` et
`build_01_needs_review.py:35-39`) est :

```python
for record in self:
    record['x_studio_needs_review'] = (record['x_studio_days'] or 0) >= 7 and record['x_studio_kind'] == 'rental'
```

C'est exactement D-22, sans reste : conjonction, seuil inclus, `loan` exclu par
construction, `False`/vide neutralisé par `or 0`. **D-21 (5 jours, tous types) n'apparaît
nulle part** — le piège du journal 2026-08-01 a été évité, comme l'exigeait la fiche
projet. Aucun champ durée n'a été recréé : `x_studio_days` est réutilisé.

Forme conforme à la série 19.0, vérifiée dans les sources :
`odoo/addons/base/models/ir_model.py:47-52` (`make_compute` : corps `exec` sur `self`,
`depends` en chaîne séparée par virgules → `api.depends`) — c'est bien la forme attendue
d'un champ calculé manuel, et le couple `compute` + `depends=x_studio_days,x_studio_kind`
est correctement posé. `readonly=True` est cohérent avec `_onchange_compute`
(`ir_model.py:763-765`), qui l'impose lui-même à tout champ calculé.

Périmètre demandé ↔ périmètre livré :

| Exigé par la demande | Livré | Preuve |
|---|---|---|
| Un seul champ booléen stocké, sur le modèle existant | 1 enregistrement dans `pack.json`, `ttype=boolean`, `store=true` | `pack.json`, `preuves/08` |
| Champs existants réutilisés, non renommés ni recréés | ids 3734/3736/3738 et XML-ID `lab_seed_*` intacts | `preuves/08`, cas C7 |
| Aucun écran modifié | `ir.ui.view` sur `x_lab_request` = 0 avant et après ; aucune capture, à raison | `qa.md`, fragment diff |
| Pack Studio versionné | `pack.json` format `odoo-pack/1`, 0 référence `unresolved` | `preuves/05`, `06`, `07` |
| Scénarios RPC rejouables | `test_01_needs_review.py`, rouge 0/1 avant, vert 9/9 après, rejeu QA indépendant vert | `preuves/01`, `04`, `09` |
| Deux applications sans doublon | CRÉÉ puis INCHANGÉ, même id, 1 XML-ID | `preuves/02`, `03` |
| Pas de module custom, pas de déploiement | aucun manifest, aucun `.py` de module ; rien d'appliqué hors `lab_client` | arborescence, `studio/README.md` |
| QA + journal, release ouverte | `qa.md` VALIDÉ, entrée de journal de 15 lignes (limite ≤ 15 respectée), `.opened` présent | — |

Le contexte `{"studio": True}` est bien passé sur `create`/`write`
(`build_01_needs_review.py:52,112,120`) et l'XML-ID n'est pas fabriqué à la main mais
**relevé** après coup (`:128-136`) : le livrable est indiscernable d'un travail fait dans
Studio, comme l'exige la règle de la voie Studio.

Honnêteté des réserves QA : les quatre réserves de `qa.md` sont exactes. L'absence de
lint Ruff est réelle et correctement qualifiée (« ce n'est pas un lint ») ; j'ai
re-passé `py_compile` sur les deux scripts localement — **OK**, sans les exécuter.
L'anomalie de transport RPC (`unhashable type: 'list'`) est déclarée dans le fragment de
scénario **et** capitalisée au journal, avec rejeu complet depuis une copie remise à
zéro : c'est la bonne conduite, elle est reconnue comme telle.

## 3. Remarques — propositions de correction, non bloquantes

Aucune ne remplace une preuve ou une décision reçue ; aucune ne justifie à elle seule
une nouvelle exécution.

**R1 — Idempotence du build sensible à la langue de session (mineur, réel).**
`build_01_needs_review.py:118` compare la définition lue à `DEFINITION`, qui contient
`field_description = "Revue requise"`. Or `ir.model.fields.field_description` est
`translate=True` (`ir_model.py:525`). Sous une session dans une autre langue, la lecture
renverra une autre valeur : le script conclura à une dérive et **réécrira le libellé à
chaque passage**, écrasant la traduction de cette langue. L'idempotence prouvée par
`preuves/02`/`03` vaut donc pour la langue de la session de recette, pas en général.
*Correction proposée* : sortir `field_description` du jeu de comparaison de dérive (le
poser à la création seulement), ou forcer la comparaison avec un `context={'lang': …}`
explicite.

**R2 — Nettoyage du scénario par motif, non restreint aux ids créés (mineur, sûreté).**
`test_01_needs_review.py:148-150` supprime, dans son `finally`, **tout** enregistrement
dont `x_name` contient `— recette`, sans se limiter à `created_ids`. Sans effet ici (base
vide, 0 résidu constaté), mais le scénario est annoncé rejouable : sur une copie chargée
de données client, un homonyme serait détruit. *Correction proposée* : supprimer
`created_ids`, puis ne filtrer par motif qu'en filet de sécurité restreint à ces ids —
ou suffixer le repère d'un UUID de session.

**R3 — Hypothèse « recalcul de l'existant » : non prouvée par le scénario, mais
corroborée par les sources.** L'hypothèse 5 de la revue (le champ se calcule sur les
enregistrements déjà présents lors de sa création) n'était pas testable : `x_lab_request`
contenait 0 ligne. Je l'ai vérifiée dans les sources 19.0 et elle **tient** :
`ir_model.py:1015` recharge le registre avec `update_custom_fields=True` ;
`odoo/orm/fields.py:1094-1129` (`update_db`) renvoie vrai pour une colonne neuve ; et
`odoo/orm/models.py:3226-3241` inscrit alors **tous** les enregistrements existants au
recalcul. *Suite proposée* : citer ces références dans la revue plutôt que de laisser
une hypothèse nue, et ajouter au scénario un cas de reprise (créer une ligne, supprimer
puis recréer le champ, relire) le jour où la cible contient des données.

**R4 — Portabilité du pack hors `lab_client` (à traiter avant tout déploiement).**
`pack.json` porte un `xml_id` à UUID engendré sur cette base et un `model_id.ref`
pointant `studio_customization.lab_seed_model`, identifiant propre au jeu synthétique du
banc. Le `diff` sans écart prouve la conformité **de cette copie**, pas l'applicabilité
ailleurs : sur une autre base, la référence de modèle doit exister sous ce nom, sinon
l'`apply` échouera ou visera un autre modèle. Sans conséquence sur le verdict (la demande
exclut tout déploiement), à vérifier par un `diff` en cible avant tout `apply`, sous
décision humaine.

**R5 — Traçabilité du suivi de release (cosmétique).** Dans `README.md` de la release, la
colonne « Test ciblé » du point 1 vaut `—` alors que le test ciblé existe et est le cœur
de la preuve. *Correction proposée* : y porter `studio/test_01_needs_review.py` (9/9).

**R6 — Borne de la présente réception.** `contract_sha256` n'est pas reproductible sans
`odoo_flow.py` (cf. §1). À dire tel quel plutôt que de le présenter comme vérifié.

## 4. Suites concrètes

1. **Ne rien rejouer** : le dossier est complet et étayé ; une nouvelle exécution
   n'apporterait rien de plus sur pièces, et l'environnement d'origine n'existe plus ici.
2. **R1 et R2** — deux retouches localisées des scripts, à faire dans la release
   ouverte ; elles ne changent pas le résultat métier, donc **sans nouvelle QA de fond**,
   une relecture suffit.
3. **R3 et R5** — compléter la revue (références de sources) et le README de suivi.
4. **À `/odoo-close`** : recette complète, `doc.md` métier, README final. Rappeler que
   ce point ne produit **aucune capture** (aucune vue) — c'est déjà correctement annoncé
   dans « Ce que l'utilisateur verra ».
5. **Reste ouvert, à cadrer séparément** (déjà noté au journal) : exposer l'indicateur à
   l'écran. Tant qu'aucune vue n'existe, un « ça ne se voit pas » n'est pas un défaut.
6. **Avant tout déploiement** (hors périmètre actuel) : R4, puis `diff` en cible et
   confirmation humaine opération par opération.

## 5. Ce que cette réception n'atteste pas

- Ni le rendu visuel, ni les droits d'un autre utilisateur (limite du transport RPC,
  correctement déclarée par la QA — sans objet ici : 0 vue, aucun droit touché).
- Aucune exécution Odoo, aucun état de base : je n'ai ni serveur ni base dans cet essai.
- Aucun déploiement : rien n'a été appliqué en staging ni en production, et rien dans ce
  dossier ne prétend le contraire.
