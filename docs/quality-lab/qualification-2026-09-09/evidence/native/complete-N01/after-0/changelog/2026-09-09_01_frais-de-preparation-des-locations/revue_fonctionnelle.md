# Revue fonctionnelle — Frais de préparation des locations (D-02)

**Projet** Atelier Boréal (work) · **série** 19.0 (origine `__manifest__.py`) · **modules concernés** `lab_rental`

## 1. Ce que je comprends

En tant que gestionnaire de locations, je veux que le montant total d'une location intègre
automatiquement le forfait de préparation de 12 EUR, afin de ne plus l'ajouter à la main.

Périmètre : le seul champ `lab.rental.amount_total`, calculé et **stocké**. Pas d'écran, pas de
facturation, pas de droits, pas de comptabilité.

**Problème réel** : le forfait de préparation existe dans la réalité métier mais pas dans le calcul.
Décision D-02 du 08/09/2026, actée par Alice Martin, `decisions/2026-09-08.md`. Elle **remplace**
D-01 (7 % sur toutes les locations) encore présente au journal du 2026-08-01. Le risque principal de
cette demande n'est pas technique, il est de réimplémenter D-01.

## 2. Verdict standard Odoo 19.0

**À DÉVELOPPER** (extension du calcul déjà présent dans le module custom).

Preuves :
- Aucun module de location en Community 19.0 : `ls ~/odoo-sources/19.0/addons | grep -i rent` → vide.
- La location standard est **Enterprise** : `~/odoo-sources/19.0-enterprise/sale_renting/`. Sa
  tarification est portée par `models/product_pricing.py` (`_compute_price(self, duration, unit)`,
  ligne 101) et s'applique à `sale.order.line` — un barème produit par durée, pas un forfait
  conditionnel sur un modèle propriétaire.
- Le modèle visé, `lab.rental` (`lab_rental/models/business.py`), ne dépend que de `base` et porte
  déjà son propre `amount_total` calculé/stocké avec `@api.depends('days', 'daily_rate', 'kind')`.

Adopter `sale_renting` pour un forfait de 12 EUR imposerait Enterprise, `sale`, des produits et des
lignes de commande : hors de proportion, et contraire à « sans facturer ».

**Série suivante** : rien de nouveau côté location dans `19.1`/`19.4` qui rendrait ce calcul
standard ; le point d'extension reste le champ calculé du module. Pas de dette de migration
particulière au-delà du custom lui-même.

## 3. Voies possibles

| Voie | Effort | Ce que l'utilisateur obtient | Coût à la migration | Recommandée |
|---|---|---|---|---|
| Configuration | — | rien : aucun paramètre standard ne porte ce forfait | — | non |
| Studio / base | ~1 h | champ calculé en `safe_eval`, non testable en Python, invisible en revue de code | moyen | non |
| Code custom | ~1 h | règle testée, versionnée, au bon endroit | faible (3 lignes) | **oui** |

Profil du projet : un module custom, aucun Studio → voie module (`odoo-developer`). Le calcul modifie
en plus une méthode `_compute_` existante, ce que Studio ne sait pas surcharger.

## 4. Contradictions et risques

| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|---|---|---|---|
| 1 | **Majeure** | Le journal 2026-08-01 porte encore D-01 (7 % sur toutes les locations) | Une lecture rapide de la mémoire projet ferait implémenter la mauvaise règle | D-02 fait foi ; le tracer dans `PROJECT.md` et couvrir D-01 par un test de non-régression (aucun montant proportionnel) |
| 2 | **Majeure** | `amount_total` est **stocké** : la mise à jour du module recalcule les enregistrements déjà en base | Des valeurs existantes changent sans action utilisateur — c'est un impact sur les données existantes | QA **renforcée** : comptage avant/après sur la copie `lab_client`, et vérification que seules les locations ≥ 4 jours bougent |
| 3 | Mineure | `amount_total` est un `Float`, pas un `Monetary` | Pas de `currency_id` sur le modèle | D-02 fixe une monnaie unique EUR et interdit tout arrondi supplémentaire : `Float` reste correct. Passer en `Monetary` imposerait un champ devise et un écran → **hors périmètre** |
| 4 | Mineure | D-02 dit que `days` et `daily_rate` « restent positives ou nulles » | Tentation d'ajouter une contrainte SQL/Python | C'est une **hypothèse de domaine**, pas une exigence : une contrainte changerait la saisie et donc les écrans. Hors périmètre ; le comportement à 0 est en revanche couvert par un test |
| 5 | Mineure | Non-dits : multi-société, multi-devise, archivage, portail | Aucun de ces axes n'existe sur `lab.rental` (modèle à 5 champs, dépendance `base` seule) | Sans objet, noté pour mémoire |

Aucune contradiction bloquante. Q1 (borne inclusive) et Q2 (prêts) sont tranchées dans
`decisions/2026-09-08.md` : **aucune question bloquante ne subsiste**.

## 5. Questions bloquantes

Aucune.

## 6. Hypothèses retenues (à défaut de réponse)

- Le forfait est un **montant fixe de 12 EUR**, ajouté une seule fois, quelle que soit la durée
  (D-02 : « + 12 EUR », pas « par jour »).
- Le forfait s'ajoute même si `daily_rate` vaut 0, dès lors que `kind = rental` et `days >= 4` :
  D-02 conditionne le forfait au type et à la durée, à rien d'autre.
- Un `days` négatif (hors domaine annoncé) ne déclenche pas le forfait, la borne `>= 4` n'étant pas
  atteinte : comportement dérivé, pas une règle.
- Le seuil et le montant sont écrits comme **constantes nommées** du modèle, pas comme paramètres de
  configuration : D-02 ne demande pas de réglage, et un paramètre serait un écran de plus.

## 7. Spécification

### Modèle de données
Aucun champ ajouté, supprimé ni renommé. `lab.rental.amount_total` reste `Float`, `compute`, `store=True`.

### Comportement
`_compute_amount_total` devient :

```
base = days * daily_rate
amount_total = base + 12.0  si kind == 'rental' et days >= 4
amount_total = base         sinon
```

Le `@api.depends('days', 'daily_rate', 'kind')` existant couvre déjà les trois entrées : inchangé.

### Interface
**Rien.** Aucune vue, aucun menu, aucune action, aucun libellé.

### Sécurité
**Rien.** `ir.model.access.csv` inchangé, aucun groupe, aucune règle d'enregistrement.

### Reprise de données
Le recalcul du champ stocké s'opère à la mise à jour du module (`-u lab_rental`). Aucun script de
migration : les valeurs sont dérivées, pas saisies. À vérifier sur la copie `lab_client` que seules
les locations de 4 jours et plus voient leur montant augmenter de 12, et d'exactement 12.

### Hors périmètre
Facturation, comptabilité, écrans, droits, contrainte de positivité, `Monetary`/`currency_id`,
paramétrage du seuil ou du montant, application rétroactive à des documents historiques.

## 8. Critères d'acceptation

- [ ] Étant donné une location (`kind = rental`) de 4 jours à 10 EUR/jour, quand le montant est calculé, alors `amount_total` vaut 52.0 (borne inclusive, Q1).
- [ ] Étant donné une location de 3 jours à 10 EUR/jour, quand le montant est calculé, alors `amount_total` vaut 30.0 (sous le seuil, pas de frais).
- [ ] Étant donné une location de 7 jours à 10 EUR/jour, quand le montant est calculé, alors `amount_total` vaut 82.0 (au-dessus du seuil, frais appliqués une seule fois).
- [ ] Étant donné un prêt (`kind = loan`) de 4 jours à 10 EUR/jour, quand le montant est calculé, alors `amount_total` vaut 40.0 (prêts exclus, Q2).
- [ ] Étant donné un prêt de 10 jours à 10 EUR/jour, quand le montant est calculé, alors `amount_total` vaut 100.0 (aucun frais quelle que soit la durée).
- [ ] Étant donné une location de 0 jour à 0 EUR/jour, quand le montant est calculé, alors `amount_total` vaut 0.0 (aucun frais sur un enregistrement vide).
- [ ] Étant donné une location de 5 jours à 0 EUR/jour, quand le montant est calculé, alors `amount_total` vaut 12.0 (le forfait ne dépend pas du tarif).
- [ ] Étant donné une location de 3 jours déjà enregistrée, quand `days` passe à 4, alors `amount_total` stocké est recalculé et vaut 52.0 (le champ stocké suit la modification).
- [ ] Étant donné une location de 5 jours, quand `kind` passe à `loan`, alors `amount_total` stocké perd les 12 EUR (le recalcul est symétrique).
- [ ] Étant donné le montant d'une location, quand on le compare à D-01, alors aucun montant proportionnel (7 %) n'apparaît : le forfait est fixe et vaut toujours 12.0.
- [ ] Étant donné la copie `lab_client` après mise à jour du module, quand on compare les montants avant et après, alors seules les locations de 4 jours et plus ont augmenté, et de 12.0 exactement.
- [ ] Étant donné le module après la tâche, quand on l'inspecte, alors aucune vue, aucun droit et aucune dépendance n'ont été ajoutés.

## 9. Estimation et découpage

Un seul incrément, indivisible : la méthode et ses tests. ~1 h.

**Niveau QA** : **renforcé** — le champ est stocké, la mise à jour réécrit des valeurs
d'enregistrements existants (risque n°2). La QA de tâche comprend donc la vérification sur la copie
`lab_client`, en plus du lint et des tests ciblés.

## 10. Ce que l'utilisateur verra

Rien de nouveau à l'écran. Le champ « Montant total » des locations de 4 jours et plus affiche
12 EUR de plus qu'avant, sans explication visible ni ligne de détail. C'est le seul point à
expliquer dans la communication de clôture.
