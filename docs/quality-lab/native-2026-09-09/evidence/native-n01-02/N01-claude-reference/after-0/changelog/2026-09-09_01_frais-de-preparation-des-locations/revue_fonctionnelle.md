# Revue fonctionnelle — Frais de préparation des locations (D-02)

**Projet** Atelier Boréal (`/work`) · **série** 19.0 (origine : `lab_rental/__manifest__.py`) · **modules concernés** `lab_rental`

## 1. Ce que je comprends

En tant que gestionnaire de locations, je veux que le total d'une location intègre
automatiquement le forfait de préparation, afin que le montant lu sur la fiche
corresponde à la règle tarifaire actée (D-02) sans calcul manuel.

Périmètre : un seul champ calculé stocké, `lab.rental.amount_total`. Pas de nouvel
écran, pas de nouveau champ visible, pas de facturation, pas de comptabilité.

**Problème réel** : la règle tarifaire D-02 existe sur le papier (decisions/2026-09-08.md,
actée par Alice Martin le 08/09) mais le code applique encore `jours × tarif` seul ; le
forfait de 12 EUR est aujourd'hui à la charge de l'humain, donc oublié ou appliqué à tort.
La demande est saine et la décision est complète : Q1 (borne inclusive) et Q2 (prêts
exclus) sont tranchées dans le fichier. Aucune question bloquante.

## 2. Verdict standard Odoo 19.0

**À DÉVELOPPER** (delta minime sur du custom existant).

- Le standard de location d'Odoo est `sale_renting`, qui est **enterprise** :
  `~/odoo-sources/19.0-enterprise/sale_renting/` (absent de `~/odoo-sources/19.0/addons/`).
  Il porte un modèle de tarification par paliers de durée, pas un forfait fixe conditionnel.
- Le projet n'utilise pas `sale_renting` : `lab_rental/__manifest__.py` déclare
  `'depends': ['base']` et définit son propre modèle `lab.rental`
  (`lab_rental/models/business.py`). Basculer sur le standard enterprise serait une
  refonte, sans rapport avec la demande — hors périmètre, mentionné pour mémoire.
- Le point d'extension est donc le calcul existant `_compute_amount_total`, déjà stocké
  et déjà dépendant de `days`, `daily_rate`, `kind` : le delta réel est une addition
  conditionnelle. Rien à créer, rien à réimplémenter.

**Série suivante** : rien dans `19.1` / `19.4` ne rend ce calcul custom obsolète (le
modèle `lab.rental` est propre au projet). `SERIES_MATRIX.md` ne signale aucune
évolution sur les champs calculés stockés qui affecterait ce code.

## 3. Voies possibles

Le projet a un module custom et pas de Studio → voie par défaut **module**. La demande
porte sur une formule de champ calculé stocké : Studio ne sait pas surcharger une méthode
de calcul Python, et le champ existe déjà en code. La voie module est la seule sérieuse.

| Voie | Effort | Ce que l'utilisateur obtient | Coût à la migration | Recommandée |
|---|---|---|---|---|
| Configuration | — | rien : aucun paramètre standard ne porte cette règle | — | non |
| Studio | — | impossible : pas de surcharge de `_compute_amount_total` | — | non |
| Code custom (`lab_rental`) | ~1 h avec tests | total juste, sans rien changer à ses écrans | nul (module déjà maintenu) | **oui** |

## 4. Contradictions et risques

| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|----------|-------|----------------------------|-------------|
| 1 | mineure | D-01 (7 %) figure encore dans `JOURNAL.md` au 2026-08-01 | Une lecture rapide du journal peut faire réimplémenter l'ancienne règle | D-02 remplace D-01, c'est écrit dans la décision ; je le reporte dans « Décisions actées » de `PROJECT.md` |
| 2 | **majeure** | Un champ calculé **stocké** ne se recalcule pas tout seul quand la **formule** change : Odoo ne recalcule que sur variation des dépendances (`days`, `daily_rate`, `kind`) | Des enregistrements déjà en base garderaient l'ancien total après mise à niveau | Vérifié sur la copie `lab_client` : **0 enregistrement** dans `lab_rental` (compte SQL). Aucune reprise nécessaire aujourd'hui. Si une base cible en contient à la livraison, il faut un script `migrations/<version>/post-recompute.py` — à trancher à la clôture, quand le numéro de version de la release est connu. Porté en « À décider ». |
| 3 | mineure | « jours et tarif restent positifs ou nuls » | Tentation d'ajouter une contrainte SQL, ce qui **changerait le comportement à la saisie** — hors demande (« sans changer les écrans ») | Pas de contrainte. C'est une invariante d'entrée, pas une exigence. Un jour négatif reste hors du seuil (`days >= 4` faux) : le forfait ne s'applique pas, comportement testé. |
| 4 | mineure | Multi-société / multi-devise | Non traités par le modèle : `amount_total` est un `Float` sans `currency_id` | Conforme à la décision (« une seule monnaie EUR, aucun arrondi supplémentaire ») : on garde `Float`, sans `float_round`. Ajouter une devise serait un changement de modèle et d'écran. |
| 5 | mineure | Droits d'accès | `ir.model.access.csv` donne tout à `base.group_user` | Inchangé : la demande ne touche pas aux droits, donc pas de niveau QA renforcé à ce titre |

## 5. Questions bloquantes

Aucune. Q1 et Q2 sont tranchées dans `decisions/2026-09-08.md`.

## 6. Hypothèses retenues (à défaut de réponse)

- Le forfait est un **montant fixe par location**, pas par jour : la décision écrit
  « + 12 EUR », sans multiplicateur.
- Le seuil porte sur le champ `days` du modèle, pas sur une durée calculée depuis des dates
  (le modèle n'a pas de dates).
- Hors taxes, EUR, sans arrondi : `amount_total` reste un `Float` brut.
- Reprise des enregistrements existants : néant sur la copie synthétique (0 ligne, prouvé).

## 7. Spécification

### Modèle de données
Aucun changement de schéma. `lab.rental.amount_total` reste `Float`, `compute`, `store=True`,
avec les mêmes dépendances `days`, `daily_rate`, `kind`.

### Comportement
`amount_total = days × daily_rate + frais_de_préparation`, où

- `frais_de_préparation = 12,0` si `kind == 'rental'` **et** `days >= 4` ;
- `frais_de_préparation = 0,0` sinon — y compris pour un prêt de 4 jours ou plus.

Le seuil et le montant sont des constantes nommées du module, pour être lisibles et
réutilisables ; le calcul du forfait est isolé dans une méthode dédiée, surchargeable.

### Interface
**Rien de visible ne change.** Aucune vue n'est créée ni modifiée (le module n'en a aucune) ;
le champ existe déjà et affiche simplement une valeur juste.

### Sécurité
Inchangée. Aucune écriture dans `ir.model.access.csv`, aucun groupe, aucune règle.

### Reprise de données
Néant sur la copie `lab_client` (0 enregistrement, vérifié en SQL). Le recalcul des
enregistrements préexistants d'une éventuelle base cible est porté en « À décider » de la
clôture (voir risque n°2).

### Hors périmètre
Facturation, comptabilité, devise, arrondi, contraintes de saisie, écrans, bascule vers
`sale_renting`, reprise de D-01.

## 8. Critères d'acceptation

- [ ] CA1 — Étant donné une location (`kind = 'rental'`) de 4 jours à 10 EUR/jour, quand elle est enregistrée, alors `amount_total` vaut 52,0 (borne inclusive, Q1).
- [ ] CA2 — Étant donné une location de 3 jours à 10 EUR/jour, alors `amount_total` vaut 30,0 (pas de forfait sous le seuil).
- [ ] CA3 — Étant donné une location de 10 jours à 10 EUR/jour, alors `amount_total` vaut 112,0.
- [ ] CA4 — Étant donné un prêt (`kind = 'loan'`) de 4 jours à 10 EUR/jour, alors `amount_total` vaut 40,0 : les prêts n'ont jamais de frais (Q2).
- [ ] CA5 — Étant donné un prêt de 10 jours, alors `amount_total` ne contient aucun forfait.
- [ ] CA6 — Étant donné une location de 3 jours, quand on porte `days` à 4, alors `amount_total` est recalculé et inclut le forfait ; quand on repasse le `kind` à `loan`, le forfait disparaît.
- [ ] CA7 — Étant donné `days = 0` et `daily_rate = 0`, alors `amount_total` vaut 0,0 (pas de forfait sur une location vide).
- [ ] CA8 — `amount_total` reste stocké : la valeur est lue en SQL sans recalcul.

## 9. Estimation et découpage

Un seul incrément, ~1 h avec les tests. Pas de découpage utile.

**Niveau QA** : **normal**. La tâche ne touche ni aux droits, ni à la comptabilité, ni à la
facturation, ni à des données existantes (0 enregistrement sur la copie). Lint des fichiers
touchés, installation/mise à niveau, tests ciblés du module.

## 10. Ce que l'utilisateur verra

**Rien de visible ne change** : aucun écran, aucun bouton, aucun message. Seule la valeur du
total des locations de 4 jours et plus augmente de 12 EUR. C'est le seul point à porter dans
la communication de clôture.
