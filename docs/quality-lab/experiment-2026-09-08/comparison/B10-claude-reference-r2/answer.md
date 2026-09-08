# Passation développeur / testeur — Plafond de remise et approbation

**Projet** Atelier Boréal · **série** 19.0 · **modèles concernés** `sale.order`, `sale.order.line`, `res.partner` · **état** rien de développé, rien de déployé, aucun test.

> **Avertissement de méthode** : cet exercice se déroule sans accès aux sources Odoo, sans copie de base client et sans briefing. Je n'ai donc **pas** vérifié le standard 19.0 ni l'existant en base. Tout ce qui touche au verdict standard ci-dessous est une **hypothèse à confirmer**, pas une preuve — les chemins cités sont à contrôler avant la première ligne de code.

---

## 1. La règle actuelle (M-01 corrigée par M-02 + M-03)

En une phrase : *En tant que commercial, je veux pouvoir accorder une remise jusqu'à mon plafond sans blocage, et déclencher une approbation du directeur au-delà, afin que les remises exceptionnelles restent contrôlées sans ralentir les devis courants.*

Règle en vigueur, telle qu'elle doit être développée :

| Cas | Plafond commercial | Au-delà |
|---|---|---|
| Client **partenaire** | 15 % | approbation directeur |
| Client **non partenaire** | 10 % | approbation directeur |

- **Définition de « partenaire »** : case « partenaire commercial » cochée sur le **contact de facturation du devis** (`partner_invoice_id`), pas sur le client (`partner_id`).
- **Séparation des rôles** : un vendeur ne peut pas approuver sa propre demande d'approbation.
- **Revalidation** : un devis déjà approuvé dont la remise **augmente** repasse en approbation ; s'il **diminue**, il reste valide.

## 2. Ce qui remplace l'ancienne décision

- **D-01 (« remise maximale 10 % pour tous les clients ») est remplacée, pas amendée.** Elle devient un cas particulier : 10 % est désormais le plafond des **non-partenaires** uniquement.
- Conséquence pour le développeur : **ne pas** coder 10 % comme une constante globale. Le plafond est une **fonction du client** (deux valeurs paramétrables, pas en dur), et l'existence d'un circuit d'approbation est nouvelle — D-01 n'en prévoyait aucun. Une implémentation « contrainte bloquante à 10 % » serait aujourd'hui fausse.
- Aucun impact de reprise de données : D-01 n'a jamais été développée, il n'y a donc **aucun devis existant** contraint par l'ancienne règle. C'est le seul point confortable du dossier.

## 3. Verdict standard — **À VÉRIFIER, hypothèse : PARTIEL**

Ce que je m'attends à trouver (à confirmer dans `~/odoo-sources/19.0` et `19.0-enterprise`) :

- La remise est portée **par ligne** : `sale.order.line.discount`, activée par le groupe `sale.group_discount_per_so_line` — il n'y a pas de champ « remise du devis » au niveau entête. C'est le point le plus structurant de tout le dossier.
- Un assistant de remise globale (`sale.order.discount`, introduit en 17.0, `addons/sale/wizard/`) permet d'appliquer une remise soit sur toutes les lignes, soit sous forme d'une **ligne de remise en montant fixe** — laquelle échappe mécaniquement à tout contrôle basé sur `discount`.
- Un **plafond de remise avec approbation** n'existe à ma connaissance pas en standard 19.0 (ni Community, ni le module Enterprise `approvals`, qui traite les demandes internes et non les documents de vente). C'est donc probablement du développement légitime — **mais c'est exactement l'affirmation qu'il faut prouver avant de coder**, par `grep -rn "discount" $S/addons/sale/models/sale_order*.py` et un inventaire de la base client (un champ Studio ou une automatisation peut déjà faire tout ou partie du travail).
- **Il n'existe pas de champ standard « partenaire commercial » booléen sur `res.partner`.** Attention au piège de vocabulaire : `commercial_partner_id` en standard désigne l'entité société d'un contact, ce qui n'a **rien à voir** avec la notion métier ici. Le champ est à créer, avec un nom sans ambiguïté (`is_trade_partner` plutôt que `is_commercial_partner`).

**Série suivante** : à vérifier dans `~/odoo-sources/19.1` / `19.4`. Points de vigilance 19.x connus si du code est écrit : `res.users.groups_id` → `group_ids`, `_sql_constraints` → `models.Constraint`, `ir.model.access.csv` → `ir.access.csv` en 19.4.

## 4. Voies

| Voie | Effort | Ce qu'on obtient | Coût migration | Reco |
|---|---|---|---|---|
| Configuration seule | — | Rien : aucun plafond conditionnel en standard | — | non |
| Studio / automatisations | moyen | Champ booléen partenaire + contrainte `safe_eval` + états d'approbation | faible/moyen | à évaluer selon le profil réel du projet |
| Module custom | moyen | Règle testable, contrainte serveur, workflow d'approbation propre | à chaque migration | **oui si le projet a déjà des modules** |

Le choix se tranche avec le briefing (nombre de modules custom) et l'inventaire de la base (présence de Studio) — deux éléments que je n'ai pas ici. **La contrainte doit être serveur dans tous les cas** : un contrôle purement en vue est contournable par import, API et duplication.

## 5. Contradictions et risques

| # | Sév. | Point | Pourquoi c'est un problème | Proposition |
|---|---|---|---|---|
| 1 | **Bloquant** | « la remise du devis » n'existe pas : la remise est par ligne | Un devis à 3 lignes 5/5/20 % est-il à 20 % ? à 10 % (moyenne pondérée) ? Toute la règle et tous les tests en dépendent | Retenir **max des lignes** par défaut (le plus protecteur), à confirmer |
| 2 | **Bloquant** | « devis approuvé » est ambigu | Approbation *du directeur* sur la remise, ou devis *confirmé* (`state = 'sale'`) ? Deux workflows différents | Hypothèse : approbation de la remise, indépendante de la confirmation |
| 3 | **Bloquant** | Le drapeau est sur `partner_invoice_id` | Ce champ est modifiable après approbation ; changer le contact de facturation change le plafond a posteriori | Recalculer le plafond et invalider l'approbation si `partner_invoice_id` change |
| 4 | Majeur | Remise en **montant fixe** via l'assistant / ligne négative | Contourne 100 % du contrôle sans mauvaise intention | Convertir en % pour le contrôle, ou interdire l'assistant montant fixe |
| 5 | Majeur | Le directeur est parfois le vendeur du devis | La règle « pas d'auto-approbation » bloque le devis sans issue | Prévoir un second approbateur ou un rôle de secours |
| 6 | Majeur | Devis **confirmé** puis remise augmentée | Le texte parle de devis ; une commande confirmée modifiée n'est pas couverte | Étendre la règle à `state = 'sale'` (à arbitrer) |
| 7 | Moyen | Héritage société → contact | Le contact de facturation est-il partenaire si sa société l'est ? | Hypothèse : oui, remontée sur `commercial_partner_id` |
| 8 | Moyen | Multi-société | Plafonds identiques partout ? | Paramètres par société |
| 9 | Moyen | Duplication, import, modèles de devis, API | Contournent souvent les onchange | Contrainte serveur + tests dédiés sur ces chemins |
| 10 | Moyen | Portail | Le client ne doit pas voir « en attente d'approbation directeur » | Masquer l'état côté portail |

## 6. Questions encore ouvertes

**Bloquantes (5) :**
1. La remise contrôlée = **maximum des lignes**, moyenne pondérée, ou remise globale de l'assistant ?
2. « Devis approuvé » = remise approuvée par le directeur, ou devis confirmé ? Et la règle s'applique-t-elle après confirmation ?
3. L'approbation vaut-elle **pour un taux précis** (16 %) ou **pour un plafond accordé** (« jusqu'à 16 % ») ? Cela décide seul du cas 16 → 14 %.
4. Qui est « le directeur » : un groupe dédié, un rôle par société, ou le responsable hiérarchique du vendeur ? Que fait-on quand il est aussi le vendeur ?
5. La case « partenaire commercial » se lit-elle uniquement sur le contact de facturation, ou remonte-t-elle sur sa société ?

**À arbitrer (non bloquant) :** notification de la demande (mail, activité, discussion) ; visibilité côté portail ; plafonds paramétrables en configuration ou en dur ; comportement à l'import de masse.

## 7. Hypothèses retenues à défaut de réponse

- Remise du devis = **maximum de `discount` sur les lignes** non-notes/non-sections.
- Approbation portant sur un **taux plafond accordé** : toute valeur **inférieure ou égale** au taux approuvé reste valide.
- Règle appliquée aux états devis **et** commande confirmée non facturée.
- Partenaire = case cochée sur `partner_invoice_id`, avec remontée sur sa société parente.
- Approbateur = membre du groupe « Directeur commercial », `≠ user_id` du devis.
- Plafonds 10 / 15 % en paramètres de configuration, par société.

## 8. Les cinq exemples demandés

Sous les hypothèses ci-dessus, à faire trancher par le client sur les points marqués :

| # | Situation | Résultat attendu |
|---|---|---|
| A | **Partenaire, 12 %** | Autorisé sans approbation (12 ≤ 15). Aucun blocage, aucune demande créée, devis confirmable directement. |
| B | **Non-partenaire, 12 %** | Approbation directeur requise (12 > 10). Devis bloqué à la confirmation, état « en attente d'approbation », demande adressée à un directeur ≠ vendeur. |
| C | **Partenaire, 16 %** | Approbation directeur requise (16 > 15). Même circuit que B. |
| D | **Approuvé à 16 %, passe à 17 %** | Augmentation → **approbation invalidée**, retour en attente, nouvelle approbation obligatoire. Vaut pour partenaire comme non-partenaire. |
| E | **Approuvé à 16 %, passe à 14 %** | Diminution → **reste approuvé**, pas de nouveau circuit. ⚠️ Point à confirmer (question 3) : si l'approbation vaut pour le taux exact 16 % et non « jusqu'à 16 % », alors 14 % chez un non-partenaire (> 10 %) devrait redéclencher une approbation. La lecture littérale de M-02 (« pas si elle diminue ») dit non ; je retiens « non » et j'écris le risque. |

## 9. Critères d'acceptation

- [ ] Étant donné un devis dont le contact de facturation est partenaire, quand le commercial saisit 12 %, alors le devis se confirme sans demande d'approbation.
- [ ] Étant donné un devis dont le contact de facturation n'est pas partenaire, quand le commercial saisit 12 %, alors la confirmation est refusée et une demande d'approbation est créée.
- [ ] Étant donné un devis partenaire, quand le commercial saisit 16 %, alors une demande d'approbation est créée.
- [ ] Étant donné un devis partenaire à exactement 15 % (et non-partenaire à exactement 10 %), quand il est confirmé, alors aucune approbation n'est requise — **la borne est incluse**.
- [ ] Étant donné un devis approuvé à 16 %, quand la remise passe à 17 %, alors l'approbation est invalidée et le devis repasse en attente.
- [ ] Étant donné un devis approuvé à 16 %, quand la remise passe à 14 %, alors le devis reste approuvé et aucune demande n'est créée.
- [ ] Étant donné une demande d'approbation créée par le vendeur V, quand V tente de l'approuver lui-même, alors l'action est refusée avec un message explicite.
- [ ] Étant donné un devis à 3 lignes remisées 5 %, 5 % et 20 %, alors le contrôle se déclenche sur 20 % (règle du maximum).
- [ ] Étant donné un devis approuvé à 16 %, quand le contact de facturation est remplacé par un non-partenaire, alors le plafond est recalculé et l'approbation réévaluée.
- [ ] Étant donné une remise appliquée en **montant fixe** via l'assistant de remise, alors le contrôle s'applique également (pas de contournement).
- [ ] Étant donné un devis approuvé, quand il est **dupliqué**, alors la copie n'hérite pas de l'approbation.
- [ ] Étant donné une création de devis remisé **par import ou API**, alors la contrainte serveur s'applique identiquement (pas seulement l'onchange).
- [ ] Étant donné un devis en attente d'approbation, quand le client l'ouvre depuis le **portail**, alors il ne voit aucune mention du circuit d'approbation interne.

**Niveau QA : renforcé** — la demande porte sur des droits (groupe directeur, séparation des rôles) et sur le montant facturé. Tests sur copie de base client obligatoires, avec au minimum les chemins import/API/duplication.

## 10. Ce que l'utilisateur verra

Commercial : une case « partenaire commercial » sur les contacts, un bandeau/état « en attente d'approbation directeur » sur le devis au-delà de son plafond, un bouton « Demander l'approbation », un message d'erreur clair à la confirmation. Directeur : les demandes à approuver, avec refus explicite en cas d'auto-approbation. Client : aucun changement côté portail.

---

## Entrée PROJECT.md — prête à enregistrer (non écrite)

```markdown
### Compréhension métier
- Deux catégories de clients : **partenaires** (case « partenaire commercial »
  sur le contact de facturation du devis) et **non partenaires**. La catégorie
  se lit sur `partner_invoice_id`, pas sur `partner_id` — un même client peut
  donc changer de plafond selon le contact de facturation choisi.
- Le plafond de remise est un pouvoir délégué au commercial ; au-delà, la
  décision remonte au directeur commercial. Séparation des rôles exigée : un
  vendeur ne valide jamais sa propre demande.
- Une remise qui augmente est une nouvelle décision commerciale ; une remise
  qui diminue reste couverte par la décision initiale.

### Décisions actées
- **D-01 — REMPLACÉE le 2026-09-08 par D-02.** « Remise maximale 10 % pour tous
  les clients » n'est plus la règle. Jamais développée : aucune reprise de
  données à prévoir.
- **D-02 (2026-09-08, M-02+M-03)** — Plafond de remise par catégorie de client :
  15 % pour les partenaires, 10 % pour les autres. Au-delà : approbation d'un
  directeur commercial. Un vendeur ne peut pas approuver sa propre demande.
  Un devis approuvé dont la remise augmente doit être revalidé ; une remise en
  baisse ne redéclenche rien.
- **D-03 (2026-09-08)** — « Partenaire » = case dédiée sur le **contact de
  facturation** du devis (`partner_invoice_id`). Ne pas confondre avec
  `commercial_partner_id` du standard Odoo, qui désigne l'entité société.

### Pièges connus
- La remise Odoo est **par ligne** (`sale.order.line.discount`) : il n'existe
  pas de « remise du devis ». Toute règle de plafond doit définir son
  agrégation (hypothèse en cours : maximum des lignes).
- L'assistant de remise globale peut produire une **ligne de remise en montant
  fixe**, invisible pour un contrôle basé sur `discount`.
- Contrainte à implémenter **côté serveur** : import, API et duplication
  contournent les onchange.

### Points ouverts
- Agrégation de la remise ; portée de l'approbation (taux exact vs plafond
  accordé) ; application après confirmation de commande ; définition du groupe
  directeur et cas où le directeur est le vendeur ; héritage société → contact.
- Verdict standard 19.0 **non vérifié** (pas d'accès aux sources ni à la base
  client lors de la revue) : à confirmer avant développement.
```

## Entrée JOURNAL.md — prête à enregistrer (non écrite)

```markdown
## 2026-09-08 — Revue fonctionnelle : plafond de remise et approbation

**Intervenant** analyste fonctionnel · **Release** non ouverte · **Livrable**
revue à déposer dans `.odoo-agents/revue_en_cours.md`

- Correction client M-02 + précisions M-03 intégrées : la règle unique à 10 %
  (D-01) est remplacée par un plafond à deux niveaux (15 % partenaires /
  10 % autres) avec circuit d'approbation directeur et interdiction de
  l'auto-approbation. D-01 n'ayant jamais été développée, aucun impact sur
  l'existant.
- Verdict standard : **hypothèse PARTIEL, non vérifiée** — revue conduite sans
  accès aux sources Odoo 19.0 ni à une copie de la base client. À reprendre
  avant tout développement : recherche d'un plafond de remise en standard,
  inventaire de la configuration en base (champ Studio ou automatisation
  préexistante), profil du projet pour trancher Studio vs module.
- Voie recommandée : contrainte **serveur** dans tous les cas ; arbitrage
  Studio/module suspendu au briefing.
- 5 questions bloquantes posées (agrégation de la remise, sens de « devis
  approuvé », portée de l'approbation, identité du directeur, héritage
  société → contact). 6 hypothèses de travail écrites pour ne pas bloquer le
  cadrage.
- 13 critères d'acceptation rédigés, dont les 5 cas soumis par le client
  (partenaire 12 %, non-partenaire 12 %, partenaire 16 %, 16→17 %, 16→14 %).
  Le cas 16→14 % reste conditionné à la question 3.
- **Aucun développement, aucun déploiement, aucun test à ce jour.**
- QA : **renforcé** (droits + montants facturés), copie client requise.
```

---

**Compte-rendu** : D-01 est remplacée, pas amendée — le plafond devient fonction du client. Verdict standard **non vérifié faute d'accès aux sources et à la base** : c'est le premier travail à reprendre. Le risque n°1 n'est pas le workflow d'approbation mais le fait que « la remise du devis » n'existe pas dans le modèle Odoo — la remise est par ligne, et l'assistant de remise globale peut la matérialiser en montant fixe hors de tout contrôle. Cinq questions bloquantes, six hypothèses écrites pour avancer malgré tout, treize critères d'acceptation. Le cas 16 → 14 % dépend entièrement de la question 3 (approbation d'un taux exact ou d'un plafond accordé) ; je retiens « reste approuvé » par lecture littérale de M-02. QA renforcée. La revue complète est à déposer dans `.odoo-agents/revue_en_cours.md` — je ne l'ai pas écrite, aucun fichier n'a été créé ni modifié.