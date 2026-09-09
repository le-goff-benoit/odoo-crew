# Revue fonctionnelle — Frais de préparation des locations (D-02)

**Projet** Atelier Boréal (`/work`) · **série** 19.0 (origine : `__manifest__.py`) · **modules concernés** `lab_rental`

## 1. Ce que je comprends

En tant que gestionnaire de locations, je veux que le total d'une location de 4 jours ou
plus intègre automatiquement 12 EUR de frais de préparation, afin que le montant stocké
reflète le coût réel de remise en état sans ressaisie.

Périmètre : le seul champ `lab.rental.amount_total` (calculé, stocké). Pas d'écran, pas de
facturation, pas de comptabilité, pas de droits.

**Problème réel** : le total actuel (`days × daily_rate`) ignore le temps de préparation,
constant et non proportionnel à la durée. La décision D-02 (`decisions/2026-09-08.md`,
actée le 08/09 par Alice Martin) le forfaitise à 12 EUR à partir de 4 jours, pour les
locations seulement. D-02 **remplace** D-01 (7 % sur toutes les locations, `JOURNAL.md`
2026-08-01) : la règle en pourcentage ne doit apparaître nulle part dans le code livré.

## 2. Verdict standard Odoo 19.0

**PARTIEL au niveau du standard — À DÉVELOPPER sur l'existant custom.**

- Le standard sait tarifer une location à la durée, mais uniquement dans **Enterprise** :
  `~/odoo-sources/19.0-enterprise/sale_renting/` (`models/product_pricing.py`,
  `models/sale_order_line.py`). Aucun module `*renting*` dans
  `~/odoo-sources/19.0/addons` (vérifié : `ls ~/odoo-sources/19.0/addons | grep -i rent`
  ne renvoie rien) — c'est de l'Enterprise pur.
- `sale_renting` tarife des `sale.order.line` liées à des `product.product` et à des
  `product.pricing`. Le seul mécanisme de supplément qu'il porte est la pénalité de retard
  (`sale_order_line.py:271`, `company_id.min_extra_hour`) : ce n'est pas un forfait de
  préparation conditionné à la durée.
- Le modèle du projet, `lab.rental` (`lab_rental/models/business.py`), est autonome :
  pas de produit, pas de commande, pas de devise. Basculer sur `sale_renting` pour un
  forfait de 12 EUR imposerait Enterprise, `sale`, et une reprise complète du modèle —
  hors de proportion avec la demande, et hors périmètre (« sans changer les écrans »).

**Série suivante** : rien à ce sujet dans `~/odoo-sources/19.1` ni `19.4` — la règle est
une spécificité métier du client, elle ne sera pas absorbée par un futur standard. Le
delta restera custom à la migration ; il est minuscule (une condition dans un compute).

## 3. Voies possibles

| Voie | Effort | Ce que l'utilisateur obtient | Coût à la migration | Recommandée |
|---|---|---|---|---|
| Configuration | impossible | rien : aucun paramètre standard ne porte cette règle | — | non |
| Studio / configuration en base | 1 h | champ calculé en `safe_eval`, non testable en Python | moyen (pack à rejouer) | non |
| Code custom (`lab_rental`) | 30 min | règle versionnée, testée, dans le compute qui existe déjà | négligeable (3 lignes) | **oui** |

Profil du projet : un module custom, aucun Studio en base → voie module par défaut. La
demande porte sur de la logique de calcul, hors de portée raisonnable de Studio (pas de
test Python). Voie retenue : **`odoo-developer`, module `lab_rental`**.

## 4. Contradictions et risques

| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|---|---|---|---|
| 1 | Majeure | `amount_total` est **stocké** : la mise à jour du module recalcule tous les enregistrements existants dont `days >= 4` et `kind = 'rental'` (+12 EUR) | C'est une écriture sur des données existantes, pas seulement du code | Acté : D-02 dit « tous les enregistrements du bac sont des essais modifiables ». Le recalcul est l'effet **voulu**. Conséquence : **QA renforcée**, contrôle obligatoire sur la copie `lab_client` (avant/après chiffrés) |
| 2 | Mineure | D-01 (7 %) traîne dans le journal | Un lecteur pressé peut réimplémenter la mauvaise règle | Rien à retirer du code (aucun frais n'y est aujourd'hui) ; noté dans `PROJECT.md` que D-02 fait foi |
| 3 | Mineure | Valeurs négatives de `days` / `daily_rate` | D-02 dit qu'elles « restent positives ou nulles » : c'est une **hypothèse** sur les données, pas une contrainte demandée | Aucune contrainte SQL ajoutée : elle échouerait sur d'éventuelles données existantes non conformes et dépasserait le périmètre. Une location à `days = -5` ne déclenche pas le forfait (borne `>= 4`), le comportement reste défini |
| 4 | Mineure | `amount_total` est un `Float`, pas un `Monetary` | Pas de devise portée par le modèle | D-02 : « une seule monnaie EUR, aucun arrondi supplémentaire ». On ne convertit pas en `Monetary` : cela ajouterait `currency_id` et changerait l'écran. Hors périmètre |
| 5 | Mineure | Multi-société, archivage, portail, mobile | Non-dits habituels | Sans objet : modèle autonome sans `company_id`, sans `active`, sans vue, sans exposition portail |

Aucune contradiction bloquante. Les deux questions ouvertes (Q1 borne, Q2 prêts) sont
**déjà tranchées** dans `decisions/2026-09-08.md` — pas de question bloquante à poser.

## 5. Questions bloquantes

Aucune.

## 6. Décisions (réponses reçues, `decisions/2026-09-08.md`)

- **Q1 — la borne de 4 jours est inclusive** : oui, `days >= 4`. Une location de 4 jours
  porte les frais.
- **Q2 — les prêts** : exclus, sans exception, y compris à 4 jours et plus.
- Montants hors taxes, monnaie unique EUR, **aucun arrondi supplémentaire** : arithmétique
  directe, pas de `float_round`, pas de `currency.round()`.
- D-02 remplace D-01 : pas de frais proportionnel.
- Aucune modification de droits, de comptabilité, ni de documents historiques.

## 7. Spécification

### Modèle de données

Aucun nouveau champ, aucune migration de schéma. `lab.rental.amount_total` (`Float`,
`compute='_compute_amount_total'`, `store=True`) conserve sa définition ; seule la formule
change.

### Comportement

`_compute_amount_total`, pour chaque enregistrement :

```
base = days × daily_rate
amount_total = base + 12.0  si kind == 'rental' et days >= 4
amount_total = base         sinon
```

Le montant du forfait (12 EUR) et le seuil (4 jours) sont des constantes de module
nommées, pas des littéraux dispersés, pour que la prochaine décision se relise en un point.

`@api.depends('days', 'daily_rate', 'kind')` est déjà correct et couvre les trois entrées :
inchangé.

### Interface

**Rien de visible.** Le module ne contient aucune vue (`__manifest__.py` → `data` ne
déclare que `security/ir.model.access.csv`). Aucun écran n'est ajouté ni modifié.

### Sécurité

Inchangée. `ir.model.access.csv` n'est pas touché, aucun groupe, aucune `ir.rule`.

### Reprise de données

**Corrigé le 09/09 par la mesure — voir `preuves/copie_client_avant.txt` et
`preuves/copie_client_apres.txt`.** L'hypothèse initiale de cette revue (« le `-u` suffit »)
est **fausse** : sur `lab_client`, la mise à jour du module avec la nouvelle formule a laissé
les sept enregistrements existants inchangés (location de 4 jours toujours à 40,00). Odoo ne
recalcule pas un champ `store=True` dont seul le **corps** du compute a changé ; c'est la
règle déjà écrite dans `~/.odoo19-agents/roles/implementation.md` (« corriger le calcul d'un
champ stocké ne corrige pas les valeurs en base »).

La reprise est donc **obligatoire et fait partie du périmètre** :
`migrations/19.0.1.1.0/post-migrate.py`, idempotent, qui réapplique la formule à tous les
`lab.rental` existants. Elle impose d'incrémenter la version du manifest **maintenant**
(19.0.1.0.0 → 19.0.1.1.0) : un script de migration ne s'exécute que si la version installée
est inférieure à celle du manifest (`~/odoo-sources/19.0/odoo/modules/migration.py:192-208`).

Effet attendu et voulu sur la copie `lab_client` : les locations (`kind = 'rental'`) de
4 jours ou plus gagnent 12 EUR ; les prêts et les locations courtes ne bougent pas d'un
centime. Ce delta est **chiffré avant/après** en QA.

### Hors périmètre

Facturation, comptabilité, taxes, devise/`Monetary`, écrans et vues, droits d'accès,
contrainte de positivité, paramétrage du forfait par société ou par utilisateur,
historisation du montant des frais dans un champ dédié.

## 8. Critères d'acceptation

- [ ] **CA1** — Étant donné une location (`kind = 'rental'`) de 5 jours à 10 EUR/jour,
      quand le total est calculé, alors `amount_total = 62.0` (50 + 12).
- [ ] **CA2** — Étant donné une location de **4 jours** à 10 EUR/jour (borne inclusive,
      Q1), quand le total est calculé, alors `amount_total = 52.0`.
- [ ] **CA3** — Étant donné une location de **3 jours** à 10 EUR/jour, quand le total est
      calculé, alors `amount_total = 30.0` — pas de frais sous le seuil.
- [ ] **CA4** — Étant donné un **prêt** (`kind = 'loan'`) de 10 jours à 10 EUR/jour (Q2),
      quand le total est calculé, alors `amount_total = 100.0` — jamais de frais sur un prêt.
- [ ] **CA5** — Étant donné un prêt de **4 jours** exactement, quand le total est calculé,
      alors `amount_total` est sans frais — la borne ne rattrape pas les prêts.
- [ ] **CA6** — Étant donné une location existante, quand `days` passe de 3 à 4, alors
      `amount_total` stocké est recalculé et inclut les frais ; quand `kind` passe de
      `rental` à `loan`, alors les frais disparaissent.
- [ ] **CA7** — Étant donné `days = 0` ou `daily_rate = 0`, quand le total est calculé,
      alors le résultat reste défini (0.0 pour 0 jour ; 12.0 pour une location de 4 jours
      à tarif nul — le forfait ne dépend pas du tarif).
- [ ] **CA8** — Après mise à jour du module sur la copie `lab_client`, les enregistrements
      **déjà en base** portent le bon total : locations ≥ 4 j : +12 ; prêts et locations
      courtes inchangés. Delta mesuré en SQL avant/après.
- [ ] **CA10** — La reprise est **idempotente** : la rejouer ne cumule pas les frais.
- [ ] **CA9** — Aucune vue, aucun droit, aucun champ ajouté : le diff se limite à
      `models/business.py`, aux tests, au script de reprise et à la version du manifest.

## 9. Estimation et découpage

Un seul incrément, indivisible : formule + tests. ~30 min.

**Niveau QA : renforcé.** La tâche modifie des **données existantes** (recalcul d'un champ
stocké sur la copie `lab_client`) : la validation sur copie client est obligatoire et se
joue maintenant, sans attendre la clôture de la release.

## 10. Ce que l'utilisateur verra

**Rien de visible au sens des écrans** : aucune vue n'est ajoutée ni modifiée. Ce qui
change pour lui, c'est la **valeur** du total sur les locations de 4 jours ou plus, qui
augmente de 12 EUR. À la clôture, la communication client devra dire exactement cela :
« le total des locations de 4 jours et plus intègre désormais 12 EUR de frais de
préparation ; les prêts et les locations de moins de 4 jours sont inchangés ; aucune
facture n'est émise ni modifiée ».
