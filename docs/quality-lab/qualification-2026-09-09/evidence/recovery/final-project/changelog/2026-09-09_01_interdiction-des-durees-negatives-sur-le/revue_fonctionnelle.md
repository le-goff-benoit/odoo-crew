# Revue fonctionnelle — Interdire les jours négatifs sur `lab.rental` (D-31)

**Projet** Atelier Boréal (lab synthétique) · **série** 19.0 · **module** `lab_rental`

## 1. Ce que je comprends
En tant que responsable des locations, je veux qu'un enregistrement `lab.rental`
ne puisse jamais porter un nombre de jours négatif (zéro restant autorisé), afin
que le total facturable (`amount_total = days × daily_rate`) reste toujours
cohérent et que la tolérance historique des essais à durée négative disparaisse.

**Périmètre** : ajout d'une contrainte SQL sur `lab.rental.days`, aucune
modification d'écran, de droit, ni de règle de calcul de `daily_rate` /
`amount_total`.

**Contrat déjà arbitré (D-31, 2026-09-08)** — je ne rouvre pas ces points :
- Q1 (borne) : zéro **inclus**, seul le négatif est interdit → `days >= 0`.
- Q2 (mécanisme) : contrainte **SQL** explicitement demandée, pas de
  `@api.constrains` Python.
- A8 : le rejet d'une création `days=-1` doit être **constaté par un vrai
  appel XML-RPC** contre `lab_client`, avec vérification du message et de la
  conservation des données.

## 2. Verdict standard Odoo 19.0
**À DÉVELOPPER** — `lab.rental` est un modèle 100 % custom du module
`lab_rental` (`/work/lab_rental/models/business.py`), sans équivalent standard
(ce n'est ni `sale.order`, ni `product.pricing`, ni un modèle de location
Enterprise). Il n'y a donc rien à configurer côté standard.

Forme confirmée dans les sources 19.0 (pas `_sql_constraints`, obsolète) :
```
~/odoo-sources/19.0/odoo/orm/table_objects.py:79  → class Constraint(TableObject)
~/odoo-sources/19.0/addons/sale/models/sale_order_line.py:20-27  → exemple d'usage
~/odoo-sources/19.0/addons/hr_holidays/models/hr_leave.py:244  → 'CHECK ( number_of_days >= 0 )'
```
Donc :
```python
_days_positive = models.Constraint(
    'CHECK(days >= 0)',
    "Le nombre de jours doit être positif ou nul.",
)
```
**Série suivante** : rien à signaler, la forme `models.Constraint` est déjà la
forme cible depuis 19.0 ; pas de piège de migration ici.

## 3. Voies possibles
Studio est écarté d'emblée : Studio ne pose pas de contrainte SQL (`CHECK`)
sur une table, seule une contrainte Python `safe_eval` limitée serait possible
— or Q2 impose explicitement une contrainte SQL. Voie retenue : **module**
(le seul module custom du projet, déjà en place).

| Voie | Effort | Obtenu | Coût migration | Recommandée |
|---|---|---|---|---|
| Configuration | — | rien : pas de paramètre existant | — | non |
| Studio | incompatible avec Q2 (SQL) | — | — | non |
| Code custom (module) | faible : un `models.Constraint` + tests + QA | contrainte fiable au niveau base, valable pour toute voie d'écriture (UI, import, RPC, code serveur) | quasi nul (forme déjà 19.0) | **oui** |

## 4. Contradictions et risques

| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|----------|-------|----------------------------|-------------|
| 1 | **Majeure** | Message exact (A8) vs transport XML-RPC | Une violation de `CHECK` remonte comme `psycopg2.IntegrityError`. Sur le chemin XML-RPC (`execute_kw`), c'est `odoo/service/model.py:retrying()` qui l'attrape (ligne ~213) et lève `ValidationError(env._("The operation cannot be completed: %s", model._sql_error_to_message(exc)))`. Traduit en français (`odoo/addons/base/i18n/fr.po`), le fault XML-RPC réel sera **« L'opération ne peut pas être terminée : Le nombre de jours doit être positif ou nul. »**, pas le message seul. Une contrainte SQL pure (imposée par Q2/D-31) ne peut pas produire le message nu tel quel sur ce chemin — ce n'est pas un défaut d'implémentation, c'est le comportement standard du noyau. | Écrire le critère A8 comme un test de **contenu** (le message contient exactement la phrase « Le nombre de jours doit être positif ou nul. »), pas d'**égalité stricte** avec le fault complet. Cohérent avec D-31 (SQL) et avec l'intention d'A8 (le texte métier attendu). Je ne rouvre pas Q2 : je documente le format réel constaté. |
| 2 | Mineure | Application de la contrainte à la mise à jour du module | `Constraint.apply_to_database` exécute `ADD CONSTRAINT` sur la table existante à l'`update`. Le journal du projet indique que les durées négatives « étaient anciennement permises pour des essais » : si des lignes négatives existaient encore en base, la mise à jour du module échouerait net (rollback), bloquant le déploiement. La sonde `probe_initial.json` confirme `lab.rental` vide sur `lab_client` **à ce jour** — donc la mise à jour est sûre *maintenant*, mais ce résultat dépend entièrement de l'état courant de la table, pas d'une propriété du code. | Ajouter un critère de mise à jour propre sur données existantes (même si actuellement vides), et documenter dans les notes de version que toute réintroduction de données historiques négatives devra être nettoyée avant mise à jour. |
| 3 | Mineure | `amount_total` déjà cohérent | Le calcul `days * daily_rate` reste correct avec `days = 0` (résultat 0), aucune régression du champ stocké à prévoir. Signalé pour mémoire, ce n'est pas un risque. | — |

## 5. Questions bloquantes
Aucune : Q1 et Q2 sont tranchées par D-31, et le point 1 ci-dessus (format du
message XML-RPC) est un fait technique vérifiable, pas un arbitrage à
demander — il ajuste seulement la formulation du critère A8, pas son intention.

## 6. Hypothèses retenues
- Le message métier attendu est le contenu défini dans `models.Constraint`,
  vérifié comme sous-chaîne du fault XML-RPC (voir risque 1).
- Aucune donnée réelle à reprendre : `lab.rental` est vide sur `lab_client` au
  moment de la revue (preuve : `/work/.odoo-agents/probe_initial.json`).

## 7. Spécification

### Modèle de données
`lab.rental` (existant, `/work/lab_rental/models/business.py`) : ajout d'une
seule contrainte SQL, aucun nouveau champ.
```python
_days_positive = models.Constraint(
    'CHECK(days >= 0)',
    "Le nombre de jours doit être positif ou nul.",
)
```

### Comportement
- `create()` avec `days < 0` → refusée par la base au flush, remontée en
  `ValidationError` côté ORM / `Fault` côté XML-RPC.
- `write()` faisant passer `days` à une valeur `< 0` sur un enregistrement
  existant → même refus.
- `days = 0` → accepté sans particularité.
- `amount_total` reste calculé `days * daily_rate`, sans changement de règle.

### Interface
Aucune (hors périmètre explicite de la demande).

### Sécurité
Aucun changement de droit ; la contrainte s'applique à tout accès en
écriture quel que soit le vecteur (UI, import, RPC, code serveur), c'est une
propriété du schéma, pas des `ir.rule`/`ir.model.access`.

### Reprise de données
Aucune donnée existante à reprendre (table vide sur `lab_client`). La mise à
jour du module doit néanmoins être vérifiée sur la copie pour prouver
qu'`apply_to_database` s'exécute sans erreur dans l'état courant.

### Hors périmètre
Écrans, droits, facturation, mise en production (rappels explicites de la
demande et de D-31).

## 8. Critères d'acceptation

- [ ] Étant donné le module `lab_rental` mis à jour sur `lab_client`, quand on lit le code source du modèle, alors la contrainte `days >= 0` est déclarée via `models.Constraint('CHECK(days >= 0)', ...)` (pas `_sql_constraints`).
- [ ] Étant donné la copie `lab_client`, quand on met à jour le module `lab_rental` (`/bridge/labctl update`), alors la mise à jour se termine sans erreur (aucune ligne existante ne viole `days >= 0`).
- [ ] Étant donné `lab_client` via un appel XML-RPC réel (`/bridge/labctl rpc`), quand on appelle `create` sur `lab.rental` avec `days=-1`, alors l'appel échoue (`Fault`) et le message renvoyé contient exactement la phrase « Le nombre de jours doit être positif ou nul. ».
- [ ] Étant donné un enregistrement `lab.rental` existant valide (`days >= 0`) créé en amont via XML-RPC, quand on appelle `write` dessus avec `days=-1` via XML-RPC réel, alors l'appel échoue avec le même message que le critère précédent, et les valeurs de l'enregistrement (`days`, `daily_rate`, `amount_total`) restent inchangées après l'échec (relecture par `search_read` ou `read`).
- [ ] Étant donné `lab.rental`, quand on crée ou modifie un enregistrement avec `days=0`, alors l'opération réussit (via XML-RPC réel), sans erreur.
- [ ] Étant donné un enregistrement `lab.rental` avec `days` et `daily_rate` quelconques valides, quand on le lit après création ou modification, alors `amount_total == days * daily_rate`.
- [ ] Étant donné une création `lab.rental` valide suivie d'une tentative de `write(days=-1)` refusée sur ce même enregistrement, quand on relit l'enregistrement, alors il existe toujours en base avec ses valeurs d'avant tentative (aucune perte, aucun enregistrement partiel).
- [ ] Étant donné la suite de tests du module, quand on exécute `/bridge/labctl qa lab_rental`, alors tous les tests passent, y compris les scénarios ci-dessus couverts par un vrai appel RPC (pas seulement des appels ORM internes).

## 9. Estimation et découpage
Incrément unique, livrable d'un coup : ajout de la contrainte + tests
(création refusée, écriture refusée, jour zéro accepté, conservation après
rejet, message exact via RPC réel). Pas de découpage utile, la portée est
trop réduite.

**Niveau QA** : **renforcé** — la contrainte touche une donnée existante au
sens strict (schéma appliqué à une table déjà peuplée en usage réel, même si
la copie courante est vide), avec copie client (`lab_client`) obligatoire
pour la preuve RPC d'A8.

## 10. Ce que l'utilisateur verra
Rien de visible à l'écran (pas de vue modifiée). Le seul changement perceptible :
une tentative de saisie ou d'import avec un nombre de jours négatif sera
refusée, avec le message « Le nombre de jours doit être positif ou nul. »
(potentiellement encadré par le texte standard Odoo « L'opération ne peut pas
être terminée : » selon le canal utilisé — RPC direct, formulaire, import).

ISSUE: module_high_risk
