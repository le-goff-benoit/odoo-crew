# Revue fonctionnelle — Indicateur de revue sur les demandes Aster (D-22)

**Projet** work (Association Aster) · **série** 19.0 (origine : `.odoo-agents/config`) · **modules concernés** aucun — configuration en base (`studio_customization`), modèle manuel `x_lab_request`

## 1. Ce que je comprends
En tant que coordinatrice des demandes, je veux qu'une demande signale d'elle-même qu'elle exige une revue, afin de ne plus trier à la main les locations longues.
Périmètre : un seul champ booléen calculé et stocké, `x_studio_needs_review`, sur le modèle manuel existant `x_lab_request`. Aucun écran, aucune automatisation, aucun droit.

**Problème réel** : le tri « faut-il une revue ? » se refait de tête à chaque demande, à partir de deux champs déjà saisis (`x_studio_days`, `x_studio_kind`). La règle est stable et écrite (D-22) : elle peut être portée par la donnée plutôt que par la mémoire. Volume constaté sur la copie `lab_client` : **0 enregistrement** aujourd'hui — le champ naît sur un modèle vide, donc sans reprise de données.

## 2. Verdict standard Odoo 19.0
**À DÉVELOPPER (en configuration)** — mais rien à écrire en Python.

`x_lab_request` est un modèle **manuel** créé en base (`ir.model.state = 'manual'`, source `odoo/addons/base/models/ir_model.py:228`). Aucun modèle standard ne porte cette notion : il n'y a donc pas de fonctionnalité standard à réutiliser, et aucun risque de doubler du standard.

Ce qu'Odoo 19.0 fournit **en base**, et qui suffit :
- champ manuel calculé et stocké : `ir.model.fields.compute` / `depends` / `store` (`ir_model.py:566`, `571`, `574`) ;
- le code du calcul est compilé par `make_compute()` (`ir_model.py:47-52`) et exécuté en `safe_eval` mode `exec` avec `self` en portée ; les boucles et l'affectation par clé (`STORE_SUBSCR`) sont autorisées (`odoo/tools/safe_eval.py:135-155`) ;
- les dépendances sont validées à l'écriture (`_check_depends`, `ir_model.py:733`) : `x_studio_days,x_studio_kind` sont des champs réels du modèle, la contrainte passe ;
- un champ portant un `compute` est automatiquement passé en lecture seule (`_onchange_compute`, `ir_model.py:763`).

**Série suivante** : la mécanique `ir.model.fields.compute` est identique en 19.1/19.4 ; aucune migration à prévoir. `SERIES_MATRIX.md` ne signale d'écart sur ce point ni pour la sécurité (`ir.access.csv` en 19.4) — non concerné ici puisqu'on ne touche pas aux droits.

## 3. Voies possibles
| Voie | Effort | Ce que l'utilisateur obtient | Coût à la migration | Recommandée |
|---|---|---|---|---|
| Configuration pure (filtre enregistré) | 10 min | un filtre `days >= 7 et kind = rental`, pas de donnée | nul | non : la demande veut une **donnée stockée**, filtrable et groupable, pas une vue filtrée |
| **Studio / configuration en base (`odoo-studio`, pack versionné)** | ~1 h | le booléen calculé, stocké, recalculé automatiquement | quasi nul (un champ manuel survit aux montées de version) | **oui** |
| Code custom (module) | ~2 h + module à créer | même résultat | payé à chaque migration | non |

Profil du projet : **0 module custom, du Studio déjà en base** (`studio_customization.lab_seed_*`) → voie Studio par défaut, et l'humain l'a explicitement demandée. Aucune limite de Studio n'est touchée : le calcul est une comparaison de deux champs, sans import, sans réseau, sans JS.

## 4. Contradictions et risques
| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|----------|-------|----------------------------|-------------|
| 1 | Majeure (levée) | D-21 (journal 2026-08-01) dit « revue à 5 jours pour tout le monde » ; D-22 dit « ≥ 7 jours **et** location » | Deux règles incompatibles en mémoire du projet | D-22 (2026-09-08) remplace explicitement D-21. **Retenu : seuil 7 inclus, `loan` exclu.** D-21 est historique, pas à appliquer |
| 2 | Majeure (levée) | Un brouillon de conception demandait un nouveau champ « durée » | Créerait un doublon de `x_studio_days` | Écarté : `x_studio_days` existe (`ir.model.fields` id 3736, XML-ID `studio_customization.lab_seed_x_studio_days`) et est réutilisé tel quel |
| 3 | **Majeure, à arbitrer** | `x_lab_request` n'a **aucun** `ir.model.access` ni `ir.rule` en base (relevé : 0 ligne) | Aucun utilisateur non-superuser — `admin` compris — ne peut lire ni créer un enregistrement du modèle. Un appel XML-RPC `x_lab_request.create` échoue en `AccessError` (« No group currently allows this operation », `ir_model.py:33`). Le scénario de recette au niveau **enregistrement** n'est donc pas jouable en XML-RPC | D-22 et la demande interdisent tout changement de droits. **Retenu : on ne crée pas d'ACL.** Le comportement est prouvé côté serveur via l'ORM (superuser) ; le XML-RPC prouve la définition du champ et l'idempotence du pack. Voir « À décider » du compte-rendu : si le champ doit être exploitable par un humain, une ACL devra faire l'objet d'une demande distincte |
| 4 | Mineure | Champ calculé **stocké** sur un modèle appelé à grossir | Un recalcul de masse coûte à volume élevé | Non bloquant : 0 enregistrement, `depends` limité à deux champs scalaires du même modèle, pas de traversée relationnelle |
| 5 | Mineure | `x_studio_kind` peut être vide, `x_studio_days` vaut 0 par défaut | Une demande incomplète pourrait paraître « à revoir » | La règle est une conjonction : vide ⇒ `False`. Explicité dans les critères |

## 5. Questions bloquantes
Aucune. Les deux questions ouvertes de la décision sont tranchées dans D-22 (Q1 seuil : 7 inclus ; Q2 prêts : exclus).

## 6. Hypothèses retenues (à défaut de réponse)
- Le seuil est **`>= 7`** (7 déclenche la revue, 6 non) — D-22, Q1.
- Seul `x_studio_kind = 'rental'` déclenche ; `'loan'` et valeur vide ne déclenchent jamais — D-22, Q2.
- Le champ est **calculé et stocké**, donc en lecture seule pour l'utilisateur : il n'est pas cochable à la main.
- Aucune ACL n'est créée malgré le constat n°3 (voir ci-dessus).

## 7. Spécification
### Modèle de données
`x_lab_request` — **un seul champ ajouté** :

| Attribut | Valeur |
|---|---|
| `name` | `x_studio_needs_review` |
| `ttype` | `boolean` |
| `field_description` | `Revue requise` |
| `state` | `manual` |
| `store` | `True` |
| `readonly` | `True` |
| `depends` | `x_studio_days,x_studio_kind` |
| `compute` | boucle sur `self`, affectation de la conjonction |
| XML-ID | sous `studio_customization`, créé par Odoo en contexte `studio=True` |

`x_name`, `x_studio_days`, `x_studio_kind` : **inchangés**, ni renommés ni recréés.

### Comportement
`x_studio_needs_review = (x_studio_days >= 7) et (x_studio_kind == 'rental')`, recalculé à la création et à chaque modification de l'un des deux champs sources.

### Interface
**Rien de visible dans cette tâche** : aucune vue n'existe sur `x_lab_request` (0 `ir.ui.view`), aucune n'est créée ni modifiée. Aucune capture requise.

### Sécurité
Aucun changement : ni groupe, ni ACL, ni règle d'enregistrement. Le champ hérite de la sécurité (inexistante) du modèle.

### Reprise de données
Aucune : le modèle est vide. Les enregistrements créés ensuite seront calculés à la création.

### Hors périmètre
Vue, menu, action, automatisation d'envoi, notification, changement de droits, module custom, déploiement staging/production, guide utilisateur.

## 8. Critères d'acceptation
- [ ] C1 — Étant donné une demande `x_studio_days = 7` et `x_studio_kind = 'rental'`, quand elle est créée, alors `x_studio_needs_review` relu depuis le serveur vaut `True` (seuil inclusif, D-22 Q1).
- [ ] C2 — Étant donné une demande `x_studio_days = 30` et `x_studio_kind = 'rental'`, quand elle est créée, alors `x_studio_needs_review` vaut `True`.
- [ ] C3 — Étant donné une demande `x_studio_days = 6` et `x_studio_kind = 'rental'`, quand elle est créée, alors `x_studio_needs_review` vaut `False`.
- [ ] C4 — Étant donné une demande `x_studio_days = 7` et `x_studio_kind = 'loan'`, quand elle est créée, alors `x_studio_needs_review` vaut `False` (prêts exclus, D-22 Q2).
- [ ] C5 — Étant donné une demande `x_studio_days = 30` et `x_studio_kind = 'loan'`, quand elle est créée, alors `x_studio_needs_review` vaut `False`.
- [ ] C6 — Étant donné une demande sans `x_studio_kind` et `x_studio_days = 0`, quand elle est créée, alors `x_studio_needs_review` vaut `False`.
- [ ] C7 — Étant donné une demande à `False`, quand `x_studio_days` passe de 6 à 7, alors le champ stocké est recalculé à `True` sans autre intervention ; et l'inverse (7 → 6) le repasse à `False`.
- [ ] C8 — Étant donné une demande à `True`, quand `x_studio_kind` passe de `rental` à `loan`, alors le champ stocké est recalculé à `False`.
- [ ] C9 — Le champ est en base `boolean`, `state = manual`, `store = True`, `readonly = True`, `depends = x_studio_days,x_studio_kind`, et porte un XML-ID sous `studio_customization` — lu par XML-RPC.
- [ ] C10 — `x_name`, `x_studio_days`, `x_studio_kind` ont les mêmes `id` et les mêmes XML-ID `lab_seed_*` qu'avant la tâche ; aucun champ dupliqué n'existe sur `x_lab_request` (un seul champ dont le nom contient `needs_review`).
- [ ] C11 — Le script de construction et `odoo_pack.py apply` sont **idempotents** : deux applications successives ne créent aucun doublon et le nombre de champs du modèle est identique après la seconde.
- [ ] C12 — `odoo_pack.py diff pack.json` ne rapporte **aucun** écart après application.
- [ ] C13 — Aucun `ir.model.access`, `ir.rule`, `ir.ui.view`, `base.automation`, `ir.actions.server` ni `ir.cron` n'a été créé ou modifié sur `x_lab_request` par la tâche.

## 9. Estimation et découpage
Un seul incrément, indivisible : le champ et son calcul. ~1 h avec le pack et les scénarios.
**Niveau QA** : **normal**. La tâche ne touche ni les droits, ni la comptabilité, ni la facturation, ni des données existantes (modèle vide, aucun champ existant modifié). Le constat n°3 est un état *préexistant* de la copie, pas une modification apportée par la tâche.

## 10. Ce que l'utilisateur verra
**Rien.** Aucune vue n'existe sur ce modèle et aucune n'est créée. Le champ est disponible pour un filtre, un regroupement ou un futur écran, mais rien ne change à l'écran dans cette tâche. Matière pour la clôture : « un indicateur `Revue requise` est désormais calculé automatiquement ; il n'est pas encore affiché ».
