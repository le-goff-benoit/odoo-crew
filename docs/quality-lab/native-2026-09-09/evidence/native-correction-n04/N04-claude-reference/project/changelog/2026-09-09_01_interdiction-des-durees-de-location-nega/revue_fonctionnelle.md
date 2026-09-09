# Revue fonctionnelle — jours négatifs interdits sur les locations (D-31)

**Projet** Éole (`/work`) · **série** 19.0 (origine `.odoo-agents/config`, confirmée par le manifest `19.0.1.0.0`) · **modules concernés** `lab_rental`

## 1. Ce que je comprends
En tant que gestionnaire de locations, je veux que le système refuse une durée négative afin qu'aucune location ne porte un total inversé.
Périmètre : le seul champ `lab.rental.days`. Le zéro reste valide (location du jour, prêt). `daily_rate` et `amount_total` gardent leur règle actuelle (jours × tarif).
**Problème réel** : la tolérance historique aux durées négatives (journal du 2026-08-01, essais) n'a plus de justification métier ; une durée négative produit un `amount_total` négatif silencieux, sans aucun garde-fou (`lab_rental/models/business.py` : `days = fields.Integer(default=0)`, aucune contrainte).

## 2. Verdict standard Odoo 19.0
**À DÉVELOPPER** — `lab.rental` est un modèle entièrement custom du projet (`lab_rental/models/business.py:6`) ; aucun standard ne porte ce champ ni cette règle. Il n'y a rien à configurer : Odoo n'offre pas de borne déclarative sur un `fields.Integer` hors contrainte.
La forme, en revanche, est du standard pur : la borne sur un entier s'écrit comme dans le standard de la série, `models.Constraint('CHECK(...)', '<message>')` — précédents : `addons/mass_mailing/models/mailing.py:239` (`CHECK(ab_testing_pc >= 0 AND ab_testing_pc <= 100)`), `addons/product/models/product_attribute.py:14`.
**Série suivante** : `models.Constraint` est la forme en vigueur depuis la 19.0 (`odoo/orm/table_objects.py:79`) ; rien ne disparaît en 19.1/19.4. Aucune dette de migration.

## 3. Voies possibles
| Voie | Effort | Ce que l'utilisateur obtient | Coût à la migration | Recommandée |
|---|---|---|---|---|
| Configuration | — | rien : aucun paramètre standard ne borne un entier custom | — | non |
| Studio / configuration en base | ~15 min | une contrainte Python en `safe_eval`, non testable en Python, invisible du dépôt | à reprendre à chaque migration | non |
| Code custom (`models.Constraint` dans `lab_rental`) | ~30 min | refus au niveau de la base, quel que soit le chemin d'écriture (UI, RPC, import, SQL ORM) | nul (forme standard 19.0) | **oui** |

Le profil du projet impose déjà cette voie : un module custom, aucun Studio en base. Et D-31 tranche explicitement le type de contrainte (SQL, pas `@api.constrains`).

## 4. Contradictions et risques
| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|---|---|---|---|
| 1 | mineure | Une contrainte SQL ne s'ajoute pas si des lignes la violent déjà : PostgreSQL refuse l'`ALTER TABLE` et Odoo se contente d'un avertissement au log — le module s'installe, la contrainte est absente | Un déploiement pourrait se croire protégé sans l'être | Vérifié sur la copie `lab_client` : `SELECT count(*) FROM lab_rental WHERE days < 0` → **0**, sur **0** ligne au total (preuve : `.odoo-agents/flow-artifacts/d31-jours-negatifs/inventaire_copie.py`). Aucune reprise nécessaire ici ; la QA de tâche vérifiera que la contrainte est **réellement présente** dans `pg_constraint` après mise à niveau, et non seulement dans le code |
| 2 | mineure | Message d'erreur SQL vs message métier | Une `IntegrityError` brute est illisible pour l'utilisateur | Le second argument de `models.Constraint` porte le message ; il sera renseigné en français, comme le reste du module |
| 3 | mineure | `days` est un `Integer` non `required` : la colonne accepte `NULL`, et `CHECK(days >= 0)` laisse passer `NULL` | Une écriture ORM à `False` ne serait pas rejetée | Sans effet ici : Odoo écrit `0` pour un `Integer` à `False`, et D-31 autorise le zéro. Aucun élargissement du périmètre pour couvrir ce cas théorique |
| 4 | pour mémoire | Aucun écran, aucun droit, aucune vue dans le module | — | Rien à faire : le module n'a pas de vue ; l'utilisateur ne verra que le message de refus |

Aucune contradiction bloquante. La demande est saine et entièrement arbitrée.

## 5. Questions bloquantes
Aucune. Les deux questions ouvertes sont tranchées par D-31 (`decisions/2026-09-08.md`, Luc Roy) : Q1 borne zéro → **incluse (zéro valide)** ; Q2 type de contrainte → **SQL**.

## 6. Hypothèses retenues (à défaut de réponse)
- Le message d'erreur est rédigé en français, comme les libellés existants du module (`_description = 'Location synthétique'`).
- La contrainte porte sur `days` seul ; `daily_rate` négatif reste possible et **hors périmètre** (non arbitré par D-31).

## 7. Spécification
### Modèle de données
`lab.rental` : ajout d'un objet de table `models.Constraint` bornant `days` à `>= 0`. Aucun champ ajouté, modifié ni supprimé. `amount_total` et son `@api.depends` sont inchangés.
### Comportement
Toute création ou modification amenant `days < 0` est refusée par la base ; l'enregistrement n'est pas écrit et l'état antérieur est conservé. `days = 0` reste valide et donne `amount_total = 0`.
### Interface
Aucune. Le module n'a pas de vue ; l'utilisateur voit le message de la contrainte au refus.
### Sécurité
Inchangée. `security/ir.model.access.csv` n'est pas touché — aucun groupe, aucun droit modifié.
### Reprise de données
Aucune : la copie `lab_client` contient 0 ligne `lab_rental` (donc 0 violation). Si une base cible contenait des durées négatives, la contrainte ne s'installerait pas silencieusement — d'où le contrôle `pg_constraint` exigé en QA.
### Hors périmètre
`daily_rate` négatif ; `amount_total` négatif par le tarif ; toute vue, tout droit, toute borne haute sur `days`.

## 8. Critères d'acceptation
- [ ] CA1 — Étant donné une contrainte SQL nommée sur `lab_rental`, quand on inspecte `pg_constraint` après mise à niveau, alors la contrainte `CHECK (days >= 0)` est présente sur la table.
- [ ] CA2 — Étant donné un `lab.rental` à créer, quand `days = -1`, alors la création est refusée (`IntegrityError`) et aucun enregistrement n'est créé.
- [ ] CA3 — Étant donné un `lab.rental` valide, quand on écrit `days = -3`, alors l'écriture est refusée et l'enregistrement conserve sa valeur antérieure (`days` et `amount_total` inchangés).
- [ ] CA4 — Étant donné un `lab.rental`, quand `days = 0`, alors la création passe et `amount_total = 0`.
- [ ] CA5 — Étant donné un `lab.rental` à `days` positif, quand on lit `amount_total`, alors il vaut `days × daily_rate` — le calcul existant est inchangé.

## 9. Estimation et découpage
Un seul incrément : contrainte + tests. ~30 min.
**Niveau QA** : **renforcé** — la règle porte sur des données existantes (durées négatives historiquement tolérées, journal 2026-08-01) et une contrainte SQL peut échouer silencieusement sur une base peuplée. La validation sur la copie `lab_client` est obligatoire tout de suite, sans attendre la clôture.

## 10. Ce que l'utilisateur verra
Aucun écran ne change. Une saisie de durée négative est refusée avec le message « Le nombre de jours d'une location ne peut pas être négatif. » ; une durée de zéro reste acceptée.
