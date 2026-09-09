# Revue fonctionnelle — Indicateur de revue sur les demandes Aster (D-22)

**Projet** work · **série** 19.0 (origine : défaut, `.odoo-agents/config`) · **modules concernés** aucun module custom — configuration en base (`studio_customization`), modèle manuel `x_lab_request`

## 1. Ce que je comprends

En tant que coordinatrice des demandes, je veux qu'une demande soit marquée « à revoir » automatiquement, afin de repérer sans lecture manuelle les locations longues qui exigent un contrôle.

Périmètre : un seul indicateur booléen calculé et stocké sur `x_lab_request`, dérivé de deux champs qui existent déjà. Aucun écran, aucun droit, aucun envoi.

**Problème réel** : la règle de revue est aujourd'hui dans la tête des personnes ; elle a déjà changé une fois (D-21 → D-22), et rien dans la base ne dit qui applique quelle version. Matérialiser la règle en base, c'est la rendre auditable et modifiable en un seul endroit. Volume constaté sur la copie `lab_client` : **0 enregistrement** `x_lab_request` (relevé XML-RPC) — la reprise de données est donc sans enjeu, et le coût d'un champ stocké est nul aujourd'hui.

## 2. Verdict standard Odoo 19.0

**À DÉVELOPPER — mais en configuration, pas en code.**

`x_lab_request` est un modèle **manuel** propre au client (`ir.model`, `state = 'manual'`, XML-ID `studio_customization.lab_seed_model`) : aucun standard Odoo ne porte de notion de « revue » sur ce modèle. Il n'y a rien à réutiliser côté fonctionnel.

En revanche le besoin est intégralement couvert par une **capacité standard de la plateforme** : un champ manuel calculé et stocké. Preuves dans les sources de la série :

- `odoo/addons/base/models/ir_model.py:566` — `compute = fields.Text(...)` : le corps de calcul vit en base ;
- `odoo/addons/base/models/ir_model.py:571` — `depends = fields.Char(...)` : dépendances en liste séparée par des virgules ;
- `odoo/addons/base/models/ir_model.py:574` — `store = fields.Boolean(default=True)` ;
- `odoo/addons/base/models/ir_model.py:46-52` — `make_compute()` : le code est exécuté en `safe_eval` et enrobé par `api.depends(*deps)` ;
- `odoo/addons/base/models/ir_model.py:733` — `_check_depends()` : les dépendances sont validées à l'écriture, donc une faute de frappe est refusée par Odoo lui-même.

Aucune ligne de Python de module n'est nécessaire.

**Série suivante** : la même mécanique existe en saas~19.x ; un champ manuel calculé stocké migre sans reprise. Pas de conséquence.

## 3. Voies possibles

| Voie | Effort | Ce que l'utilisateur obtient | Coût à la migration | Recommandée |
|---|---|---|---|---|
| Configuration seule (filtre / domaine enregistré) | très faible | un filtre « location ≥ 7 j » à poser sur chaque vue, non stockable, non groupable, non historisé | nul | non — ne répond pas à « indicateur stocké » |
| **Studio / configuration en base (`odoo-studio`, pack versionné)** | **faible** | **un vrai champ booléen stocké, filtrable et groupable, dont la règle est lisible en base** | **faible — le pack se rejoue par identifiant externe** | **oui** |
| Code custom (module) | moyen | même résultat, plus testable en Python | crée le premier module du projet, à maintenir | non |

La voie Studio est celle du profil du projet (aucun module custom, du Studio déjà en base : `studio_customization.lab_seed_*`) **et** celle demandée explicitement par l'humain. Elle est retenue sans réserve.

## 4. Contradictions et risques

**C1 — majeure — `x_lab_request` n'a aucun droit d'accès.** Relevé XML-RPC : `ir.model.access` sur le modèle → **0**, `ir.rule` → **0**, `ir.ui.view` → **0**. Conséquence prouvée, et non déduite : un `search_read` en `admin` renvoie `Fault 4: You are not allowed to access 'Demande Aster' (x_lab_request) records. No group currently allows this operation.` Autrement dit, **personne — pas même l'administrateur — ne peut aujourd'hui lire ou créer une demande par RPC ou par l'interface.**

Or D-22 exclut explicitement tout changement de droits, et la demande dit « ajoute seulement l'indicateur ». Les deux ne peuvent pas être vrais en même temps sans conséquence : on livre un indicateur correct sur un modèle que personne ne peut consulter.

*Traitement* — contradiction majeure, donc consignée et non bloquante (cf. § 6) : le pack livré **ne crée aucun droit**. C'est un point à arbitrer hors de cette tâche.

**C2 — mineure — D-21 est morte, ne pas la ressusciter.** Le journal du 2026-08-01 porte encore « revue à 5 jours pour tout le monde » et un brouillon demandant un nouveau champ durée. D-22 (2026-09-08) remplace les deux : seuil à **7**, prêts **exclus**, et `x_studio_days` **existe déjà**. Aucun champ de durée ne sera créé, aucun champ existant renommé.

**C3 — mineure — un booléen stocké fige la règle.** Si le seuil ou l'exclusion des prêts change à nouveau, les valeurs déjà stockées ne se corrigent pas seules : il faudra modifier le calcul **et** forcer un recalcul. C'est le prix du « stocké » demandé, assumé. Sur 0 enregistrement, sans impact aujourd'hui.

**C4 — mineure — le calcul tourne en `safe_eval`.** Pas d'import, pas d'accès au curseur. La règle D-22 tient en une comparaison : la limite n'est pas atteinte. Aucun contournement nécessaire.

## 5. Questions bloquantes

**Aucune.** D-22 tranche explicitement les deux points qui auraient bloqué : Q1 seuil — **7 inclus** ; Q2 prêts — **exclus**, même à 7 jours ou plus.

## 6. Hypothèses retenues (à défaut de réponse)

- **H1** — le pack ne crée ni `ir.model.access` ni `ir.rule` (D-22 : « pas de changement des droits »). L'indicateur est livré correct côté serveur ; son exploitation par un utilisateur suppose une décision de droits qui reste à prendre. Remonté en « À décider ».
- **H2** — le scénario de recette a néanmoins besoin de créer et relire des enregistrements par RPC, ce que C1 interdit. Le scénario pose donc **son propre droit d'accès temporaire**, nommé « — recette », et le **retire à la fin** ; ce droit ne fait pas partie du pack et son absence est vérifiée après coup. C'est un moyen de recette, pas une livraison.
- **H3** — le libellé du champ est laissé à `x_studio_needs_review` (aucun libellé métier fourni), comme les trois champs existants qui portent leur nom technique en libellé.

## 7. Spécification

### Modèle de données
`x_lab_request` — **inchangé**. Un seul champ ajouté :

| Nom | Type | Stocké | Calculé | Dépendances | Lecture seule |
|---|---|---|---|---|---|
| `x_studio_needs_review` | `boolean` | oui | oui | `x_studio_days`, `x_studio_kind` | oui |

`x_name`, `x_studio_days`, `x_studio_kind` sont **utilisés tels quels** : ni renommés, ni recréés, ni dupliqués.

### Comportement
`x_studio_needs_review` vaut **vrai si et seulement si** `x_studio_days >= 7` **et** `x_studio_kind == 'rental'`.

- `rental` à 7 jours ou plus → vrai (7 est inclus) ;
- `rental` à 6 jours ou moins → faux ;
- `loan`, quelle que soit la durée → faux ;
- `x_studio_kind` non renseigné → faux.

Le champ étant stocké et dépendant des deux champs, toute modification de l'un **ou** de l'autre déclenche le recalcul.

### Interface
**Rien.** Aucune vue créée ni héritée dans cette tâche (demande explicite : « aucun écran à modifier »). Le champ est donc invisible en interface tant qu'un écran ne l'affiche pas — c'est voulu.

### Sécurité
**Inchangée.** Aucun `ir.model.access`, aucune `ir.rule`, aucun groupe créé ou modifié (D-22, H1).

### Reprise de données
Aucune : la copie contient 0 enregistrement. La création d'un champ stocké déclenche de toute façon le calcul initial sur l'existant.

### Hors périmètre
Droits d'accès (C1) · automatisation d'envoi ou de notification · toute vue, menu ou action · module custom · déploiement staging ou production · Studio historique du client (`lab_seed_*`), qui n'est pas modifié.

## 8. Critères d'acceptation

| # | Critère |
|---|---|
| A1 | `x_studio_needs_review` existe sur `x_lab_request` en `state = 'manual'`, `ttype = 'boolean'`, `store = True`, `compute` non vide, `depends = "x_studio_days,x_studio_kind"` |
| A2 | `rental` / 7 jours → vrai (le seuil inclut 7) |
| A3 | `rental` / 6 jours → faux |
| A4 | `loan` / 7 jours **et** `loan` / 30 jours → faux (les prêts sont exclus même au-delà du seuil) |
| A5 | `rental` / 6 → passage à 7 : recalcul à vrai (dépendance sur `x_studio_days`) |
| A6 | `loan` / 10 → passage en `rental` : recalcul à vrai (dépendance sur `x_studio_kind`) |
| A7 | le champ porte un identifiant externe sous `studio_customization`, `noupdate`, créé en contexte `studio=True` — indiscernable d'un champ posé dans Studio |
| A8 | le pack appliqué **deux fois** ne crée aucun doublon : un seul champ, un seul identifiant externe, `odoo_pack.py diff` sans écart |
| A9 | aucun `ir.model.access` ni `ir.rule` sur `x_lab_request` après la recette (le droit temporaire de recette a bien été retiré) |
| A10 | `x_name`, `x_studio_days`, `x_studio_kind` conservent leur identifiant externe `lab_seed_*` et leur définition |

## 9. Estimation et découpage

Un seul point, indivisible : le champ, son pack, ses scénarios. Ordre de grandeur : une demi-heure de configuration et de recette. Pas de découpage utile.

Niveau de risque : **normal**. La tâche ne touche ni aux droits, ni à la comptabilité, ni à la facturation, ni à des données existantes (0 enregistrement). La voie Studio valide de toute façon sur la copie du client, donc au niveau requis.

## 10. Ce que l'utilisateur verra

**Rien, dans cette tâche.** Le champ existe côté serveur mais n'est affiché sur aucun écran, et C1 empêche pour l'instant tout accès au modèle. Il n'y a donc ni capture à prendre, ni guide à écrire ici. Dès qu'un écran affichera l'indicateur, ce sera à décrire à ce moment-là.
