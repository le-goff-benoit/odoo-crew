# Passation — Plafond de remise et approbation directeur

**Projet** Atelier Boréal · **série** 19.0 · **modèle pivot** `sale.order` / `sale.order.line`, `res.partner`

⚠️ **Limite de cet exercice** : je n'ai pas eu accès aux sources `~/odoo-sources/19.0`, ni au briefing, ni à une copie de la base client. Le verdict standard ci-dessous est donc **à confirmer par lecture des sources avant développement** — je signale les points exacts à vérifier plutôt que d'affirmer de mémoire. Aucun fichier n'a été écrit : les blocs `PROJECT.md` et `JOURNAL.md` en fin de note sont prêts à coller, pas enregistrés.

---

## 1. La règle actuelle (consolidée D-01 + M-02 + M-03)

En tant que **commercial**, je veux saisir une remise sur un devis dans une limite qui dépend du type de client, et demander l'accord du directeur au-delà, afin qu'aucune remise exceptionnelle ne parte sans validation.

Règle en vigueur après consolidation :

1. **Seuil** = 15 % si le client est *partenaire*, 10 % sinon.
2. **Partenaire** = case « partenaire commercial » cochée sur le **contact de facturation du devis** (`partner_invoice_id`), pas sur le client `partner_id`.
3. Remise **≤ seuil** : le commercial passe seul, aucun workflow.
4. Remise **> seuil** : approbation d'un **directeur** obligatoire avant confirmation du devis.
5. Un **vendeur ne peut pas approuver sa propre demande** (le demandeur ≠ l'approbateur).
6. Un devis **déjà approuvé** dont la remise **augmente** repasse « à approuver » ; si elle **diminue**, l'approbation reste acquise.

## 2. Ce qui remplace l'ancienne décision

| Élément | D-01 (initiale) | Règle en vigueur |
|---|---|---|
| Plafond | 10 % pour **tous** les clients | 10 % par défaut, **15 % si partenaire** |
| Dépassement | non prévu (implicitement interdit) | **autorisé sous approbation directeur** |
| Approbateur | — | directeur, **jamais le vendeur du devis lui-même** |
| Cycle de vie | — | **révision à la hausse = ré-approbation**, à la baisse = non |
| Notion de partenaire | inexistante | **nouveau champ booléen sur `res.partner`**, lu sur le contact de facturation |

→ **D-01 est remplacée, pas amendée.** Elle passe en statut « superseded » dans `PROJECT.md` (voir §7). Rien n'ayant été développé, il n'y a **aucune reprise de code** à faire ; en revanche il y a une **reprise de données** (§6) sur les devis existants.

## 3. Verdict standard Odoo 19.0 — à confirmer

**PARTIEL, probablement À DÉVELOPPER pour la partie approbation.** Points à vérifier dans les sources avant d'écrire une ligne :

- `addons/sale/` : le champ `discount` existe sur `sale.order.line` ; le groupe `sale.group_discount_per_so_line` conditionne son affichage. Vérifier aussi le wizard de remise globale (`sale.order.discount`, `addons/sale/wizard/`) — **c'est un chemin d'écriture parallèle qui doit être couvert par le contrôle**, sinon la règle se contourne en trois clics.
- **Aucun plafond de remise paramétrable** n'existe à ma connaissance en standard Community. À confirmer par `grep -rn "max_discount\|discount_limit" $S/addons/*/models/*.py`.
- **Enterprise** : les *règles d'approbation* de Studio (`addons/studio/` ou `web_studio`, modèle de type `studio.approval.rule`) couvrent nativement « ce bouton exige l'accord d'un groupe » **et** la règle « l'approbateur ne peut pas être l'auteur ». Si le client a Enterprise, **c'est la première voie à instruire** : elle fournit 70 % du besoin sans code. Ce qu'elle ne fournit pas : le **seuil conditionnel** (10/15 selon partenaire) et la **ré-approbation sur hausse**.
- **Série suivante (19.1/19.4)** : à vérifier dans `SERIES_MATRIX.md`. Si une notion de plafond de remise apparaît, calquer les noms de champs. Rappel de série pour 19.x : `res.users.groups_id` → `group_ids`, `_sql_constraints` → `models.Constraint`, `ir.model.access.csv` → `ir.access.csv` en 19.4.

**Piège de nommage à ne pas rater** : ne **jamais** nommer le nouveau booléen `commercial_partner_id` ni quoi que ce soit d'approchant — `commercial_partner_id` existe déjà sur `res.partner` en standard et désigne la société mère du contact. Nom proposé : `is_trade_partner` (module) ou `x_is_trade_partner` (Studio), libellé « Partenaire commercial ».

## 4. Voies

| Voie | Effort | Ce que l'utilisateur obtient | Coût migration | Recommandée |
|---|---|---|---|---|
| Configuration seule | ~0 | rien : pas de plafond conditionnel en standard | nul | non |
| Studio + règle d'approbation (si Enterprise) | faible | le workflow d'approbation et la séparation demandeur/approbateur ; seuil conditionnel en contrainte `safe_eval`, ré-approbation fragile | moyen | **oui si Enterprise et pas de module custom au projet** |
| Module custom | moyen | tout, testable, seuil conditionnel et high-water mark propres | à chaque migration | **oui si le projet a déjà des modules** |

Le briefing (nombre de modules custom, présence de Studio en base) tranche. La logique « ré-approbation si la remise augmente » demande de **comparer une valeur stockée à la valeur courante dans `write()`** : c'est hors des capacités de Studio (pas de surcharge de méthode). Si la voie Studio est retenue, ce point précis doit être dégradé ou codé.

## 5. Les cinq exemples demandés

Hypothèse de lecture retenue : « la remise du devis » = **remise maximale parmi les lignes** (voir Q1 — c'est la question bloquante n°1).

| # | Cas | Résultat attendu |
|---|---|---|
| 1 | **Partenaire à 12 %** | ✅ **Autorisé sans approbation.** 12 ≤ 15. Le devis reste confirmable directement par le commercial. |
| 2 | **Non-partenaire à 12 %** | ⛔ **Approbation directeur requise.** 12 > 10. Le devis passe en « Approbation demandée », le bouton *Confirmer* est bloqué. Piège de test : mêmes 12 %, résultat opposé au cas 1 — c'est le cœur de la règle. |
| 3 | **Partenaire à 16 %** | ⛔ **Approbation directeur requise.** 16 > 15. |
| 4 | **Devis approuvé à 16 %, passe à 17 %** | ⛔ **L'approbation tombe, retour en « Approbation demandée ».** Hausse ⇒ revalidation. Le nom de l'approbateur précédent et la date sont conservés en historique mais l'état d'approbation est réinitialisé. |
| 5 | **Devis approuvé à 16 %, passe à 14 %** | ✅ **Reste approuvé.** Baisse ⇒ pas de revalidation, **même si 14 % reste au-dessus du seuil** (cas d'un non-partenaire, seuil 10). C'est bien ce que dit M-02 pris à la lettre : la baisse ne réinstruit jamais. Point à faire confirmer explicitement (Q3) car il est contre-intuitif pour un contrôleur de gestion. |

**Cas dérivé non couvert par M-02, à arbitrer (Q4)** : approuvé à 16 %, descendu à 14 %, puis **remonté à 15 %**. Lecture « valeur précédente » → 14 → 15 est une hausse, donc revalidation. Lecture « plus haut niveau déjà approuvé » (*high-water mark*) → 15 ≤ 16, déjà couvert, pas de revalidation. Je recommande le **high-water mark** : il évite de ré-instruire une remise que le directeur a déjà validée à un niveau supérieur, et il est plus simple à expliquer au commercial. À trancher avant développement, car cela change le modèle de données (`approved_discount` stocké).

## 6. Questions encore ouvertes

**BLOQUANTES** (sans réponse, risque de tout refaire) :

1. **Remise par ligne ou remise globale ?** Odoo porte `discount` sur `sale.order.line`. Un devis peut avoir 3 % sur une ligne et 20 % sur une autre. La règle porte-t-elle sur (a) le **max des lignes**, (b) la **remise globale équivalente** en montant (`(total sans remise − total) / total sans remise`), ou (c) **chaque ligne indépendamment** ? La (b) est la plus proche du langage commercial mais laisse passer une ligne à 40 % compensée par des lignes à 0 %. **Toute la spec en dépend.**
2. **Les remises issues des listes de prix comptent-elles ?** Une pricelist peut alimenter `discount` automatiquement. Si oui, un client avec une pricelist à 12 % déclenche une demande d'approbation à chaque devis — ingérable. Si non, il faut distinguer remise automatique et remise manuelle, ce qui n'est pas trivial.
3. **Une baisse au-dessus du seuil reste-t-elle approuvée ?** (cas 5, non-partenaire de 16 % à 14 % alors que le seuil est 10 %). Confirmer que oui.
4. **Comparaison à la valeur précédente ou au plus haut niveau approuvé ?** (§5, cas dérivé).
5. **Qui approuve quand le directeur est lui-même le vendeur du devis ?** M-03 interdit l'auto-approbation. S'il n'y a qu'un directeur, ses propres devis remisés sont bloqués définitivement. Faut-il un second approbateur, une délégation, ou une exception ?

**À ARBITRER** (on peut avancer sous hypothèse) :

- Le changement de **contact de facturation** après approbation (partenaire → non-partenaire) fait baisser le seuil sans changer la remise : revalidation ou non ?
- **Ajout d'une ligne** remisée après approbation : traité comme une hausse.
- Une **commande confirmée** puis modifiée (remise augmentée sur un bon de commande) : la règle s'applique-t-elle encore, ou seulement en état devis ?
- **Multi-société** : le directeur approbateur est-il par société ?
- **Portail / mobile** : le client voit-il quoi que ce soit ? (réponse attendue : non).
- **Devis existants en base** : combien sont au-dessus des seuils ? Sans copie de la base, ce volume est inconnu — à mesurer avant de choisir la stratégie de reprise.

## 7. Spécification pour le développeur

**Modèle de données**
- `res.partner.is_trade_partner` (Boolean, « Partenaire commercial »), visible sur l'onglet Ventes & Achats. **Ne pas** le nommer `commercial_partner_*`.
- `sale.order.discount_limit` (Float, **calculé, non stocké** ou stocké selon les besoins de recherche) : `15.0` si `partner_invoice_id.is_trade_partner` sinon `10.0`. Dépendance `@api.depends('partner_invoice_id.is_trade_partner')`.
- `sale.order.effective_discount` (Float, calculé, stocké) : la valeur retenue en Q1.
- `sale.order.discount_approval_state` (Selection : `not_required` / `to_approve` / `approved`).
- `sale.order.discount_approved_by` (Many2one `res.users`), `discount_approved_on` (Datetime), `approved_discount` (Float — le niveau approuvé, pour le high-water mark si Q4 = HWM).
- Groupe `group_discount_approver` (« Approbation des remises »).

**Comportement**
- Recalcul de `discount_approval_state` sur toute écriture touchant les lignes, la remise ou `partner_invoice_id`.
- Passage à `to_approve` dès que `effective_discount > discount_limit`.
- Bouton *Approuver la remise* visible aux membres de `group_discount_approver`, **désactivé si `env.user == order.user_id`** (message explicite : « Vous ne pouvez pas approuver votre propre demande de remise »).
- `action_confirm()` surchargé : `raise UserError` si `discount_approval_state == 'to_approve'`.
- **Couvrir le wizard `sale.order.discount`** : la remise posée par le wizard doit déclencher le même recalcul.
- Traçabilité : approbation et retombée d'approbation postées en message sur le devis (`message_post`), avec l'ancien et le nouveau taux.

**Sécurité** — le contrôle doit vivre dans le modèle Python (pas seulement en `attrs`/`invisible` de vue), sinon il se contourne par import, API XML-RPC ou action serveur.

**Reprise de données** — `is_trade_partner` à `False` par défaut : quelqu'un doit fournir la liste des partenaires à cocher. Les devis existants au-dessus du seuil doivent être initialisés en `approved` (grand-père) ou `to_approve` : **décision à prendre**, elle peut bloquer des devis en cours.

**Hors périmètre** — les remises sur factures (`account.move`), les abonnements, les listes de prix elles-mêmes, tout reporting sur les remises exceptionnelles.

## 8. Critères d'acceptation (pour le testeur)

- [ ] Étant donné un devis dont le contact de facturation a « Partenaire commercial » coché, quand le commercial saisit 12 % de remise, alors aucune approbation n'est demandée et *Confirmer* fonctionne.
- [ ] Étant donné un devis dont le contact de facturation n'est **pas** partenaire, quand le commercial saisit 12 %, alors le devis passe « Approbation demandée » et *Confirmer* lève une erreur explicite.
- [ ] Étant donné un devis partenaire, quand la remise passe à 16 %, alors l'approbation est demandée.
- [ ] Étant donné un devis approuvé à 16 %, quand la remise passe à 17 %, alors l'état repasse à « Approbation demandée » et *Confirmer* est de nouveau bloqué.
- [ ] Étant donné un devis approuvé à 16 %, quand la remise passe à 14 %, alors le devis **reste approuvé** et reste confirmable.
- [ ] Étant donné un devis en attente d'approbation, quand le vendeur du devis est aussi membre du groupe approbateur, alors il ne peut pas approuver et le message le lui explique.
- [ ] Étant donné un devis en attente, quand un autre utilisateur du groupe approbateur approuve, alors l'état passe à « Approuvé » avec nom et date tracés dans le chatter.
- [ ] Étant donné un devis approuvé, quand on remplace le contact de facturation par un non-partenaire (seuil 15 → 10) sans changer la remise à 12 %, alors le comportement est **celui décidé en arbitrage** — test à écrire une fois la question tranchée.
- [ ] Étant donné une remise posée via le **wizard de remise globale** au-dessus du seuil, alors l'approbation est demandée de la même façon que par saisie de ligne.
- [ ] Étant donné un utilisateur sans droit d'approbation, quand il tente d'écrire directement `discount_approval_state = 'approved'` par l'API, alors l'écriture est refusée.

**Niveau QA : renforcé** — la fonction touche les prix de vente, les droits d'accès et des devis existants en base. Test obligatoire sur copie de la base client, jamais en direct.

## 9. Découpage

1. Champ `is_trade_partner` + calcul du seuil, sans workflow (livrable seul, visible immédiatement).
2. Workflow d'approbation + blocage de `action_confirm` + séparation demandeur/approbateur.
3. Ré-approbation sur hausse (dépend de Q4).
4. Couverture du wizard de remise globale et des chemins d'écriture annexes.

## 10. Ce que l'utilisateur verra

Une case « Partenaire commercial » sur la fiche contact ; sur le devis, un bandeau « Approbation de remise demandée » et un bouton *Approuver la remise* réservé aux directeurs ; un message d'erreur au moment de confirmer un devis non approuvé ; des messages de suivi dans le chatter à chaque approbation ou retombée.

---

## Entrées prêtes à enregistrer

**À écrire dans `<projet>/.odoo-agents/PROJECT.md`** — aucune release n'étant ouverte, la revue elle-même irait dans `.odoo-agents/revue_en_cours.md`. Je n'ai rien écrit.

```markdown
### Décisions actées

- **D-01 — Remise commerciale plafonnée à 10 % pour tous les clients.**
  _Statut : REMPLACÉE par D-02 (M-02 du client). Jamais développée, aucun code à reprendre._

- **D-02 — Plafond de remise conditionnel avec approbation directeur.** (source : M-02, précisée par M-03)
  - Seuil de remise : **15 % pour les clients partenaires**, **10 % pour les autres**.
  - « Partenaire » = case « Partenaire commercial » cochée sur le **contact de facturation du devis**
    (`partner_invoice_id`), et non sur le client du devis.
  - Au-delà du seuil : **approbation d'un directeur** obligatoire avant confirmation du devis.
  - **Un vendeur ne peut pas approuver sa propre demande** (demandeur ≠ approbateur).
  - Un devis approuvé dont la remise **augmente** repasse en attente d'approbation ;
    une **baisse** ne déclenche pas de revalidation.
  - Nommage : le booléen ne doit **pas** s'appeler `commercial_partner_*`
    (collision avec `res.partner.commercial_partner_id` du standard). Retenu : `is_trade_partner`.

### Compréhension métier

- Deux catégories de clients coexistent chez Atelier Boréal : les **partenaires commerciaux**,
  qui bénéficient d'une latitude de négociation supérieure (15 %), et les autres (10 %).
  La qualité de partenaire se porte au niveau du **contact de facturation**, pas de l'interlocuteur
  du devis : c'est l'entité qui paie qui détermine la latitude.
- La remise exceptionnelle n'est pas interdite mais **contrôlée** : le dépassement est un acte
  de direction, pas une erreur à bloquer.
- L'asymétrie hausse/baisse traduit une logique de risque : le directeur a validé un plafond,
  descendre en dessous ne l'expose pas davantage.

### Pièges connus

- `commercial_partner_id` est un champ standard d'Odoo (société mère du contact) : ne jamais
  réutiliser ce nom pour la notion de partenaire commercial métier.
- La remise a plusieurs chemins d'écriture : ligne de commande, wizard de remise globale
  (`sale.order.discount`), listes de prix, import. Tout contrôle posé en vue seulement est contournable.

### Points ouverts

- Assiette de la règle : remise par ligne, max des lignes, ou remise globale en montant ? (bloquant)
- Les remises issues des listes de prix entrent-elles dans le contrôle ? (bloquant)
- Comparaison à la valeur précédente ou au plus haut niveau déjà approuvé ? (bloquant)
- Approbateur de secours quand le directeur est le vendeur du devis. (bloquant)
- Traitement des devis existants déjà au-dessus des seuils à la mise en service.
```

**À écrire dans `JOURNAL.md`** :

```markdown
## 2026-09-08 — Revue fonctionnelle : plafond de remise et approbation directeur

**Intervenant** analyste fonctionnel · **série** 19.0 · **modules** sale, res.partner
**Statut** revue produite, développement non démarré, aucun déploiement ni test.

- Consolidation de M-02 (client) et M-03 (réponse humaine) : la décision D-01
  (10 % pour tous) est **remplacée** par D-02 (10 % / 15 % selon partenaire,
  approbation directeur au-delà, pas d'auto-approbation, revalidation sur hausse seule).
  D-01 n'ayant jamais été développée, il n'y a pas de dette de code.
- Verdict standard **non tranché faute d'accès aux sources 19.0 et à une copie de la base** :
  à confirmer avant développement, notamment l'existence de règles d'approbation Studio
  (Enterprise) qui couvriraient le workflow et la séparation demandeur/approbateur sans code.
  Le seuil conditionnel et la ré-approbation sur hausse resteront à développer dans tous les cas.
- Cinq scénarios de référence arbitrés et documentés (partenaire 12 % → OK ;
  non-partenaire 12 % → approbation ; partenaire 16 % → approbation ;
  approuvé 16 → 17 % → revalidation ; approuvé 16 → 14 % → reste approuvé).
- 5 questions bloquantes ouvertes, dont l'assiette de la règle (remise par ligne
  vs remise globale) qui conditionne toute la spécification.
- Piège de nommage identifié : collision avec `res.partner.commercial_partner_id`.
- **Niveau QA fixé à renforcé** (prix de vente, droits, données existantes) :
  copie de la base client obligatoire avant recette.

**Prochaine étape** : obtenir les réponses aux 5 questions bloquantes et une sauvegarde
de la base, puis ouvrir la release et confronter la demande aux sources 19.0.
```