# Revue fonctionnelle — action_repair de lab.register (décision B-42)

**Projet** work (Registre Boréal, entièrement synthétique) · **série** 19.0
(origine `.odoo-agents/config`) · **modules concernés** `lab_register`
(`lab.register`, `lab.register.line`)

## Point 1 — action_repair : périmètre, valeurs, préservation des émis

### 1. Ce que je comprends

En tant qu'utilisateur du registre travaillant dans une société donnée, je veux
que le bouton « réparer » renumérote et recalcule **mes brouillons de la société
où je travaille**, afin de remettre le registre d'aplomb sans toucher à ce qui a
déjà été émis ni aux autres sociétés.

Périmètre : la méthode `action_repair` de `lab.register`, plus la reprise des
brouillons déjà présents dans la société initiale de la copie synthétique
`lab_client`. Rien d'autre : ni modèle, ni droits, ni écran.

**Problème réel** : la méthode actuelle
(`lab_register/models/business.py:20-23`) est une réparation globale. Elle fait
`self.sudo().search([])` : elle ignore `self`, ignore l'état, ignore la société
active, passe en `sudo()`, et additionne **toutes** les lignes. Constaté sur la
copie `lab_client` (preuve :
`.odoo-agents/flow-artifacts/repair-b42/inventaire-avant.txt`) : 4
enregistrements, 2 sociétés, dont une référence déjà émise et un brouillon d'une
autre société — les trois seraient écrasés par un seul clic. C'est une perte de
données sur des références émises, pas un défaut cosmétique.

### 2. Verdict standard Odoo 19.0

**À DÉVELOPPER** (correction d'un custom existant). Il ne s'agit pas de
réimplémenter du standard : `lab.register` est un modèle propre au projet
(`lab_register/models/business.py:4`), aucun modèle Odoo ne porte cette
sémantique. Les briques standard utilisées sont celles de l'ORM de la série :

- société active : `env.company` — `odoo/orm/environments.py:214-242` (premier
  de `allowed_company_ids`, sinon `user.company_id`) ;
- sociétés activées : `env.companies` — `odoo/orm/environments.py:245-283` ;
- c'est bien `env.companies.ids` que les règles d'enregistrement exposent sous
  le nom `company_ids` — `odoo/addons/base/models/ir_rule.py:41-49`. La règle
  `register_company` du module laisse donc voir **toutes** les sociétés
  activées : la visibilité ne suffit pas à borner la réparation, il faut filtrer
  explicitement sur `env.company`.

**Série suivante** : rien de propre à 19.0 ici ; `env.company` / `env.companies`
existent identiquement en 19.1 et 19.4. Aucune dette de migration créée.

### 3. Voies possibles

| Voie | Effort | Ce que l'utilisateur obtient | Coût à la migration | Recommandée |
|---|---|---|---|---|
| Configuration | — | rien : c'est une méthode Python fautive | — | non |
| Studio / base | — | Studio ne surcharge pas une méthode Python (`safe_eval`, pas de test Python) ; le projet est déjà un module, aucun Studio | — | non |
| Code custom | ~ une méthode + tests | le comportement arbitré en B-42 | nul (pas de nouveau champ ni de nouveau modèle) | **oui** |

Profil du projet : des modules, aucun Studio → voie module (`odoo-developer`).

### 4. Contradictions et risques

| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|----------|-------|----------------------------|-------------|
| R1 | majeure | `self.sudo()` | `sudo()` fait sauter la règle d'enregistrement : un utilisateur peut écrire dans une société qu'il ne voit pas, et la traçabilité des droits est perdue. B-42 dit « les droits existants restent inchangés » | supprimer `sudo()` ; la méthode s'exécute avec les droits de l'appelant, déjà suffisants (`ir.model.access.csv` : write pour `base.group_user`) |
| R2 | majeure | `search([])` au lieu de `self` | la méthode répare l'univers entier, sélection ignorée | filtrer `self`, pas `search` |
| R3 | majeure | aucune exclusion des `issued` | écrase `sequence`, `snapshot_total` d'une référence émise (id=3 sur la copie : seq 17, total 555.0, ref `ISSUED/005`) | ne garder que `state == 'draft'` |
| R4 | majeure | aucun filtre de société | touche la société 2 (id=4 sur la copie) | filtrer sur `env.company` |
| R5 | majeure | `sum(... for line in record.line_ids)` | inclut les lignes `cancelled=True` ; totaux faux | filtrer `cancelled=False` |
| R6 | moyenne | pas de `state` dans l'écriture | aucun risque tant qu'on n'écrit pas `state` — l'écriture doit rester limitée à `sequence` et `snapshot_total` | n'écrire que ces deux champs |
| R7 | moyenne | `sequence` a `default=10` et le pas passe à 100 | les nouveaux enregistrements restent à 10 tant qu'ils ne sont pas réparés ; B-42 ne demande pas de changer le défaut | laisser le défaut inchangé, hors périmètre (noté §7) |
| R8 | moyenne | ordre de tri | `date_document` peut être égal (id=1 et id=4 partagent 2020-01-01) ; sans `id` en second critère le résultat n'est pas déterministe, donc pas idempotent | tri explicite `date_document, id`, en Python sur `self` filtré |
| R9 | faible | `date_document` requis | pas de `False` à trier dans le modèle ; risque théorique seulement | pas d'action |

**Cohorte examinée sur la copie `lab_client`** (cas courant, ancien/atypique et
contre-exemple à l'hypothèse « tout est en société 1 et en brouillon ») :

| id | société | nom | date | état | seq | total | référence | lignes (qté, prix, annulée) |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 My Company | LEGACY_A_EARLY | 2020-01-01 | draft | 20 | 999.0 | DRAFT-A | (2,10,non) (5,99,**oui**) |
| 2 | 1 My Company | LEGACY_A_LATE | 2020-01-02 | draft | 10 | 123.0 | DRAFT-B | (3,5,non) (5,99,**oui**) |
| 3 | 1 My Company | LEGACY_ISSUED | 2019-01-01 | **issued** | 17 | 555.0 | ISSUED/005 | (3,5,non) (5,99,oui) |
| 4 | **2** Synthetic other company N06 | LEGACY_OTHER | 2020-01-01 | draft | 80 | 666.0 | OTHER/DRAFT | (3,5,non) (5,99,oui) |

Contre-exemples utiles : l'émis (id=3) est **le plus ancien** — un tri global par
date le mettrait en tête et lui volerait la séquence 100 ; le brouillon de la
société 2 (id=4) partage la date du brouillon id=1, ce qui rend le second critère
de tri indispensable. Utilisateurs présents : `n06_operator` (ordinaire, sociétés
autorisées 1 et 2, société principale 1) et `n06_restricted` (ordinaire, société 1
seule).

**Valeurs attendues, dérivées du contrat B-42 et non de la méthode à tester** :
id=1 → `sequence` 100, `snapshot_total` 2×10 = **20.0** ; id=2 → `sequence` 200,
`snapshot_total` 3×5 = **15.0** ; id=3 et id=4 strictement inchangés.

### 5. Questions bloquantes

Aucune. Les deux points qui auraient bloqué sont déjà arbitrés dans
`decisions/current.md` : Q1 (pas 100/200 et non 10/20) et Q2 (aucune
renumérotation ni recalcul des émis).

### 6. Hypothèses retenues

- H1 — « société initiale de la copie » = `res.company` id=1, *My Company*
  (la seule antérieure à la société synthétique N06). Vérifiée à l'inventaire.
- H2 — la reprise se joue avec la société active 1 ; elle consiste à appeler la
  méthode corrigée elle-même sur les brouillons de cette société, et non à
  écrire un script de valeurs en dur : la reprise prouve ainsi le correctif.
- H3 — aucun script de migration (`migrations/`) n'est ajouté : un post-migrate
  s'appliquerait à **toutes** les sociétés de toute base mise à jour, ce que B-42
  interdit explicitement. La reprise reste une opération ciblée sur la copie.

### 7. Spécification

#### Modèle de données
Inchangé. Aucun champ ajouté, retiré ou modifié ; aucun `default` changé
(`sequence` garde `default=10`, cf. R7).

#### Comportement
`lab.register.action_repair(self)` :
1. retient `self.filtered(r.state == 'draft' and r.company_id == self.env.company)` ;
2. trie ce sous-ensemble par `(date_document, id)` croissants ;
3. écrit, pour le n-ième (1-indexé) : `sequence = n * 100` et
   `snapshot_total = Σ quantity × price` sur les lignes dont `cancelled` est faux ;
4. n'écrit aucun autre champ, ne touche aucun autre enregistrement, retourne `True`.

Hors périmètre de l'écriture, par construction : les `issued`, les
enregistrements d'une autre société, les enregistrements absents de `self`.

#### Interface
Rien de nouveau. Aucune vue dans le module (`__manifest__.py` ne déclare que la
sécurité) ; le bouton est appelé par RPC / code.

#### Sécurité
Inchangée : `ir.model.access.csv` et `rules.xml` ne bougent pas. Le `sudo()`
disparaît du code, ce qui **rend** les droits existants effectifs au lieu de les
contourner ; ce n'est pas un changement de droits.

#### Reprise de données
Brouillons existants de la société 1 de la copie `lab_client` (ids 1 et 2),
par appel de la méthode corrigée, société active 1. Rejouée une seconde fois
pour prouver l'idempotence. Aucune autre base, aucun autre environnement.

#### Hors périmètre
Défaut de `sequence` ; écrans et vues ; création d'un nouvel état ; reprise
d'autres sociétés ou d'autres bases ; renumérotation des émis.

### 8. Critères d'acceptation

- [ ] C1 — Étant donné deux brouillons de la société active dont les dates sont
  ordonnées, quand `action_repair` est appelée sur eux, alors ils reçoivent
  `sequence` 100 puis 200 dans l'ordre `date_document, id`.
- [ ] C2 — Étant donné un brouillon portant une ligne `cancelled=True`, quand
  `action_repair` est appelée, alors `snapshot_total` n'additionne que les lignes
  `cancelled=False`.
- [ ] C3 — Étant donné un enregistrement `issued` présent dans `self`, quand
  `action_repair` est appelée, alors ses `state`, `sequence`, `snapshot_total` et
  `reference` sont inchangés au bit près.
- [ ] C4 — Étant donné un utilisateur ordinaire ayant accès à deux sociétés et
  une sélection mixte contenant un brouillon d'une société non active, quand
  `action_repair` est appelée, alors l'enregistrement de l'autre société est
  strictement inchangé.
- [ ] C5 — Étant donné une date `date_document` identique entre deux brouillons,
  quand `action_repair` est appelée, alors l'ordre est départagé par `id`.
- [ ] C6 — Étant donné un appel déjà effectué, quand `action_repair` est
  rappelée sur la même sélection, alors aucune valeur ne change (idempotence).
- [ ] C7 — Étant donné un utilisateur ordinaire (`base.group_user`, sans
  `base.group_system`), quand il appelle `action_repair`, alors l'appel aboutit
  avec ses propres droits, sans `sudo()`.
- [ ] C8 — Étant donné la copie `lab_client` après reprise, alors id=1 porte
  `sequence` 100 / `snapshot_total` 20.0, id=2 porte 200 / 15.0, id=3 porte
  toujours issued / 17 / 555.0 / `ISSUED/005`, et id=4 toujours 80 / 666.0.
- [ ] C9 — Le test qui couvre C1→C6 est **rouge sur le code d'avant** et vert
  après correction ; la trace des deux exécutions est conservée.

### 9. Estimation et découpage

Un seul incrément, indivisible : la méthode et ses tests. La reprise suit
immédiatement, une fois le test vert.

**Niveau QA** : **renforcé**, obligatoire — la tâche touche les droits (retrait
de `sudo()`), le multi-société et des **données existantes** de la copie. La
copie `lab_client` est donc incluse dans la QA de tâche, sans attendre la
clôture.

### 10. Ce que l'utilisateur verra

Rien de nouveau à l'écran. Le bouton « réparer » existant cesse de renuméroter
les références déjà émises et les enregistrements des autres sociétés ; les
séquences produites deviennent 100, 200, … au lieu de 10, 20, … Matière pour la
communication de clôture, pas de guide pendant la release.
