## Compte-rendu (conversation)

**Avertissement de méthode** : dans cet exercice je n'ai ni les sources Odoo, ni la base client, ni le briefing. Je n'ai donc **exécuté aucun script et lu aucun fichier**. Tout ce qui touche au standard 19.0 ci-dessous est marqué `À VÉRIFIER` et doit être confirmé par `grep` dans `~/odoo-sources/19.0` avant la moindre ligne de code. Je livre la passation, les entrées de suivi et la matrice de tests demandée.

- **Verdict pressenti : PARTIEL.** E-01 (« tout livrer en une fois ») ressemble à de la configuration pure ; c'est le seuil 60 % + l'approbation qui est du développement.
- **Voie recommandée** : indéterminable sans le profil du projet (nombre de modules custom, présence de Studio). Le double workflow d'approbation + le calcul de seuil + les tests exigés poussent vers **module**, sauf projet Online/SaaS.
- **Quatre arbitrages non tranchés bloquent le chiffrage** ; les cinq cas de test demandés sont, eux, tranchables dès maintenant sauf le cas 4/5 en variation successive.
- Fichiers à écrire (contenus fournis ci-dessous, non écrits) : `.odoo-agents/revue_en_cours.md`, `.odoo-agents/PROJECT.md`, `.odoo-agents/JOURNAL.md`.

---

# Revue fonctionnelle — Livraison partielle sous seuil et approbation logistique

**Projet** Entrepôt Cobalt · **série** 19.0 · **modules concernés** `sale`, `sale_stock`, `stock`, `contacts` (+ module custom à créer ou pack Studio)

## 1. Ce que je comprends

> En tant que préparateur logistique, je veux savoir si je peux expédier une commande incomplète, afin de ne pas retarder un client qui accepte les partiels ni expédier à tort chez un client qui les refuse.

Périmètre : commandes de vente et leurs transferts de livraison sortants. Introduction d'un consentement contact au partiel, d'un seuil de 60 %, et d'un circuit d'approbation par le responsable logistique avec séparation des rôles.

**Problème réel** : **non établi.** Le dossier donne trois demandes (E-01, E-02, E-03) mais aucune évidence : pas de ticket, pas de volume de commandes concernées, pas de fréquence des expéditions sous seuil, pas de coût actuel. Je ne peux pas dire si ce dispositif traite 3 commandes par an ou 300 par semaine. **C'est le premier manque à combler** : le seuil de 60 % est un chiffre de réunion, pas une donnée observée, et l'ensemble du circuit d'approbation peut s'avérer plus cher que le problème.

Second point : E-01 (« toutes les commandes livrées en une fois ») et E-02 (« on peut livrer à 60 % ») sont **contradictoires en l'état**. E-02 est présentée comme une « correction », je la traite donc comme remplaçant E-01, avec E-01 réduit au cas « contact refusant les partiels ». À confirmer par le client.

## 2. Verdict standard Odoo 19.0 — `À VÉRIFIER`

**PARTIEL (présomption, non vérifiée)**

| Élément | Piste standard à vérifier | Commande de vérification |
|---|---|---|
| « Livrer en une fois » (E-01) | champ `picking_policy` sur `sale.order` (valeurs `direct` / `one`), fourni par `sale_stock` | `grep -rn "picking_policy" ~/odoo-sources/19.0/addons/sale_stock/models/` |
| Valeur par défaut par client | présence d'un défaut de politique de livraison au niveau `res.partner` ou paramétrage société | `grep -rn "picking_policy" ~/odoo-sources/19.0/addons/*/models/res_partner.py` |
| Case « accepte les expéditions partielles » sur le contact (E-03) | **aucun champ standard connu** portant ce sens | `grep -rn "partial" ~/odoo-sources/19.0/addons/stock/models/res_partner.py` |
| Seuil de 60 % avant expédition | **aucun mécanisme standard connu** | `grep -rn "availability\|forecast" ~/odoo-sources/19.0/addons/stock/models/stock_picking.py` |
| Approbation d'un transfert par un tiers | **aucun workflow d'approbation sur `stock.picking`** ; comparer avec `stock_barcode`/`quality` en enterprise | `ls ~/odoo-sources/19.0-enterprise \| grep -i "approval\|quality"` |
| Approbation générique réutilisable | module `approvals` (enterprise) — à évaluer : couvre-t-il un objet `stock.picking` ? | `ls ~/odoo-sources/19.0-enterprise/approvals` |

**Conclusion attendue** : E-01 est probablement de la **configuration** (`picking_policy = 'one'`), pas du développement — c'est le point à trancher en premier, avant tout chiffrage. Le seuil et l'approbation sont, eux, du développement.

**Série suivante (19.1 / 19.4)** : non vérifié. À contrôler avant conception, car cela dicte le nommage des champs. Pièges 19.x à retenir dès maintenant pour le développeur : `res.users.group_ids` (et non `groups_id`), `models.Constraint` (et non `_sql_constraints`), `ir.model.access.csv` encore valide en 19.0 mais renommé `ir.access.csv` en 19.4.

## 3. Voies possibles

| Voie | Effort | Ce que l'utilisateur obtient | Coût migration | Recommandée |
|---|---|---|---|---|
| Configuration seule (`picking_policy`) | quasi nul | E-01 uniquement : blocage tant que tout n'est pas dispo. Ni seuil ni approbation. | ~0 | **Oui pour E-01**, insuffisant pour E-02/E-03 |
| Studio / base | moyen | Case contact + champ calculé de taux + automatisation d'alerte. Le blocage dur de `button_validate` et la règle « pas soi-même » sont hors de portée fiable (pas de surcharge de méthode, pas de test Python). | faible | Seulement si projet Online/SaaS — avec risque de contournement documenté |
| Module custom | le plus élevé | Règle appliquée réellement, testable, traçable | à chaque migration | **Oui**, sauf profil SaaS |

**Non tranché** : je ne connais pas le profil du projet (modules custom existants, présence de Studio en base). Lancer `odoo_briefing.py` puis `odoo-config-inventory.sh` sur une copie avant de figer la voie — un champ Studio « partiels acceptés » existe peut-être déjà sur le contact, auquel cas le redévelopper serait un défaut.

## 4. Contradictions et risques

| # | Sév. | Point | Pourquoi c'est un problème | Proposition |
|---|---|---|---|---|
| R1 | Haute | E-01 vs E-02 | Deux règles opposées, aucune abrogation formelle | Acter E-02 comme remplaçante ; E-01 = comportement du cas « refus » |
| R2 | Haute | Définition de « quantité disponible » | `qty_available`, `free_qty`, `virtual_available` ou quantité réservée sur le transfert donnent des résultats différents pour un même stock | Trancher : quantité **réservée sur le transfert** (c'est ce que le préparateur va réellement expédier) |
| R3 | Haute | Granularité ligne vs commande | 60 % atteint globalement peut masquer une ligne à 0 % ; l'inverse aussi | Non arbitré → Q1 |
| R4 | Haute | Base de calcul du taux | 60 % de la quantité **commandée** ou de la quantité **restant à livrer** ? Sur une 2ᵉ expédition après un reliquat, l'écart est majeur | Non arbitré → Q2 |
| R5 | Haute | Référence après variations successives | 50 approuvé → 40 → 45 : « augmentation » par rapport à 40, « diminution » par rapport à 50 | Non arbitré → Q3. Hypothèse : comparaison à la **dernière quantité approuvée** |
| R6 | Moyenne | Point de blocage du workflow | Confirmation du transfert ? Validation (`button_validate`) ? Réservation ? | Non arbitré → Q4. Hypothèse : validation |
| R7 | Moyenne | Reprise des commandes ouvertes | Commandes déjà confirmées, transferts déjà réservés au jour du déploiement ; contacts sans valeur pour la nouvelle case | Défaut = « refuse les partiels » (le plus prudent) et **exclusion des transferts déjà confirmés** → Q5 |
| R8 | Moyenne | Cas « refus » + urgence | Aucune soupape : si le client refuse les partiels, le responsable logistique peut-il forcer ? Le dossier dit non | Acté « non », à confirmer ; sinon c'est une exigence supplémentaire |
| R9 | Moyenne | Séparation des rôles (E-03) | « Ne peut pas approuver sa propre demande » suppose de tracer **qui** a demandé. Un responsable logistique qui prépare lui-même se bloque | Tracer `demandeur` ; prévoir le cas responsable-préparateur (2ᵉ approbateur ou dérogation) |
| R10 | Moyenne | Multi-société / multi-entrepôt | Non évoqué. Un responsable logistique d'une société approuve-t-il pour une autre ? | À poser ; hypothèse mono-société |
| R11 | Moyenne | Contact de livraison ≠ client facturé | La case est sur le **contact de livraison** (E-03), pas sur le client. Si le transfert n'a pas d'adresse de livraison distincte, on retombe sur le client | Règle de repli explicite à écrire |
| R12 | Basse | Backorders | Odoo crée un reliquat après expédition partielle ; le reliquat repassera-t-il par la règle ? | Oui, avec base de calcul à trancher (R4) |
| R13 | Basse | Volume / performance | Inconnu, aucune donnée | Relever le nombre de transferts sortants/mois sur copie |

## 5. Questions bloquantes (5)

1. **Granularité** : le seuil de 60 % s'apprécie-t-il sur la commande entière (total des quantités) ou ligne par ligne (chaque ligne ≥ 60 %) ?
2. **Base de calcul** : 60 % de la quantité commandée d'origine, ou de la quantité restant à livrer sur le transfert en cours ?
3. **Référence après variations** : une quantité approuvée à 50 puis descendue à 40 puis remontée à 45 doit-elle être réapprouvée ? (comparaison à la dernière quantité **approuvée** = oui ; à la dernière quantité **proposée** = non)
4. **Point de blocage** : à quel moment l'utilisateur est-il arrêté — confirmation du transfert, ou clic sur Valider ?
5. **Commandes ouvertes** : au déploiement, la règle s'applique-t-elle aux transferts déjà confirmés/réservés, ou seulement aux nouveaux ?

## 6. Hypothèses retenues à défaut de réponse

- H1 — Granularité : **commande entière** (somme des quantités livrables / somme des quantités commandées).
- H2 — Base : **quantité commandée d'origine** de la ligne/commande.
- H3 — Référence : **dernière quantité approuvée**. Toute baisse sous cette valeur invalide l'approbation ; toute remontée qui n'atteint pas cette valeur reste invalidée.
- H4 — Blocage : à la **validation** du transfert (`button_validate`).
- H5 — Reprise : contacts existants = **refuse les partiels** ; transferts déjà confirmés au déploiement = **exclus** de la règle.
- H6 — Mono-société, mono-devise, pas d'exposition portail.
- H7 — « Disponible » = quantité **réservée sur le transfert sortant**.
- H8 — Aucune dérogation possible au refus client (E-01 s'applique intégralement dans ce cas).

Toutes ces hypothèses sont à valider ; le développeur les implémente telles quelles et les rend faciles à inverser (paramètre plutôt que constante en dur pour le seuil et pour H1/H2).

## 7. Spécification

### Modèle de données
- `res.partner.x_accepte_expedition_partielle` (Boolean, défaut `False`) — case dédiée sur le contact de livraison (E-03). Nom définitif à aligner sur un éventuel champ Studio existant en base.
- `stock.picking` :
  - `taux_livraison` (Float, calculé, non stocké ou stocké selon perf) — ratio livrable/commandé selon H1/H2.
  - `approbation_requise` (Boolean, calculé).
  - `approbation_etat` (Selection : `non_requise`, `a_approuver`, `approuvee`) .
  - `quantite_approuvee` (Float) — quantité de référence gelée au moment de l'approbation (support de H3).
  - `demandeur_id` (Many2one `res.users`) — qui a demandé l'approbation.
  - `approbateur_id` (Many2one `res.users`), `date_approbation` (Datetime).
- Paramètre système `entrepot_cobalt.seuil_partiel` = `0.60` (jamais en dur).
- Contraintes : utiliser `models.Constraint` (19.0), pas `_sql_constraints`.

### Comportement
Au point de blocage (H4), pour un transfert sortant lié à une commande de vente :

1. Si le contact de livraison **refuse** les partiels et que la quantité proposée < quantité commandée → **blocage dur**, message explicite, aucune approbation possible.
2. Si le contact **accepte** et taux ≥ 60 % → passage libre, aucune approbation.
3. Si le contact **accepte** et taux < 60 % → approbation requise ; état `a_approuver`, validation refusée tant que non approuvée.
4. Approbation : réservée au groupe « Responsable logistique ». Refus si `approbateur == demandeur_id` (E-03).
5. Après approbation, si la quantité proposée **diminue** sous `quantite_approuvee` → retour à `a_approuver`, `quantite_approuvee` remise à zéro. Si elle **augmente** → approbation conservée, `quantite_approuvee` mise à jour à la nouvelle valeur.

### Interface
- Case à cocher sur la fiche contact, onglet Ventes ou Logistique.
- Sur le transfert : bandeau d'avertissement, champ taux en lecture seule, bouton **Demander l'approbation** (préparateur) et **Approuver** (responsable, masqué si demandeur).
- Message d'erreur distinct pour le cas « refus client » (non contournable) et le cas « sous seuil » (approbable).
- Trace au chatter à chaque demande, approbation et invalidation.

### Sécurité
- Nouveau groupe « Responsable logistique » ; en 19.0 utiliser `group_ids` sur `res.users`.
- Droits d'écriture sur les champs d'approbation limités à ce groupe ; les préparateurs sont en lecture.
- Le contrôle « pas soi-même » doit être **serveur** (pas seulement masquage de bouton).
- Droits `ir.model.access.csv` (valide en 19.0).

### Reprise de données
- Aucun contact ne dispose de la case → tous à `False` (H5) : **effet immédiat = toutes les commandes basculent en « refus des partiels »**. C'est un impact d'exploitation majeur, à annoncer. Prévoir un export de la liste des contacts à requalifier avant mise en production.
- Transferts déjà confirmés au déploiement : exclus (H5), via une date de bascule ou un marquage à l'installation.
- Aucun champ obligatoire ajouté sur un modèle peuplé.

### Hors périmètre
Achats et transferts internes ; notifications e-mail au client ; délégation d'approbation en cas d'absence ; historique des approbations antérieures au déploiement ; portail client.

## 8. Critères d'acceptation

Les cinq cas demandés, sur une commande de **80 unités**, seuil = 60 % → **48 unités**.

| # | Situation | Attendu |
|---|---|---|
| **T1** | Contact **accepte**, 50 disponibles | 50 ≥ 48 → **livraison sans approbation**. Aucun blocage, aucun état d'approbation. |
| **T2** | Contact **accepte**, 40 disponibles | 40 < 48 → **approbation du responsable logistique requise**. Validation refusée tant que non approuvée. |
| **T3** | Contact **refuse**, 50 disponibles | **Blocage**, attente des 80 unités. **Aucune approbation ne débloque** (H8). |
| **T4** | Approuvée à 50, abaissée à 40 | Diminution → **approbation invalidée, revalidation requise**. (40 est en outre sous le seuil.) |
| **T5** | Approuvée à 50, portée à 60 | Augmentation → **approbation conservée**, aucune revalidation. `quantite_approuvee` passe à 60. |

Rédaction Gherkin :

- [ ] **T1** — Étant donné une commande de 80 unités pour un contact acceptant les partiels, quand 50 unités sont disponibles, alors le transfert se valide sans demande d'approbation.
- [ ] **T2** — Étant donné la même commande, quand 40 unités seulement sont disponibles, alors la validation est refusée et une demande d'approbation est proposée.
- [ ] **T2b** — Étant donné cette demande d'approbation créée par le préparateur P, quand P tente d'approuver, alors le système refuse (E-03).
- [ ] **T2c** — Étant donné cette demande, quand le responsable logistique R (≠ P) approuve, alors la validation devient possible.
- [ ] **T3** — Étant donné une commande de 80 unités pour un contact refusant les partiels, quand 50 unités sont disponibles, alors la validation est refusée et aucun bouton d'approbation n'est proposé.
- [ ] **T3b** — Étant donné le même cas, quand les 80 unités deviennent disponibles, alors la validation passe sans approbation.
- [ ] **T4** — Étant donné une livraison approuvée à 50, quand la quantité proposée passe à 40, alors l'état repasse à « à approuver » et la validation est refusée.
- [ ] **T5** — Étant donné une livraison approuvée à 50, quand la quantité proposée passe à 60, alors l'approbation reste valide et la validation passe sans nouvelle intervention.
- [ ] **T5b** — Étant donné une livraison approuvée à 50, quand la quantité passe à 40 puis à 45, alors *(dépend de Q3 ; sous H3 : la validation reste refusée car 45 < 50)*.
- [ ] **T6** — Étant donné un contact sans valeur pour la case (migration), quand on tente une livraison partielle, alors le comportement est celui du refus.
- [ ] **T7** — Étant donné un utilisateur sans le groupe « Responsable logistique », quand il appelle la méthode d'approbation directement, alors l'accès est refusé côté serveur.

## 9. Estimation et découpage

Aucune estimation chiffrée n'est communicable tant que Q1–Q5 et le profil du projet ne sont pas connus. Découpage proposé, chaque lot livrable seul :

1. **Lot 0 — configuration** : appliquer `picking_policy` (E-01) si le standard le permet. Peut couvrir une partie du besoin sans développement, et se déploie immédiatement.
2. **Lot 1 — consentement contact** : case sur `res.partner`, blocage dur en cas de refus (T3, T3b, T6). Livre à lui seul le cas le plus strict.
3. **Lot 2 — seuil** : calcul du taux, paramètre 60 %, distinction sous/au-dessus (T1, T2).
4. **Lot 3 — approbation** : groupe, workflow, séparation des rôles (T2b, T2c, T7).
5. **Lot 4 — revalidation sur variation** : gel et comparaison de `quantite_approuvee` (T4, T5, T5b).

**Niveau QA : renforcé, obligatoire.** Motifs cumulés : création d'un groupe et de droits (E-03), modification de données existantes (contacts, transferts ouverts), et impact direct sur les expéditions donc sur la facturation. **Copie de la base client exigée** avant déploiement — elle sert aussi à mesurer le volume manquant (R13) et à vérifier l'absence de champ Studio équivalent.

## 10. Ce que l'utilisateur verra

- **Contact** : une nouvelle case « Accepte les expéditions partielles », décochée sur toutes les fiches existantes.
- **Préparateur** : un bandeau sur le transfert indiquant le taux de livraison ; un refus de validation avec deux messages distincts selon refus client ou sous-seuil ; un bouton « Demander l'approbation » dans le second cas seulement.
- **Responsable logistique** : un bouton « Approuver », grisé sur ses propres demandes ; une notification au chatter.
- **Changement d'habitude à annoncer** : le jour du déploiement, **toutes** les livraisons partielles se bloquent tant que les contacts n'ont pas été requalifiés. C'est le point principal de la communication client.

---

# Entrées à enregistrer

### `.odoo-agents/PROJECT.md` — section « Compréhension métier »

```markdown
## Compréhension métier — Livraison partielle (Entrepôt Cobalt, 19.0)

- Le consentement à l'expédition partielle est une propriété du **contact de
  livraison**, pas du client facturé ni de la commande (source : E-03, client).
- Un seuil de 60 % de la quantité commandée sépare la livraison partielle libre
  de la livraison partielle soumise à approbation (source : E-02, client).
- L'approbation relève du **responsable logistique** ; le préparateur qui
  demande ne peut pas approuver (séparation des rôles, source : E-03).
- Une approbation porte sur une quantité : elle tombe si la quantité baisse,
  elle survit si la quantité monte (source : E-02).
- Volumétrie, fréquence et coût actuel du problème : **inconnus**, jamais
  fournis. Le seuil de 60 % n'est adossé à aucune mesure.
```

### `.odoo-agents/PROJECT.md` — section « Décisions actées »

```markdown
## Décisions actées

- **D-01** (source E-02, arbitrage client) — E-02 **remplace** E-01. La règle
  « toutes les commandes livrées en une fois » ne s'applique plus qu'aux
  contacts refusant les expéditions partielles. *Confirmation client à obtenir.*
- **D-02** (source E-02) — Seuil de livraison sans approbation : 60 % de la
  quantité commandée. Implémenté en **paramètre système**, jamais en dur.
- **D-03** (source E-03) — Le consentement au partiel est une case dédiée du
  contact de livraison ; aucun champ standard connu ne le porte.
- **D-04** (source E-03) — Séparation des rôles : contrôle **serveur**, pas
  seulement masquage de bouton.
- **D-05** (source E-02) — Asymétrie assumée : baisse de quantité = nouvelle
  approbation, hausse = approbation maintenue.
- **D-06** (analyse) — Cas « refus client » sans soupape : aucune approbation ne
  débloque une livraison incomplète vers un contact refusant les partiels.
  *Hypothèse, à confirmer.*
- **D-07** (analyse) — QA renforcée obligatoire (droits + données existantes +
  impact facturation). Copie de la base client exigée avant déploiement.
```

### `.odoo-agents/PROJECT.md` — section « Pièges / points de vigilance »

```markdown
- Vérifier avant tout développement si `picking_policy` (sale_stock) couvre E-01 :
  développer par-dessus serait une réimplémentation du standard.
- Vérifier sur copie de base l'absence d'un champ Studio « partiels acceptés »
  déjà présent sur res.partner.
- Série 19.0 : `res.users.group_ids` (pas `groups_id`), `models.Constraint`
  (pas `_sql_constraints`), `ir.model.access.csv` encore valide (→ `ir.access.csv` en 19.4).
- Reprise : contacts par défaut à « refuse les partiels » ⇒ blocage généralisé au
  jour J si la requalification n'est pas faite avant.
```

### `.odoo-agents/JOURNAL.md`

```markdown
## 2026-09-08 — Revue fonctionnelle « livraison partielle sous seuil »

**Intervenant** analyste fonctionnel · **Statut** revue produite, en attente client

- Demandes traitées : E-01 (livraison en une fois, non implémentée), E-02
  (seuil 60 % + approbation), E-03 (case contact + séparation des rôles).
- Revue écrite dans `.odoo-agents/revue_en_cours.md` (release non ouverte).
- Verdict standard : **PARTIEL, non vérifié** — aucun accès aux sources ni à la
  base lors de cette revue. Vérifications `picking_policy` / `res.partner` /
  module `approvals` à faire avant conception.
- Voie non tranchée : profil du projet inconnu (briefing et inventaire de base
  non exécutés).
- 5 questions bloquantes ouvertes (granularité, base de calcul, référence après
  variations, point de blocage, reprise des commandes ouvertes). 8 hypothèses
  H1–H8 posées pour permettre l'avancement.
- Contradiction E-01/E-02 relevée et arbitrée provisoirement en D-01.
- Manque d'évidence signalé : ni volume, ni fréquence, ni coût du problème.
- Prochaine action : `odoo_briefing.py` + `odoo-config-inventory.sh` sur copie,
  puis retour client sur Q1–Q5.
```

### Ce qui attend le client (à ne pas développer avant réponse)

| Réf | Attente | Bloque |
|---|---|---|
| Q1 | Granularité ligne vs commande | Modèle de calcul, lots 2 et 4 |
| Q2 | Base : quantité commandée vs restant à livrer | Comportement des reliquats |
| Q3 | Référence après variations successives (T5b) | Lot 4 |
| Q4 | Point de blocage dans le workflow | Toute l'implémentation |
| Q5 | Sort des commandes ouvertes au déploiement | Plan de reprise, déploiement |
| C1 | Confirmation que E-02 abroge bien E-01 (D-01) | Périmètre global |
| C2 | Confirmation qu'aucune dérogation n'existe au refus client (D-06) | Lot 1 |
| C3 | Volumétrie et fréquence réelles | Décision d'opportunité : ce dispositif vaut-il son coût ? |
| C4 | Fourniture d'une sauvegarde de la base | Vérification Studio, volumes, QA renforcée |