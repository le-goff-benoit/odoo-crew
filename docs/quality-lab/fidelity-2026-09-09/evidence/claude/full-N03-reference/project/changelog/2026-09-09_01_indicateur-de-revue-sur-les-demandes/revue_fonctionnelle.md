# Revue fonctionnelle — Indicateur `x_studio_needs_review` sur `x_lab_request`

**Projet** /work · **série** 19.0 · **modèle concerné** `x_lab_request` (modèle manuel, `ir.model` id 422, XML-ID `studio_customization.lab_seed_model`) · **aucun module custom**

## 1. Ce que je comprends

En tant que coordinatrice des demandes, je veux que chaque demande porte un indicateur automatique « à revoir » afin de repérer sans calcul manuel les locations longues qui exigent une revue.

Périmètre : un seul champ booléen calculé **stocké**, `x_studio_needs_review`, sur `x_lab_request`, dépendant de `x_studio_days` et `x_studio_kind`. Aucun écran, aucune automatisation, aucun droit, aucun déploiement.

**Problème réel** : la règle D-22 (revue si ≥ 7 jours **et** type location) est aujourd'hui appliquée de tête ; la règle a déjà changé une fois (D-21 : 5 jours pour tous), et le journal montre que l'ancienne règle circule encore. Matérialiser la règle dans un champ stocké la rend filtrable, groupable et surtout **unique** : une seule définition à corriger au prochain arbitrage. La demande est saine et déjà cadrée ; l'essentiel de la revue tient donc dans les hypothèses et les critères.

## 2. Verdict standard Odoo 19.0

**À DÉVELOPPER — mais en configuration pure, sans code de module.**

Il n'existe aucun champ standard « needs review » sur un modèle de demande de location/prêt : `x_lab_request` est un modèle **manuel** propre au client (`ir.model.state = 'manual'`), il n'hérite d'aucun mixin standard. Rien à réutiliser côté `sale_renting` / `stock` : le modèle métier n'est pas celui d'Odoo.

En revanche, **le mécanisme demandé est du standard 19.0 à part entière**, et n'exige aucune ligne de Python dans un module :

- `~/odoo-sources/19.0/odoo/addons/base/models/ir_model.py:566` — `compute = fields.Text(...)` : code de calcul porté par l'enregistrement `ir.model.fields`.
- `ir_model.py:571` — `depends = fields.Char(...)` : dépendances en liste séparée par virgules.
- `ir_model.py:574` — `store = fields.Boolean(string='Stored', default=True)` : le champ calculé manuel **peut** être stocké, et l'est par défaut.
- `ir_model.py:47-52` — `make_compute(text, deps)` fabrique la méthode : `safe_eval(text, SAFE_EVAL_BASE | {'self': self}, mode="exec")` puis `api.depends(*deps)`. C'est exactement le comportement d'un `@api.depends` Python, recalcul et invalidation compris.
- `ir_model.py:1351-1353` — au chargement du registre, `attrs['compute'] = make_compute(field_data['compute'], field_data['depends'])`.
- `ir_model.py:733-760` — `_check_depends` valide à l'écriture que chaque nom de `depends` existe réellement : une faute de frappe sur `x_studio_days` est refusée immédiatement, pas au premier recalcul.
- `ir_model.py:763-765` — `_onchange_compute` force `readonly = True` dès qu'un `compute` est saisi : le champ ne sera pas modifiable à la main. C'est conforme à D-22 (indicateur dérivé, pas saisi) — à acter, ce n'est pas un défaut.

Environnement d'exécution du calcul : `safe_eval` avec pour seuls globaux `datetime`, `dateutil`, `time` et `self` (`ir_model.py:39-44`, `~/odoo-sources/19.0/odoo/tools/safe_eval.py`). La règle D-22 est une comparaison d'entier et une égalité de chaîne : elle tient largement dans cette enveloppe. **Aucune limite de Studio n'est atteinte par cette demande** (pas de JS, pas de surcharge de méthode, pas d'appel à un service externe).

**Série suivante** : le trio `compute` / `depends` / `store` sur `ir.model.fields` est un mécanisme de socle, stable de 17.0 à 19.4 ; il n'est ni déprécié ni remplacé. Aucun risque de migration lié au mécanisme. Le seul coût de migration est celui, normal, de tout champ Studio : il voyage dans `studio_customization`.

## 3. Voies possibles

| Voie | Effort | Ce que l'utilisateur obtient | Coût à la migration | Recommandée |
|---|---|---|---|---|
| Configuration seule (filtre / domaine sauvegardé « ≥ 7 j et location ») | très faible | une vue filtrée, mais **aucun champ** : pas de groupement, pas de dépendance possible, règle dupliquée dans chaque filtre | nul | non — ne répond pas à D-22 qui demande un indicateur |
| **Studio / configuration en base** (`odoo-studio`, pack versionné) | faible | le champ booléen stocké, filtrable et groupable, recalculé automatiquement | faible : un champ manuel dans `studio_customization`, aucun code à reprendre | **oui** |
| Code custom (module Python) | moyen | résultat fonctionnellement identique | à chaque montée de version : manifest, lint, tests, revue | non |
| Automatisation `base_automation` écrivant un booléen simple | faible | valeur figée si la source change hors déclencheur, désynchronisations silencieuses | moyen | non — un calculé stocké fait mieux et sans dérive |

**Voie retenue : Studio.** Le profil tranche seul : **aucun module custom dans le projet**, Studio installé (`web_studio` : `installed`) et déjà porteur de l'existant (`x_name`, `x_studio_days`, `x_studio_kind` sous XML-ID `studio_customization.lab_seed_*`). Introduire un premier module Python pour un booléen dérivé créerait une seconde voie de personnalisation sur le même modèle — c'est exactement le défaut de conception que la table de profils cherche à éviter. La demande explicite « pas de module custom » va dans le même sens.

**Limites de Studio applicables ici, annoncées avant de faire** : le calcul s'exécute en `safe_eval` (pas d'import, pas d'accès aux attributs privés) ; pas de test Python automatisé sur le champ — la preuve sera un scénario RPC rejouable sur la copie ; le champ sera `readonly` par construction.

## 4. Contradictions et risques

| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|---|---|---|---|
| 1 | majeure | **D-21 (5 jours, tous types) contre D-22 (7 jours, location seule)** — D-21 est encore citée dans `/work/.odoo-agents/JOURNAL.md` | Implémenter 5 jours, ou oublier l'exclusion des prêts, produit un indicateur faux et invisible (aucun message d'erreur) | D-22 fait foi (`/work/decisions/2026-09-08.md`, Nora Petit, remplace explicitement D-21). Le seuil **7 est inclus**, les prêts sont exclus **quelle que soit la durée**. Verrouillé par la table de vérité en §8 |
| 2 | mineure | Le brouillon de conception initial demandait **un nouveau champ durée** | Recréer une durée doublonnerait `x_studio_days` et scinderait la donnée | Écarté : `x_studio_days` (id 3736) existe et est la source. Confirmé par le journal du 2026-08-01 |
| 3 | mineure | **Valeurs réelles de `x_studio_kind`** | Un littéral fautif (`'Rental'`, `'location'`) rendrait l'indicateur toujours faux, sans erreur | Vérifié en base : exactement deux valeurs techniques, `rental` (libellé « Location ») et `loan` (« Prêt »). La comparaison porte sur `rental`, pas sur le libellé |
| 4 | mineure | **`x_studio_days` vide ou négatif** | Un entier Odoo non renseigné vaut `0`, jamais `False` : pas de plantage, mais le comportement doit être décidé, pas subi | `0` et les négatifs sont `< 7` → indicateur faux. Aucune garde supplémentaire, aucune contrainte ajoutée (hors périmètre) |
| 5 | mineure | **`x_studio_kind` non renseigné** (`False`) | `False != 'rental'` → faux ; comportement correct mais non écrit | Acté : type absent = pas de revue |
| 6 | mineure | **Recalcul du stocké sur l'existant** | Un champ stocké ajouté sur un modèle peuplé exige un recalcul initial ; c'est le piège classique | **Vérifié : `x_lab_request` contient 0 enregistrement** sur la copie (`search_count` = 0). Aucune reprise de données à faire. Les scénarios devront donc **créer leurs propres jeux d'essai** |
| 7 | mineure | **Doublon de champ à la seconde application du pack** | Deux `ir.model.fields` homonymes casseraient le modèle | Impossible en base : `UNIQUE(model, name)` — `~/odoo-sources/19.0/odoo/addons/base/models/ir_model.py:649`. L'idempotence tient au XML-ID (`studio_customization.*`) : la seconde application doit **mettre à jour**, pas insérer. À prouver, pas à supposer (critère §8) |
| 8 | mineure | Nom du champ | `CHECK (state != 'manual' OR name LIKE 'x\_%')` — `ir_model.py:651-654` | `x_studio_needs_review` est conforme |
| 9 | pour information | **Multi-société / archivage / droits** | Souvent des non-dits coûteux | Sans objet ici : le modèle n'a **ni `company_id` ni `active`** (relevé des champs). Une seule ACL, `base.group_user`, RWCU complets (`ir.model.access` id 295) — **non modifiée** par cette tâche |
| 10 | pour information | Le champ sera `readonly` (`ir_model.py:763-765`) | Une écriture directe sur `x_studio_needs_review` sera ignorée ou refusée | Conforme à D-22. À ne pas confondre avec un échec lors des essais RPC |

Aucune contradiction bloquante. La demande est mûre : **zéro question bloquante**, on avance sur hypothèses.

## 5. Questions bloquantes

Aucune. D-22 tranche explicitement les deux points qui l'auraient été (Q1 seuil : 7 inclus ; Q2 prêts : exclus).

## 6. Hypothèses retenues (à défaut de réponse)

- **H1** — D-22 seule fait foi ; D-21 (5 jours) est morte et ne doit apparaître nulle part dans le calcul.
- **H2** — Seuil `>= 7`, **7 inclus**.
- **H3** — Seul le type technique `rental` déclenche la revue ; `loan` et l'absence de type ne la déclenchent **jamais**, quelle que soit la durée.
- **H4** — `x_studio_days` à `0` (non renseigné) ou négatif → indicateur faux, sans erreur ni contrainte ajoutée.
- **H5** — Le champ est **stocké** (`store = True`) et **readonly** ; il ne s'écrit pas à la main.
- **H6** — Aucune reprise de données : le modèle est vide sur la copie. Les jeux d'essai sont créés par les scénarios et n'engagent pas de données métier réelles.
- **H7** — Le pack Studio est versionné dans le projet et rejouable ; l'identité du champ repose sur un XML-ID stable sous `studio_customization`, ce qui rend la seconde application idempotente.
- **H8** — Travaux sur la copie locale `lab_client` uniquement. Aucun déploiement, aucune écriture sur une instance déclarée.

## 7. Spécification

### Modèle de données

Sur `x_lab_request`, **un seul** nouveau champ manuel :

| Attribut | Valeur |
|---|---|
| `name` | `x_studio_needs_review` |
| `ttype` | `boolean` |
| `field_description` | « À revoir » (libellé métier) |
| `store` | `True` |
| `depends` | `x_studio_days,x_studio_kind` |
| `compute` | règle D-22, en `safe_eval` (`mode="exec"`), itérant sur `self` |
| `state` | `manual` |
| XML-ID | sous `studio_customization`, stable entre deux applications |

Les champs `x_name` (3734), `x_studio_days` (3736), `x_studio_kind` (3738) et leurs XML-ID `lab_seed_*` (`noupdate`) sont **inchangés** : ni renommés, ni recréés, ni retypés, ni vus modifier leurs valeurs de sélection.

### Comportement

Table de vérité D-22, faisant foi :

| `x_studio_kind` | `x_studio_days` | `x_studio_needs_review` |
|---|---|---|
| `rental` | 6 (ou moins, y compris 0 et négatif) | **faux** |
| `rental` | 7 | **vrai** |
| `rental` | 8 et plus | **vrai** |
| `loan` | 7, 8, ou plus | **faux** |
| `loan` | 6 ou moins | **faux** |
| non renseigné | quelconque | **faux** |

Le calcul est **stocké et recalculé automatiquement** à toute modification de l'un des deux champs sources, à la création comme à l'écriture, via le `depends` déclaré (`ir_model.py:47-52`).

### Interface

**Aucune modification.** Pas de vue créée ni héritée, pas d'ajout au formulaire, à la liste, aux filtres ou au groupement. Le champ existe en base et via RPC ; il sera exposé à l'écran dans une tâche ultérieure, sur demande.

### Sécurité

**Aucune modification.** L'ACL existante (`ir.model.access` id 295, `base.group_user`, RWCU) reste telle quelle. Aucune règle d'enregistrement, aucun groupe créé, aucun `groups` posé sur le champ.

### Reprise de données

**Aucune.** `x_lab_request` est vide (0 enregistrement, vérifié). L'ajout de la colonne et le recalcul initial sont sans effet sur des données métier. Si le pack devait plus tard être appliqué sur une base peuplée, le recalcul initial du stocké est assuré par le mécanisme standard et devra être vérifié à ce moment-là.

### Hors périmètre

- Toute vue, tout écran, tout filtre, tout groupement, toute capture.
- Toute automatisation, en particulier tout envoi de courriel ou notification (`base_automation` est installé — on n'y touche pas).
- Toute modification de droits, de groupes ou de règles d'accès.
- Tout module custom, tout code Python de module.
- Tout déploiement, toute écriture sur une instance déclarée : la copie `lab_client` seule.
- Toute modification des champs existants et de leurs XML-ID `lab_seed_*`.
- Toute contrainte de saisie sur `x_studio_days` (bornes, obligation).
- Tout guide utilisateur ou communication client (réservés à la clôture de release).

## 8. Critères d'acceptation

- [ ] Étant donné le pack Studio appliqué sur `lab_client`, quand je lis `ir.model.fields` pour `model = 'x_lab_request'` et `name = 'x_studio_needs_review'`, alors j'obtiens **exactement un** enregistrement, de `ttype = 'boolean'`, `state = 'manual'` et `store = True`.
- [ ] Étant donné ce champ, quand je lis ses attributs `depends`, alors il dépend des deux champs sources `x_studio_days` et `x_studio_kind`, et de rien d'autre.
- [ ] Étant donné une demande créée avec `x_studio_kind = 'rental'` et `x_studio_days = 6`, quand je relis `x_studio_needs_review`, alors il vaut **faux**.
- [ ] Étant donné une demande créée avec `x_studio_kind = 'rental'` et `x_studio_days = 7`, quand je relis `x_studio_needs_review`, alors il vaut **vrai** (seuil inclus, D-22 Q1).
- [ ] Étant donné une demande créée avec `x_studio_kind = 'rental'` et `x_studio_days = 12`, quand je relis `x_studio_needs_review`, alors il vaut **vrai**.
- [ ] Étant donné une demande créée avec `x_studio_kind = 'loan'` et `x_studio_days = 7`, quand je relis `x_studio_needs_review`, alors il vaut **faux** (prêts exclus, D-22 Q2).
- [ ] Étant donné une demande créée avec `x_studio_kind = 'loan'` et `x_studio_days = 30`, quand je relis `x_studio_needs_review`, alors il vaut **faux**, ce qui prouve que l'exclusion des prêts ne dépend pas de la durée.
- [ ] Étant donné une demande créée avec `x_studio_kind = 'rental'` et sans `x_studio_days` renseigné, quand je relis `x_studio_needs_review`, alors il vaut **faux** et la création n'a levé aucune erreur.
- [ ] Étant donné une demande à `x_studio_kind = 'rental'` et `x_studio_days = 6` (indicateur faux), quand j'écris `x_studio_days = 9`, alors `x_studio_needs_review` passe à **vrai** sans autre action (recalcul sur la source durée).
- [ ] Étant donné une demande à `x_studio_kind = 'rental'` et `x_studio_days = 9` (indicateur vrai), quand j'écris `x_studio_kind = 'loan'`, alors `x_studio_needs_review` repasse à **faux** (recalcul sur la source type).
- [ ] Étant donné une demande à `x_studio_kind = 'loan'` et `x_studio_days = 9` (indicateur faux), quand j'écris `x_studio_kind = 'rental'`, alors `x_studio_needs_review` passe à **vrai**.
- [ ] Étant donné des demandes créées avant l'application du pack ou lues par une session neuve, quand j'interroge `x_lab_request` par `search` sur le domaine `[('x_studio_needs_review', '=', True)]`, alors la recherche aboutit sans erreur et ne renvoie que les locations à 7 jours ou plus, ce qui prouve que la valeur est bien **stockée en colonne** et non calculée à la volée.
- [ ] Étant donné le pack déjà appliqué une fois, quand je l'applique une **seconde** fois, alors l'opération réussit et `ir.model.fields` ne contient toujours qu'**un seul** `x_studio_needs_review` sur `x_lab_request` (aucun doublon).
- [ ] Étant donné cette seconde application, quand je compare l'`id` de `ir.model.fields` de `x_studio_needs_review` avant et après, alors il est **identique** (mise à jour par XML-ID, pas suppression/recréation), et les valeurs déjà calculées sur les enregistrements d'essai sont inchangées (idempotence).
- [ ] Étant donné la seconde application du pack, quand je relis les `id` et les attributs (`name`, `ttype`, `store`, `required`) des champs `x_name` (3734), `x_studio_days` (3736) et `x_studio_kind` (3738), alors ils sont **strictement inchangés** par rapport au relevé initial.
- [ ] Étant donné le champ `x_studio_kind`, quand je relis ses valeurs de sélection, alors elles sont toujours exactement `rental` et `loan`, dans le même ordre, aucune valeur n'ayant été ajoutée ni renommée.
- [ ] Étant donné l'ACL `ir.model.access` id 295 sur `x_lab_request`, quand je la relis après application, alors son groupe et ses quatre permissions sont **inchangés**, et aucune autre ACL ni règle d'enregistrement n'a été créée sur ce modèle.
- [ ] Étant donné le périmètre annoncé, quand je recherche les `ir.ui.view` et les `base.automation` portant sur `x_lab_request`, alors le pack n'en a créé ni modifié **aucun**.

## 9. Estimation et découpage

Un seul incrément, non sécable utilement : le champ et son calcul forment l'unité livrable minimale.

1. Pack Studio versionné ajoutant `x_studio_needs_review` (booléen, stocké, `depends` sur les deux sources, `compute` D-22) sous XML-ID stable — livrable unique.
2. Scénarios RPC rejouables sur `lab_client` couvrant la table de vérité, le recalcul, le stockage et les non-régressions.
3. Double application du pack et contre-vérification d'idempotence.

Effort : faible (moins d'une demi-journée, essais compris).

**Niveau QA : normal.** La tâche ne touche ni les droits (ACL inchangée), ni la comptabilité, ni la facturation, ni des données existantes (modèle vide). Elle reste néanmoins **prouvée sur la copie client** `lab_client` : le passage RPC ne démontre ni le rendu visuel ni les droits d'un autre utilisateur, ce qui est sans conséquence ici puisque ni écran ni droit ne changent. Point de vigilance QA : un `Fault` RPC quelconque ne vaut pas preuve — chaque scénario doit vérifier la valeur attendue et les postconditions.

## 10. Ce que l'utilisateur verra

**Rien.** Aucun écran, aucun bouton, aucun message ne change dans cette tâche. Le champ existe en base et sera exploitable par filtre ou groupement, mais il n'est ajouté à aucune vue : un utilisateur qui ouvre une demande de location verra exactement la même fiche qu'avant. Aucune formation, aucune communication, aucune capture n'est requise pour cette livraison. L'exposition à l'écran de l'indicateur « À revoir » fera l'objet d'une demande distincte, qui sera alors le vrai moment de la communication client.

VERDICT: studio
