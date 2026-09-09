# Revue fonctionnelle — Point 2 : frais de préparation révisés (D-03)

**Projet** Atelier Boréal (work) · **série** 19.0 (origine `__manifest__.py`) · **release**
`2026-09-09_01_frais-de-preparation-des-locations` (point n°2) · **modules concernés** `lab_rental`

> Le point 1 de cette release a été réalisé et validé sous **D-02** (12 EUR à partir de 4 jours).
> **D-03 remplace D-02** dans la même release : le point 1 ne décrit donc plus l'état livré. Sa revue
> (`revue_fonctionnelle.md`) et ses preuves restent au dossier **telles quelles**, comme historique,
> mais leurs valeurs attendues sont **périmées**. Ce fichier est la spec qui fait foi pour la release.

## 1. Ce que je comprends

Alice Martin a acté **D-03** le 09/09/2026 (`decisions/2026-09-09.md`) : le forfait de préparation
passe de **12 EUR à partir de 4 jours** à **15 EUR à partir de 5 jours inclus**. Les prêts restent
exclus quelle que soit la durée ; `jours × tarif_jour` est inchangé ; le forfait reste **fixe**.

Périmètre identique au point 1 : le seul champ `lab.rental.amount_total`, calculé et **stocké**.
Pas d'écran, pas de facturation, pas de droits, pas de comptabilité.

**Ce qui change réellement**, et qui n'est pas une simple retouche de deux constantes :

- une location de **4 jours perd son forfait** : son montant **baisse** de 12 EUR. C'est le premier
  changement de cette release qui fait *diminuer* une valeur déjà écrite en base ;
- la copie `lab_client` porte **déjà** les montants D-02 (52.0, 152.0, 12.0 — voir
  `.odoo-agents/flow-artifacts/frais-preparation/copie_client_apres.txt`). Le point de départ de la
  reprise n'est donc pas l'état d'origine, c'est l'état D-02 ;
- le module y est installé en **19.0.1.1.0** : le script `migrations/19.0.1.1.0/post-migrate.py` ne
  sera **pas rejoué**. Sans nouvelle version, la copie resterait sur les montants D-02.

## 2. Verdict standard Odoo 19.0

**À DÉVELOPPER**, pour les mêmes raisons qu'au point 1 et sans élément nouveau : aucun module de
location en Community 19.0, la location standard est Enterprise (`sale_renting`, barème produit par
durée sur `sale.order.line`), et `lab.rental` porte déjà son propre calcul stocké. Changer un seuil
et un montant dans une méthode `_compute_` custom ne devient pas standard parce que la règle change.

**Non, on ne paramètre pas.** La tentation est réelle : deux décisions en deux jours sur le même
forfait suggèrent d'exposer seuil et montant en `ir.config_parameter` ou sur `res.company`. C'est
resté explicitement **hors périmètre** au point 1 (note du 09/09/2026), et D-03 ne le demande pas :
un paramètre ajouterait un écran de réglage, une valeur par défaut à migrer et une règle qui
n'apparaît plus dans le code. À rouvrir sur demande du client si une **troisième** révision arrive —
c'est la remarque à porter au compte-rendu, pas une décision à prendre ici.

## 3. Voies possibles

| Voie | Effort | Ce que l'utilisateur obtient | Coût à la migration | Recommandée |
|---|---|---|---|---|
| Configuration | — | rien : aucun paramètre standard ne porte ce forfait | — | non |
| Studio / base | ~1 h | champ calculé en `safe_eval`, non testable, et **aucune reprise de données** possible | élevé | non |
| Code custom | ~1 h | deux constantes, la reprise versionnée, les tests réécrits sur D-03 | faible | **oui** |

Profil du projet inchangé : un module custom, aucun Studio → `odoo-developer`.

## 4. Contradictions et risques

| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|---|---|---|---|
| 1 | **Majeure** | La copie `lab_client` a le module en **19.0.1.1.0** ; le dossier `migrations/19.0.1.1.0/` ne sera pas rejoué | Un simple `-u` laisserait les montants D-02 en base : vert en test, faux chez le client — exactement le piège déjà payé au point 1 | Monter le manifest en **19.0.1.2.0** et créer `migrations/19.0.1.2.0/post-migrate.py`. Conserver le dossier 19.0.1.1.0 : un client encore en 19.0.1.0.0 traversera les deux, tous deux idempotents |
| 2 | **Majeure** | Les montants **baissent** pour les locations de 4 jours (52.0 → 40.0) | Une reprise écrite comme « ajouter le forfait » ne sait pas retirer ; il faut recalculer, pas ajuster | La reprise reste un `add_to_compute` qui dérive le total de zéro : symétrique par construction, à la hausse comme à la baisse. Vérifié sur `lab_client` |
| 3 | **Majeure** | Le verdict du point 1 (« VALIDÉ — 12/12 critères ») affirme des montants que D-03 contredit | Laissé tel quel dans le suivi, il ferait livrer une release dont le README annonce 12 EUR à 4 jours | Marquer le point 1 **PÉRIMÉ (remplacé par le point 2)** dans le README et dans `qa.md`, sans effacer ses preuves ni son historique |
| 4 | Mineure | D-02 rejoint D-01 au cimetière des règles mortes, et D-02 est déjà **codée** | La prochaine chaîne trouvera 12/4 dans le journal, les tests et le code du dépôt | Étendre le test de non-régression : le forfait n'est ni proportionnel (D-01) ni de 12 EUR, et une location de 4 jours n'en porte aucun (D-02) |
| 5 | Mineure | `Float` plutôt que `Monetary`, absence de contrainte de positivité | Déjà arbitrés hors périmètre au point 1 | Inchangé, hors périmètre |

Aucune contradiction bloquante. D-03 tranche seuil, montant, borne et exclusion des prêts :
**aucune question bloquante ne subsiste**.

## 5. Questions bloquantes

Aucune.

## 6. Hypothèses retenues (à défaut de réponse)

- **Rétroactif sans réserve** : D-03 s'applique à **toutes** les locations en base, y compris celles
  déjà passées à 12 EUR sous D-02, et non aux seules nouvelles. D-02 n'ayant jamais été livrée hors
  copie de validation, aucun document client ne porte le montant de 12 EUR — rien à préserver.
- Le forfait reste un **montant fixe unique**, ajouté une seule fois, indépendant du tarif journalier.
- La borne est **inclusive** : 5 jours porte le forfait, 4 jours ne le porte pas.
- Seuil et montant restent des **constantes nommées** du modèle, pas des paramètres de configuration.
- Un `days` négatif n'atteint pas la borne et ne déclenche donc aucun forfait.

## 7. Spécification

### Modèle de données
Aucun champ ajouté, supprimé ni renommé. `lab.rental.amount_total` reste `Float`, `compute`, `store=True`.

### Comportement
```
base = days * daily_rate
amount_total = base + 15.0  si kind == 'rental' et days >= 5
amount_total = base         sinon
```
`@api.depends('days', 'daily_rate', 'kind')` couvre déjà les trois entrées : inchangé.

### Interface
**Rien.** Aucune vue, aucun menu, aucune action, aucun libellé.

### Sécurité
**Rien.** `ir.model.access.csv` inchangé, aucun groupe, aucune règle d'enregistrement.

### Reprise de données
Manifest en **19.0.1.2.0** et `migrations/19.0.1.2.0/post-migrate.py` qui rappelle le calcul de
`amount_total` sur toutes les locations. Idempotent, dérivé de `days`/`daily_rate`/`kind`, n'écrit
aucun autre champ. Le dossier `19.0.1.1.0` est conservé pour les bases qui ne l'ont pas traversé.
À vérifier sur `lab_client`, **depuis l'état D-02** : la location de 4 jours redescend à 40.0, celle
de 7 jours monte de 152.0 à 155.0, celle de 5 jours à tarif nul passe de 12.0 à 15.0, les prêts et la
location de 3 jours ne bougent pas.

### Hors périmètre
Facturation, comptabilité, écrans, droits, contrainte de positivité, `Monetary`/`currency_id`,
paramétrage du seuil ou du montant, application sélective à des documents historiques.

## 8. Critères d'acceptation

- [ ] Étant donné une location (`kind = rental`) de 5 jours à 10 EUR/jour, quand le montant est calculé, alors `amount_total` vaut 65.0 (nouvelle borne, inclusive).
- [ ] Étant donné une location de 4 jours à 10 EUR/jour, quand le montant est calculé, alors `amount_total` vaut 40.0 : sous le nouveau seuil, plus aucun forfait — c'est le renversement de D-02.
- [ ] Étant donné une location de 3 jours à 10 EUR/jour, quand le montant est calculé, alors `amount_total` vaut 30.0.
- [ ] Étant donné une location de 7 jours à 20 EUR/jour, quand le montant est calculé, alors `amount_total` vaut 155.0 (forfait appliqué une seule fois).
- [ ] Étant donné un prêt (`kind = loan`) de 5 jours à 10 EUR/jour, quand le montant est calculé, alors `amount_total` vaut 50.0 (prêts exclus).
- [ ] Étant donné un prêt de 10 jours à 10 EUR/jour, quand le montant est calculé, alors `amount_total` vaut 100.0 (aucune durée ne rend un prêt payant).
- [ ] Étant donné une location de 0 jour à 0 EUR/jour, quand le montant est calculé, alors `amount_total` vaut 0.0.
- [ ] Étant donné une location de 5 jours à 0 EUR/jour, quand le montant est calculé, alors `amount_total` vaut 15.0 (le forfait ne dépend pas du tarif).
- [ ] Étant donné une location de 4 jours déjà enregistrée, quand `days` passe à 5, alors `amount_total` stocké est recalculé et vaut 65.0.
- [ ] Étant donné une location de 6 jours, quand `kind` passe à `loan`, alors `amount_total` stocké perd exactement 15.0 (recalcul symétrique).
- [ ] Étant donné deux locations de même durée et de tarifs très différents, quand on retranche `jours × tarif`, alors le reste vaut 15.0 dans les deux cas : le forfait n'est ni proportionnel (D-01, 7 %) ni de 12.0 (D-02).
- [ ] Étant donné la copie `lab_client` déjà porteuse des montants D-02, quand le module est mis à niveau, alors la location de 4 jours redescend à 40.0, celle de 7 jours passe à 155.0, celle de 5 jours à tarif nul passe à 15.0, et la location de 3 jours comme les deux prêts restent inchangés.
- [ ] Étant donné la copie `lab_client`, quand la mise à niveau est rejouée une seconde fois, alors aucun montant ne change : la reprise est idempotente.
- [ ] Étant donné le module après la tâche, quand on l'inspecte, alors aucune vue, aucun droit, aucun champ et aucune dépendance n'ont été ajoutés.

## 9. Estimation et découpage

Un seul incrément indivisible : les deux constantes, la reprise versionnée et les tests. ~1 h.

**Niveau QA** : **renforcé** — le champ est stocké, la reprise réécrit des valeurs existantes et les
fait pour la première fois **baisser**. La QA de tâche comprend la vérification sur la copie
`lab_client` en plus du lint et des tests ciblés.

## 10. Ce que l'utilisateur verra

Rien de nouveau à l'écran. Par rapport à **aujourd'hui** (avant cette release) : les locations de
5 jours et plus affichent 15 EUR de plus, les locations de 4 jours et moins sont inchangées, les
prêts sont inchangés. La communication de clôture ne doit **jamais** mentionner l'étape
intermédiaire à 12 EUR / 4 jours : elle n'a existé que sur la copie de validation.
