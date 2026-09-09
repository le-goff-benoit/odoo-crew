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

---

# Point n°2 — Frais de préparation : 15 EUR à partir de 5 jours (D-03)

**Projet** Atelier Boréal (`/work`) · **série** 19.0 (origine : `lab_rental/__manifest__.py`) · **modules concernés** `lab_rental` · **release** `2026-09-09_01` (ouverte)

## 1. Ce que je comprends

Alice Martin a acté **D-03** (`decisions/2026-09-09.md`) : le forfait de préparation passe
à **15 EUR** et ne s'applique plus qu'**à partir de 5 jours inclus**. D-03 **remplace D-02**
(12 EUR à partir de 4 jours), qui a été implémentée et validée ce matin même dans cette
release, au point n°1. Les prêts restent exclus, `jours × tarif_jour` est inchangé.

Le delta réel est donc de **deux constantes et leurs attentes de test** — mais ce n'est pas
un simple ajustement de montant : le **seuil monte**, donc une location de 4 jours qui payait
12 EUR ne paie **plus rien**. Deux changements de sens dans la même release.

**Problème réel** : la release ouverte porte aujourd'hui du code, des tests et un suivi qui
appliquent une règle morte. Si elle était livrée en l'état, le client recevrait D-02.

## 2. Verdict standard Odoo 19.0

**À DÉVELOPPER**, et le raisonnement du point n°1 reste valable sans être rejoué :
`sale_renting` est enterprise (`~/odoo-sources/19.0-enterprise/sale_renting/`), le projet ne
l'utilise pas (`'depends': ['base']`, modèle propre `lab.rental`), et aucun paramètre standard
ne porte un forfait fixe conditionnel. Le point d'extension est le même :
`_preparation_fee()` dans `lab_rental/models/business.py`, déjà isolé pour cette raison au
point n°1. Rien à créer.

**Série suivante** : rien en `19.1` / `19.4` n'affecte un champ calculé stocké custom
(`SERIES_MATRIX.md`).

## 3. Voies possibles

Inchangé : Studio ne surcharge pas une méthode de calcul Python, le champ existe déjà en
code, le module est déjà là. **Voie module**, sans alternative sérieuse. Le code du point n°1
a placé le montant et le seuil dans des constantes nommées et le forfait dans une méthode
dédiée : le changement de règle se fait là, sans toucher au calcul du total.

## 4. Contradictions et risques

| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|----------|-------|----------------------------|-------------|
| 1 | **majeure** | Le point n°1 de la release est marqué **VALIDÉ** pour une règle désormais morte, et le README annonce « 12 EUR à partir de 4 jours » | La clôture lit le suivi du README : elle produirait un guide et une communication client sur D-02. La QA verte du point n°1 ne prouve plus rien sur ce qui sera livré. | Le point n°1 est marqué **REMPLACÉ par D-03** dans le suivi, sans être effacé (sa QA reste une preuve d'historique) ; le point n°2 porte la règle livrable. À la clôture, un seul comportement est décrit : celui de D-03. |
| 2 | **majeure** | Les tests du point n°1 encodent D-02 en dur (52,0 · 112,0) et **passent au vert** aujourd'hui | Des tests verts sur une règle morte donnent une fausse assurance ; ils échoueront pour la bonne raison mais avec de mauvais libellés (« la borne des 4 jours est inclusive ») | Les attentes et les libellés sont réécrits pour D-03, et la nouvelle suite est **prouvée rouge sur l'ancienne formule** avant d'être verte : un test qui n'a jamais échoué ne prouve rien (leçon du point n°1). |
| 3 | **majeure** | Le seuil **monte** : une location de 4 jours perd le forfait (12 → 0) | Ce n'est pas une hausse de tarif, c'est une exonération nouvelle pour une tranche de durée. Un lecteur pressé de D-03 ne retient que « 15 au lieu de 12 ». | Écrit explicitement dans « Ce que l'utilisateur verra » et couvert par un critère d'acceptation dédié (CA2) : 4 jours → 40,0. |
| 4 | mineure | `amount_total` est **stocké** : changer la formule ne recalcule pas les lignes existantes | Une base cible peuplée garderait les totaux D-02 (voire D-01) | Recompté aujourd'hui en SQL sur la copie `lab_client` : **0 enregistrement** (preuve `preuves/etat_lab_client_avant_d03.log`). Sans objet ce jour. La note « à trancher à la clôture » du README reste valable, et vise maintenant D-03. |
| 5 | mineure | Deux règles tarifaires successives dans la **même** release | L'historique de la release peut faire croire à deux évolutions livrables | Une seule évolution est livrée : D-02 → D-03 est une correction interne à la release, pas un incrément client. À dire tel quel dans la communication de clôture. |
| 6 | mineure | Piège d'écriture du seuil | `days > 5` exclurait le 5 jours, `days >= 4` laisserait l'ancien seuil | Constante nommée `PREPARATION_FEE_MIN_DAYS = 5` et comparaison `>=`, couvertes par CA1 et CA2 qui encadrent la borne des deux côtés. |
| 7 | mineure | Droits, compta, facturation, documents historiques | Aucun n'est touché ; le périmètre fermé du projet est inchangé | Niveau QA **normal** (voir §9). |

## 5. Questions bloquantes

Aucune. D-03 tranche le montant (15 EUR), le seuil (5 jours), l'inclusivité (« à partir de
5 jours inclus »), le sort des prêts (exclus) et celui du calcul de base (inchangé).

## 6. Hypothèses retenues (à défaut de réponse)

- Le forfait reste un **montant fixe par location**, pas par jour : D-03 écrit « frais fixes
  de 15 EUR ».
- « à partir de 5 jours inclus » = `days >= 5`.
- Hors taxes, EUR, sans arrondi : `amount_total` reste un `Float` brut (D-03 ne revient pas
  sur ces points de D-02, qui n'étaient pas contestés).
- D-03 s'applique **à partir de cette release**, donc dès le premier calcul suivant la mise à
  niveau ; aucun effet rétroactif n'est demandé sur des engagements passés (et il n'y en a pas).

## 7. Spécification

### Modèle de données
Aucun changement de schéma. `lab.rental.amount_total` reste `Float`, `compute`, `store=True`,
dépendances `days`, `daily_rate`, `kind` inchangées.

### Comportement
`amount_total = days × daily_rate + frais_de_préparation`, où

- `frais_de_préparation = 15,0` si `kind == 'rental'` **et** `days >= 5` ;
- `frais_de_préparation = 0,0` sinon — y compris pour une location de **4 jours** et pour un
  prêt de n'importe quelle durée.

Les deux constantes du module (`PREPARATION_FEE`, `PREPARATION_FEE_MIN_DAYS`) portent les
nouvelles valeurs et les commentaires citent D-03 ; la méthode `_preparation_fee()` garde sa
forme.

### Interface
**Rien de visible ne change.** Aucune vue créée ni modifiée, aucun champ nouveau.

### Sécurité
Inchangée.

### Reprise de données
Néant : `lab_client` contient 0 enregistrement (SQL, 2026-09-09). Le recalcul d'une base
cible peuplée reste porté en « À décider » de la clôture, avec D-03 pour cible.

### Hors périmètre
Facturation, comptabilité, devise, arrondi, contraintes de saisie, écrans, `sale_renting`,
toute reprise de D-01 ou D-02.

## 8. Critères d'acceptation

- [ ] CA1 — Étant donné une location (`kind = 'rental'`) de **5 jours** à 10 EUR/jour, alors `amount_total` vaut **65,0** (borne inclusive).
- [ ] CA2 — Étant donné une location de **4 jours** à 10 EUR/jour, alors `amount_total` vaut **40,0** : l'ancien seuil de D-02 ne s'applique plus.
- [ ] CA3 — Étant donné une location de 3 jours à 10 EUR/jour, alors `amount_total` vaut 30,0.
- [ ] CA4 — Étant donné une location de 10 jours à 10 EUR/jour, alors `amount_total` vaut **115,0** (forfait fixe, non multiplié).
- [ ] CA5 — Étant donné un prêt de 5 jours à 10 EUR/jour, alors `amount_total` vaut 50,0 (prêts exclus à la borne).
- [ ] CA6 — Étant donné un prêt de 10 jours, alors `amount_total` vaut 100,0.
- [ ] CA7 — Étant donné une location de 4 jours, quand `days` passe à 5, alors le forfait de 15 EUR apparaît ; quand `kind` passe à `loan`, il disparaît.
- [ ] CA8 — Étant donné `days = 0` et `daily_rate = 0`, alors `amount_total` vaut 0,0.
- [ ] CA9 — `amount_total` reste stocké : 65,0 est lu en SQL pour une location de 5 jours, sans recalcul.
- [ ] CA10 — Aucun écran, aucun champ, aucune ligne de sécurité modifiés (contrôle par le diff).

## 9. Estimation et découpage

Un seul incrément, ~30 min avec la reprise des tests. Pas de découpage utile.

**Niveau QA** : **normal**. Ni droits, ni comptabilité, ni facturation, ni données existantes
(0 enregistrement recompté ce jour sur `lab_client`). Lint des fichiers touchés,
installation/mise à niveau, tests ciblés du module, et **preuve que les tests mordent**.
La recette complète reste à la clôture.

## 10. Ce que l'utilisateur verra

**Rien de visible ne change** : aucun écran, aucun bouton, aucun message. Deux effets sur les
montants, tous deux à porter dans la communication de clôture :

1. une location de **5 jours et plus** coûte **15 EUR** de plus que `jours × tarif` ;
2. une location de **4 jours** ne porte **plus aucun** frais de préparation.

Les prêts et les locations de 1 à 3 jours sont inchangés. D-02 n'a jamais été livrée : la
communication client ne décrit que D-03.
