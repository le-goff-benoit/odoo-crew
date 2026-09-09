# Revue fonctionnelle — Indicateur de revue requise sur les demandes Aster

**Projet** Association Aster (`/work`) · **série** 19.0 (origine : défaut, `.odoo-agents/config`) · **modules concernés** aucun module custom — configuration en base (`studio_customization`), modèle manuel `x_lab_request`

## 1. Ce que je comprends

En tant que coordinatrice des demandes, je veux qu'une demande soit marquée
automatiquement « à revoir » afin de repérer sans lecture manuelle les
locations longues qui doivent passer en revue.

Périmètre : un seul indicateur booléen **calculé et stocké**
`x_studio_needs_review` sur `x_lab_request`, dérivé des deux champs déjà en
base. Aucun écran, aucune automatisation, aucun droit, aucun champ nouveau
autre que l'indicateur.

**Problème réel** : la règle de revue (D-22) n'existe aujourd'hui que dans un
document de décision ; rien dans la base ne la porte, donc rien n'est
filtrable ni groupable. L'indicateur stocké est exactement ce qui manque.
Volume mesuré sur la copie `lab_client` : **0 enregistrement** — pas de
reprise de données à craindre (vérifié, voir §7).

## 2. Verdict standard Odoo 19.0

**À DÉVELOPPER (par configuration en base)** — au sens strict, il n'y a rien à
« trouver » dans le standard : `x_lab_request` est un modèle manuel propre au
client, aucun module standard ne connaît ses champs. Ce qui existe déjà et
qu'il faut **utiliser plutôt que réimplémenter**, c'est le mécanisme de champ
manuel calculé stocké :

- `~/odoo-sources/19.0/odoo/addons/base/models/ir_model.py:47` — `make_compute()` :
  un champ manuel porte son code dans `ir.model.fields.compute`, évalué en
  `safe_eval` en mode `exec` avec `self` ; les dépendances viennent de
  `ir.model.fields.depends` (chaîne séparée par des virgules).
- `~/odoo-sources/19.0/odoo/addons/base/models/ir_model.py:566-574` — champs
  `compute`, `depends`, `store` sur `ir.model.fields`.
- `~/odoo-sources/19.0/odoo/addons/base/models/ir_model.py:763` —
  `_onchange_compute` : Studio passe le champ en `readonly` dès qu'un `compute`
  est saisi ; on fait pareil.
- `~/odoo-sources/19.0-enterprise/web_studio/models/studio_mixin.py:20` et
  `web_studio/models/ir_model.py:49` — en contexte `studio=True`, Odoo crée
  lui-même l'identifiant externe dans `studio_customization`, marqué `noupdate`.

Donc : **aucune ligne de Python de module n'est justifiée**. Le besoin est
couvert par un champ Studio calculé.

**Série suivante** : rien à anticiper, le mécanisme des champs manuels calculés
est identique en 19.1/19.4 ; le champ étant manuel, il n'y a pas de dette de
migration au sens d'un module custom.

## 3. Voies possibles

| Voie | Effort | Ce que l'utilisateur obtient | Coût à la migration | Recommandée |
|---|---|---|---|---|
| Configuration standard seule | — | rien : aucun paramètre Odoo ne porte cette règle métier | — | non |
| **Studio / configuration en base (pack versionné)** | ~1 h | indicateur stocké, filtrable et groupable, calculé à chaque écriture | quasi nul (champ manuel, repris avec la base) | **oui** |
| Module custom | ~0,5 j + cycle de livraison | même résultat | payé à chaque montée de version | non |

Profil du projet : **0 module custom, du Studio déjà en base** (`lab_seed_*`)
→ voie Studio par défaut, et voie demandée explicitement par l'humain. Les
limites de Studio sont annoncées avant de faire (§4).

## 4. Contradictions et risques

| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|---|---|---|---|
| 1 | majeure | Le journal du 2026-08-01 porte D-21 (revue à 5 jours, tous types) ; la demande porte D-22 (7 jours, locations seules) | Implémenter la mauvaise règle est le seul vrai risque fonctionnel de cette tâche | **D-22 fait foi** (décision du 2026-09-08, qui remplace explicitement D-21). Seuil 7 **inclus**, `loan` **exclu**. Critères d'acceptation §8 écrits sur les valeurs limites 6/7 et les deux types |
| 2 | majeure (recette, pas fonctionnel) | `x_lab_request` n'a **aucun** `ir.model.access` ni `ir.rule` (inventaire de `lab_client`) | `ir_model.py:2134-2167` : sans ACL, tout accès hors superutilisateur est refusé. Donc aucun utilisateur ne peut lire le modèle, et un scénario XML-RPC ne peut pas créer/relire un enregistrement | D-22 interdit de toucher aux droits → **hors périmètre**. La recette au niveau enregistrement se joue en ORM superutilisateur (`labctl shell`), la recette de la configuration se joue en XML-RPC. Signalé à l'humain : tant que ce modèle n'a pas d'ACL, l'indicateur est invisible pour tout utilisateur réel |
| 3 | mineure | `x_studio_kind` peut être vide (aucune valeur par défaut en base) | Une demande sans type n'est ni `rental` ni `loan` | Vide ⇒ pas de revue (règle : `= 'rental'` strictement). Testé |
| 4 | mineure | `x_studio_days` est un entier libre (pas de contrainte de borne) | Valeurs 0 ou négatives possibles | `< 7` ⇒ pas de revue. Testé sur 0 et −3 |
| 5 | mineure | Champ calculé **stocké** et `readonly` | L'utilisateur ne pourra pas forcer l'indicateur à la main | Voulu par D-22 (« calculé et stocké »). Écrit dans la spec |
| 6 | information | `safe_eval` | Le code du calcul tourne sans import ni accès au curseur | Le calcul demandé est une comparaison sur deux champs du même enregistrement : **aucune limite de Studio n'est touchée** |

Non-dits vérifiés : pas de multi-société sur ce modèle (aucun `x_studio_company_id`),
pas de portail, pas d'impact compta / facturation / stock, pas de vue à modifier
(aucune `ir.ui.view` sur ce modèle), aucune automatisation existante à croiser.

## 5. Questions bloquantes

Aucune. D-22 tranche les deux points qui auraient bloqué (seuil inclusif,
sort des prêts) : « Q1 seuil : 7 inclus ; Q2 prêts : exclus ».

## 6. Hypothèses retenues (à défaut de réponse)

- Le libellé du champ est `Revue requise` ; le nom technique imposé par la
  demande est `x_studio_needs_review` (et non le `x_studio_revue_requise` que
  Studio dériverait du libellé). La demande prime.
- Les champs `x_name`, `x_studio_days`, `x_studio_kind` ne sont ni renommés,
  ni recréés, ni réécrits : leurs identifiants externes `lab_seed_*` restent
  intacts (une écriture en contexte `studio` les retoucherait — évité).
- La correction de l'absence d'ACL (risque n°2) n'est pas faite ici ; elle est
  remontée à l'humain comme point distinct.

## 7. Spécification

### Modèle de données
`x_lab_request` — **un seul champ ajouté** :

| Attribut | Valeur |
|---|---|
| `name` | `x_studio_needs_review` |
| `field_description` | `Revue requise` |
| `ttype` | `boolean` |
| `store` | `True` |
| `depends` | `x_studio_days,x_studio_kind` |
| `readonly` | `True` |
| `state` | `manual` |
| identifiant externe | créé par Odoo dans `studio_customization`, contexte `studio=True` |

### Comportement
Code du calcul (safe_eval, `exec`, `self` disponible) :

```python
for record in self:
    record['x_studio_needs_review'] = record['x_studio_kind'] == 'rental' and record['x_studio_days'] >= 7
```

Vrai si et seulement si le type vaut `rental` **et** la durée est ≥ 7.
Recalculé à chaque création et à chaque modification de l'un des deux champs
dont il dépend.

### Interface
**Rien de visible dans cette tâche** : aucune vue n'est modifiée (le modèle
n'a d'ailleurs aucune vue). Le champ est disponible pour un filtre ou un
regroupement dès qu'un écran existera.

### Sécurité
Inchangée. Aucun groupe, aucune ACL, aucune règle créée ou modifiée (D-22).

### Reprise de données
0 enregistrement en base au moment de la tâche. Le mécanisme de recalcul des
enregistrements existants est tout de même prouvé : la recette crée des
enregistrements **avant** la création du champ et vérifie leur valeur après.

### Hors périmètre
Automatisation d'envoi, notification, activité, changement de droits, ACL du
modèle, écran, rapport, déploiement (staging ou production), module custom.

## 8. Critères d'acceptation

- [ ] **C1** Étant donné une demande `rental` de 7 jours, quand elle est créée, alors `x_studio_needs_review` vaut vrai (seuil inclusif).
- [ ] **C2** Étant donné une demande `rental` de 6 jours, quand elle est créée, alors l'indicateur vaut faux.
- [ ] **C3** Étant donné une demande `rental` de 30 jours, quand elle est créée, alors l'indicateur vaut vrai.
- [ ] **C4** Étant donné une demande `loan` de 7 jours (et de 30 jours), quand elle est créée, alors l'indicateur vaut faux — les prêts sont exclus même au-delà du seuil.
- [ ] **C5** Étant donné une demande sans type, ou avec une durée nulle ou négative, alors l'indicateur vaut faux.
- [ ] **C6** Étant donné une demande `loan` de 10 jours à faux, quand son type passe à `rental`, alors l'indicateur passe à vrai sans autre action (dépendance sur le type).
- [ ] **C7** Étant donné une demande `rental` de 10 jours à vrai, quand sa durée passe à 3, alors l'indicateur passe à faux (dépendance sur la durée).
- [ ] **C8** L'indicateur est **stocké** : sa valeur est relisible par une recherche serveur (`search` sur `x_studio_needs_review = True`), pas seulement calculée à l'affichage.
- [ ] **C9** Les enregistrements créés **avant** l'ajout du champ portent la bonne valeur après ajout (reprise de données).
- [ ] **C10** Le champ porte un identifiant externe dans `studio_customization`, marqué `noupdate`, créé par Odoo en contexte `studio=True`.
- [ ] **C11** Les trois champs existants (`x_name`, `x_studio_days`, `x_studio_kind`) sont inchangés : mêmes identifiants externes `lab_seed_*`, mêmes attributs.
- [ ] **C12** Le script de construction rejoué une seconde fois ne crée **aucun doublon** (un seul `ir.model.fields`, un seul `ir.model.data`).
- [ ] **C13** Le pack appliqué une seconde fois ne change rien (`diff` : 0 changement) et ne crée aucun doublon.

## 9. Estimation et découpage

Un seul incrément, indivisible : le champ et son calcul. ~1 h avec la recette.

**Niveau QA** : **normal**. La tâche ne touche ni aux droits, ni à la compta,
ni à la facturation, ni à des données existantes (0 enregistrement). La recette
complète reste à la clôture de la release.

## 10. Ce que l'utilisateur verra

**Rien** dans cette tâche : aucun écran modifié, aucun champ posé sur une vue.
L'indicateur existe côté serveur et attend un écran. À noter pour la clôture :
le guide devra dire que la règle « location ≥ 7 jours » est désormais portée
par la base, et que le champ n'est pas modifiable à la main.
