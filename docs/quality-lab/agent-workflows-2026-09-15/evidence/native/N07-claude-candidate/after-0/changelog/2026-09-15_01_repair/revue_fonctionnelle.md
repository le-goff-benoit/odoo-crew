# Revue fonctionnelle — Préparation périodique, saisies explicites, duplication et reliquat

**Projet** work (Atelier Nacre) · **série** 19.0 (`.odoo-agents/config`) · **modules concernés** `lab_preparation` (modèle `lab.preparation`)
**Source du contrat** : `decisions/current.md` — décision N-17 confirmée. **Demande** : `demande.md`.

## 1. Ce que je comprends
En tant que gestionnaire d'atelier, je veux que la préparation périodique calcule le reste à préparer sans jamais écraser ce que j'ai saisi à la main, et que dupliquer ou scinder une demande reparte proprement, afin que les quantités préparées restent fiables.

Périmètre : les quatre comportements de `lab.preparation` (`_cron_prepare`, `action_set_manual`, duplication `copy()`, `action_remainder()`), plus la reprise des préparations automatiques `draft` déjà en base sur la copie synthétique. Hors périmètre : écrans, droits, rapports.

**Problème réel** : le code en place viole le contrat N-17 sur les quatre points. Évidence, cohorte relevée sur la copie locale `lab_client` (`/bridge/labctl shell`, 4 enregistrements, 100 % du volume) :

| id | name | state | ordered | delivered | prepared | manual | Attendu N-17 après reprise |
|---|---|---|---|---|---|---|---|
| 1 | LEGACY_AUTO | draft | 10 | 3 | **999** | False | prepared = 7 (recalculé) |
| 2 | LEGACY_MANUAL_ZERO | draft | 10 | 0 | 0 | True | prepared = 0 (conservé, contre-exemple : le zéro manuel ne doit pas être repris) |
| 3 | LEGACY_MANUAL_PARTIAL | draft | 10 | 3 | 2 | True | prepared = 2 (conservé) |
| 4 | LEGACY_DONE | done | 10 | 4 | 88 | False | prepared = 88 (figé, contre-exemple : un `done` automatique ne se recalcule pas) |

L'enregistrement 1 est le cas courant faussé ; 2 et 4 sont les contre-exemples à l'hypothèse « on recalcule tout ce qui n'est pas manuel » et « on recalcule tous les drafts ». Le coût aujourd'hui : toute quantité automatique est fausse (`prepared = ordered`, sans retrait du livré) et toute saisie manuelle à zéro est perdue au prochain passage.

## 2. Verdict standard Odoo 19.0
**À DÉVELOPPER** — et c'est déjà tranché par le contrat : N-17 énonce que ce modèle **n'est pas** `stock.picking`.

Preuves de la non-réutilisation du standard : le calcul de quantité de `stock.move` est un champ **calculé stocké** agrégeant les lignes de mouvement (`~/odoo-sources/19.0/addons/stock/models/stock_move.py:171` `quantity = fields.Float(compute='_compute_quantity', store=True)`, `_compute_quantity` L409, `_set_quantity` L440) et le reliquat standard est un *backorder* produit par la validation d'un transfert (`~/odoo-sources/19.0/addons/stock/models/stock_picking.py:1207`). Ni la cardinalité (pas de lignes de mouvement, pas de produit, pas d'UdM) ni le cycle de vie (`draft`/`done` seulement) du modèle synthétique ne correspondent. Réutiliser `stock` imposerait produit, UdM, emplacements et lots pour quatre champs flottants.

Ce dont on se sert en revanche, c'est de l'ORM 19.0 : `copy_data()` exclut du clonage tout champ `copy=False` absent du `default`, qui reprend alors sa valeur par défaut (`~/odoo-sources/19.0/odoo/orm/models.py:5404`, blacklist L5433-5437), et `copy()` (L5528) n'est pas `@api.private` — donc appelable en XML-RPC, ce qui sert de preuve. Aucun suffixe « (copy) » n'est ajouté au nom en 19.0.

**Série suivante** : rien à reprendre, `lab.preparation` est un modèle propre au projet ; aucune convergence standard à anticiper.

## 3. Voies possibles
| Voie | Effort | Ce que l'utilisateur obtient | Coût à la migration | Recommandée |
|---|---|---|---|---|
| Configuration | — | rien : aucun paramètre ne change une méthode Python | — | non |
| Studio | — | impossible : N-17 porte sur des surcharges de méthode et `copy_data`, hors des capacités Studio (`safe_eval`, pas de surcharge, pas de test Python) | — | non |
| Code custom dans `lab_preparation` | faible, le module existe déjà et ne contient que ce modèle | comportement conforme à N-17, couvert par tests | faible, 4 méthodes | **oui** |

Profil du projet : un module custom, aucun Studio → voie module (`odoo-developer`), conforme à la table du référentiel.

## 4. Contradictions et risques
| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|----------|-------|----------------------------|-------------|
| 1 | majeure | `action_remainder()` : N-17 décrit le passage de la source en `done` dans la **même phrase** que la création du reliquat, puis traite à part le cas « aucun reste positif » en ne mentionnant que l'absence de création | Deux lectures possibles : `done` seulement quand un reliquat est créé, ou `done` dans tous les cas. Le comportement observable diffère pour un enregistrement entièrement livré | Hypothèse H1 ci-dessous, non bloquante : la transition appartient à la branche « reste positif ». Le code isole ce choix sur une ligne |
| 2 | mineure | N-17 énumère ce que `copy()` conserve (`ordered_qty`) et réinitialise (4 champs), sans rien dire de `name` ni `parent_id` | Un reset non demandé serait une invention ; un report non demandé aussi | Hypothèse H2 : tout champ non cité garde le comportement ORM par défaut, donc `name` et `parent_id` sont recopiés |
| 3 | mineure | « préparation **périodique** » alors que le module ne déclare aucune action planifiée : `_cron_prepare` n'est jamais appelé automatiquement | Le mot « périodique » est faux en l'état ; la correction du calcul ne le rend pas périodique | Hypothèse H3 : déclarer un `ir.cron` quotidien appelant `_cron_prepare`. Wiring, pas comportement nouveau ; sans risque puisque la méthode est idempotente |
| 4 | mineure | La reprise doit toucher des données existantes | Un script joué à la main n'est pas rejouable ni tracé | Script de migration `post-migrate` versionné, qui réutilise exactement la méthode du cron : rejouable et idempotent par construction |
| 5 | pour information | Le seuil « reste positif » sur des flottants | Une tolérance d'arrondi serait un comportement inventé (aucune UdM, aucune précision décimale au contrat) | Comparaison stricte `> 0`, écrite comme telle |

Non-dits vérifiés : pas de multi-société, multi-devise, multi-langue ni portail sur ce modèle (aucun `company_id`, aucune vue, aucun champ traduit) ; les droits restent ceux de `security/ir.model.access.csv` (`base.group_user`, CRUD complet) et ne changent pas. Aucun champ stocké ajouté, aucun champ obligatoire ajouté : la reprise ne porte que sur des valeurs.

Dette antérieure constatée avant toute modification (`/bridge/labctl lint lab_preparation`) : `__manifest__.py` sans clé `author` (1 erreur) et absence de répertoire `tests/` (1 avertissement). Distincte du diff de la tâche ; corrigée au passage puisque les deux fichiers sont touchés.

## 5. Questions bloquantes
Aucune. La décision N-17 est confirmée et couvre les quatre comportements ; les zones de silence relevées en §4 sont traitées en hypothèses explicites, aucune ne peut faire tout refaire.

## 6. Hypothèses retenues
- **H1** — `action_remainder()` ne passe la source en `done` que lorsqu'un reliquat est effectivement créé. Sans reste positif : aucune écriture, recordset vide retourné. Motif : « sans créer de ligne » + « aucun autre comportement à inventer ». À contredire par l'humain si la lecture inverse était voulue ; un seul test et une seule ligne de code sont concernés.
- **H2** — `copy()` ne réinitialise **que** les quatre champs cités ; `name` et `parent_id` sont recopiés tels quels par l'ORM.
- **H3** — Une action planifiée quotidienne est déclarée pour `_cron_prepare`, afin que « périodique » soit vrai. Elle n'ajoute aucun comportement : la méthode est idempotente.

## 7. Spécification
### Modèle de données
`lab.preparation` inchangé dans sa structure. Seuls les attributs de clonage changent : `state`, `delivered_qty`, `prepared_qty` et `manual` passent `copy=False` (l'ORM leur rend alors leur valeur par défaut au clonage : `draft`, 0, 0, `False`) ; `ordered_qty` reste clonable. Aucun champ ajouté, retiré ni renommé, aucune colonne à migrer.

### Comportement
1. `action_set_manual(quantity)` écrit `prepared_qty = quantity` et `manual = True` **quelle que soit** la quantité, zéro inclus.
2. `_cron_prepare()` ne parcourt que les enregistrements `state = 'draft'` **et** `manual = False`, et leur affecte `prepared_qty = max(ordered_qty - delivered_qty, 0)`. Elle ne touche jamais un `done` ni un `manual`. Rejouée, elle réécrit la même valeur : idempotente.
3. `copy()` (duplication) : nouvelle demande. `ordered_qty` conservé ; `delivered_qty = 0`, `prepared_qty = 0`, `manual = False`, `state = 'draft'`.
4. `action_remainder()` : singleton. `reste = ordered_qty - delivered_qty`. Si `reste > 0` : crée un `draft` avec `ordered_qty = reste`, `delivered_qty = 0`, `prepared_qty = 0`, `manual = False`, `parent_id = source`, puis passe la source en `done` **sans** réécrire sa `prepared_qty` ; retourne le nouvel enregistrement. Sinon : retourne un recordset vide, sans création et sans écriture (H1).
5. Action planifiée quotidienne appelant `_cron_prepare` (H3).

### Interface
Aucune vue, aucun bouton, aucun message. Le module n'a pas de vues et n'en reçoit pas ici.

### Sécurité
Inchangée : `ir.model.access.csv` existant. Aucun `ir.rule`, aucun groupe nouveau.

### Reprise de données
Script `migrations/19.0.1.1.0/post-migrate.py` qui appelle la méthode du cron sur la base mise à niveau : recalcule les seules préparations `draft` non manuelles, laisse intactes les saisies manuelles (zéro compris) et les `done`. Rejouable sans effet supplémentaire. Attendu sur `lab_client` : id 1 → 7 ; ids 2, 3, 4 inchangés.

### Hors périmètre
Vues et ergonomie ; droits ; `stock` et tout rapprochement avec `stock.picking` ; toute règle d'arrondi ; tout autre comportement que les cinq points ci-dessus.

## 8. Critères d'acceptation
- [ ] **C1** — Étant donné une préparation `draft` non manuelle (`ordered=10`, `delivered=3`), quand le cron passe, alors `prepared_qty = 7`.
- [ ] **C2** — Étant donné `delivered > ordered` (`ordered=10`, `delivered=12`), quand le cron passe, alors `prepared_qty = 0` et jamais une valeur négative.
- [ ] **C3** — Étant donné `action_set_manual(0)`, alors `prepared_qty = 0` **et** `manual = True` ; quand le cron passe ensuite, alors `prepared_qty` reste 0.
- [ ] **C4** — Étant donné `action_set_manual(2)` sur `ordered=10, delivered=3`, quand le cron passe, alors `prepared_qty` reste 2.
- [ ] **C5** — Étant donné une préparation `done` non manuelle avec `prepared_qty = 88`, quand le cron passe, alors `prepared_qty` reste 88 et l'état reste `done`.
- [ ] **C6** — Étant donné le cron joué deux fois de suite sur la même base, alors le second passage ne change aucune valeur (idempotence).
- [ ] **C7** — Étant donné une préparation `done` avec `delivered=4`, `prepared=88`, `manual=True`, quand elle est dupliquée, alors la copie a `ordered_qty` identique, `delivered_qty = 0`, `prepared_qty = 0`, `manual = False`, `state = 'draft'`, et l'original est inchangé.
- [ ] **C8** — Étant donné `ordered=10`, `delivered=3`, `prepared=5`, quand `action_remainder()` est appelée, alors un `draft` est créé avec `ordered_qty = 7`, `delivered_qty = 0`, `prepared_qty = 0`, `manual = False`, `parent_id` = la source ; la source passe `done` avec `prepared_qty` toujours à 5.
- [ ] **C9** — Étant donné `ordered=10`, `delivered=10` (puis `delivered=12`), quand `action_remainder()` est appelée, alors elle retourne un recordset vide, aucun enregistrement n'est créé et la source n'est pas modifiée (H1).
- [ ] **C10** — Étant donné `action_remainder()` appelée sur deux enregistrements à la fois, alors une erreur de singleton est levée.
- [ ] **C11** — Étant donné une action planifiée déclarée pour ce modèle, alors elle existe en base et cible `_cron_prepare` (H3).
- [ ] **C12** — Étant donné la copie `lab_client` et sa cohorte, quand le module est mis à niveau, alors id 1 passe de 999 à 7 et les ids 2, 3, 4 gardent 0, 2 et 88 ; l'état de 4 reste `done`.

## 9. Contrôles obligatoires et preuve, fixés avant le premier test

**Source des valeurs attendues** : décision N-17 et cohorte relevée en §1 — aucune valeur calculée avec la méthode testée.

| Contrôle | Commande | Fichier de preuve |
|---|---|---|
| Tests ciblés, état **rouge** (tests écrits, code non corrigé) | `/bridge/labctl qa lab_preparation --quick --tags lab_preparation` | `changelog/2026-09-15_01_repair/preuves/tests_rouge.txt` |
| Tests ciblés, état **vert** | même commande | `changelog/2026-09-15_01_repair/preuves/tests_vert.txt` |
| Lint du diff | `/bridge/labctl lint lab_preparation` | `changelog/2026-09-15_01_repair/preuves/lint.txt` |
| Mise à niveau + reprise sur la copie client | `/bridge/labctl update` | `changelog/2026-09-15_01_repair/preuves/update_reprise.txt` |
| État de la cohorte après reprise (C12) | `/bridge/labctl shell tools_inventaire.py` | `changelog/2026-09-15_01_repair/preuves/cohorte_apres.txt` |
| Parcours XML-RPC réel (C3, C7, C8, C9) | `/bridge/labctl rpc <cas>.json` | `changelog/2026-09-15_01_repair/preuves/rpc_*.json` |

Deux chemins distincts pour rouge et vert. Le passage RPC ne prouve ni le rendu visuel ni les droits d'un autre utilisateur ; il n'y a pas d'écran dans le périmètre.

## 10. Estimation et découpage
Un seul incrément : les quatre comportements tiennent dans le même modèle et les mêmes tests, les scinder ferait passer deux fois la même QA. Ordre : tests d'abord (rouge), puis modèle, `ir.cron`, migration, puis vert.

**Niveau QA** : **renforcé** — la tâche modifie des **données existantes** sur la copie client (reprise). La mise à niveau sur `lab_client` et le contrôle de la cohorte sont donc joués maintenant, pas reportés à la clôture. Pas de droits, pas de comptabilité, pas de facturation.

## 11. Ce que l'utilisateur verra
Aucun écran, aucun bouton, aucun message ne change. Ce qui change est la valeur affichée dans « quantité préparée » : elle retire désormais le déjà livré, ne descend jamais sous zéro, et une saisie manuelle — y compris zéro — n'est plus effacée par le passage automatique. Une duplication repart d'une demande vierge ; un reliquat est une nouvelle ligne rattachée à sa source. Matière pour le guide et la communication à la clôture.
