## Compte-rendu (conversation)

- **Aucun outil dans cet exercice** : je n'ai ni lu les sources Odoo 19.0, ni inventorié une base, ni lancé `odoo_briefing.py`. Je ne peux donc **citer aucun chemin de fichier vérifié** — ce que la règle exige. Les pistes standard ci-dessous sont explicitement marquées « à vérifier » et cette vérification est la première tâche de la passation.
- **Verdict standard : non rendu**, faute de sources. Piste forte à confirmer : `picking_policy` sur `sale.order` (« livrer dès que possible / quand tout est prêt ») couvre E-01 en configuration pure ; le seuil 60 %, l'approbation et la séparation des tâches ne sont vraisemblablement pas standard → PARTIEL attendu.
- **E-01 est caduque** : E-02 la corrige. À acter, sinon le développeur implémentera deux règles contradictoires.
- **Voie recommandée** : module custom — seuil, workflow d'approbation et contrôle « pas d'auto-approbation » sortent des limites de Studio (surcharge de `button_validate`, tests Python). À confirmer après le briefing (profil du projet inconnu ici).
- **4 arbitrages client ouverts** (granularité, point de blocage, reprise, référence après variations) : hypothèses H1–H4 posées ci-dessous, développement possible sous ces hypothèses, mais H1 et H3 sont structurantes.
- **Les 5 cas demandés sont tranchés** (seuil = 48 sur 80) et étendus à 9 cas de test.
- **QA renforcée obligatoire** : droits + commandes existantes.
- Emplacement prévu (non écrit) : `.odoo-agents/revue_en_cours.md` — aucune release ouverte.

---

## Passation développeur / testeur — Livraisons partielles

*(contenu destiné à `.odoo-agents/revue_en_cours.md`)*

**Projet** Entrepôt Cobalt · **série** 19.0 · **modules concernés** `sale`, `stock`, `res.partner` · module custom proposé : `cobalt_partial_delivery`

### 1. Ce que je comprends

En tant que **responsable logistique**, je veux que les expéditions incomplètes soient autorisées automatiquement quand elles restent au-dessus d'un seuil et que le client les accepte, **afin de** ne pas bloquer le flux tout en gardant la main sur les cas dégradés.

**Problème réel** : non caractérisé. Aucune évidence fournie — pas de ticket, pas de volume, pas de fréquence, pas de coût de la situation actuelle. E-01 (« tout en une fois ») n'a jamais été implémentée, donc **on ne sait pas ce qui se passe aujourd'hui** ni combien de commandes sont concernées. C'est une lacune à combler avant le chiffrage définitif.

### 2. Verdict standard Odoo 19.0

**NON RENDU — vérification non exécutée** (pas d'accès aux sources dans cet exercice).

À faire en premier, dans `~/odoo-sources/19.0` :

| À vérifier | Attendu | Conséquence si confirmé |
|---|---|---|
| `picking_policy` sur `sale.order` (valeurs `direct` / `one`) | existe | E-01 = **configuration**, pas de code ; devient la valeur par défaut pour les contacts refusant les partiels |
| Champ « accepte les envois partiels » sur `res.partner` | probablement absent | champ custom E-03 justifié |
| Mécanisme d'approbation sur `stock.picking` (hors Enterprise / `quality`) | probablement absent | workflow custom justifié |
| Seuil en pourcentage sur la disponibilité | absent | développement justifié |
| Série 19.1 / 19.4 : apparition d'un équivalent | à comparer | si oui, **calquer les noms de champs sur le futur standard** |

**Pièges 19.0 à respecter dans le code** (à revérifier dans `SERIES_MATRIX.md`) : `res.users.group_ids` et non `groups_id` ; `models.Constraint` et non `_sql_constraints` ; `ir.model.access.csv` encore valide en 19.0 mais renommé en 19.4 — le noter pour la migration.

### 3. Voies possibles

| Voie | Effort | Ce que l'utilisateur obtient | Coût migration | Recommandée |
|---|---|---|---|---|
| Configuration seule | ~0 | Uniquement E-01 (`picking_policy`), rien du seuil ni de l'approbation | nul | non (insuffisant) |
| Studio / base | moyen | Case du contact + automatisation simple, mais pas de blocage fiable à la validation, pas de test Python, contrôle « pas d'auto-approbation » fragile en `safe_eval` | modéré | non |
| **Module custom** | moyen | Règle complète, testable, traçable | à repayer à chaque migration | **oui** |

Réserve : le profil du projet (nombre de modules custom, présence de Studio) n'a pas été relevé. Si Cobalt est en Odoo Online sans aucun module, la voie module est impossible et il faut re-arbitrer.

### 4. Règle métier consolidée (source de vérité pour le développeur)

Soit `Q` la quantité commandée, `D` la quantité proposée à l'expédition, `S = 0,60 × Q` le seuil, `A` la dernière quantité approuvée.

1. Contact de livraison **refusant** les partiels → aucune expédition tant que `D < Q`. Aucune approbation ne peut lever ce blocage *(E-02)*.
2. Contact **acceptant** les partiels et `D ≥ S` → expédition libre, sans approbation *(E-02)*.
3. Contact **acceptant** et `D < S` → approbation d'un **responsable logistique** requise *(E-02)*.
4. Approbation obtenue puis `D` **diminue** → approbation invalidée, revalidation requise *(E-02)*.
5. Approbation obtenue puis `D` **augmente** → approbation conservée *(E-02)*.
6. L'accord aux partiels est une **case dédiée du contact de livraison** (`partner_shipping_id`), pas du client facturé *(E-03)*.
7. L'approbateur doit être **différent** du demandeur *(E-03)*.

Décision actée : **E-01 est remplacée par E-02**. La règle « tout en une fois » ne subsiste que comme comportement du cas 1.

### 5. Hypothèses retenues (à défaut d'arbitrage client)

| # | Point ouvert | Hypothèse de travail | Risque si infirmée |
|---|---|---|---|
| **H1** | Granularité du calcul | Seuil évalué **ligne à ligne** : le blocage se déclenche si **au moins une ligne** est sous 60 %. Un ratio global masquerait une ligne livrée à 0 %. | **Structurant** — refonte du calcul et des tests |
| **H2** | Point de blocage | À la **validation du transfert** (`stock.picking.button_validate`), pas à la confirmation de commande ni à la réservation. L'utilisateur voit le blocage au moment où il agit. | Modéré — déplacement de la surcharge |
| **H3** | Reprise des commandes ouvertes | Case du contact **par défaut « refuse les partiels »**, cohérente avec E-01 ; règle appliquée **uniquement aux transferts créés après déploiement**, les transferts en cours restent hors périmètre. | **Structurant** — un défaut « refuse » bloque tous les transferts partiels en cours si on l'applique rétroactivement |
| **H4** | Référence après variations successives | Comparaison contre la **dernière quantité approuvée** `A`, mémorisée à chaque approbation — pas contre la quantité initiale ni contre le maximum historique. | Modéré — cas 50→40→45 change de résultat |

H1 et H3 doivent être confirmées **avant** de coder ; H2 et H4 peuvent être livrées puis ajustées.

### 6. Questions bloquantes (client)

1. **Granularité** : 60 % s'apprécie-t-il par ligne de commande, ou sur l'ensemble de la commande (en quantité ? en valeur ?) — cas d'une commande à 3 lignes dont une seule est indisponible ?
2. **Reprise** : quelle valeur par défaut pour la case sur les ~N contacts existants, et applique-t-on la règle aux transferts déjà en cours ?
3. **Référence après variations** : après 50 approuvé → 60 → 45, faut-il revalider (45 < 50, dernière approbation) ou non (45 < 60, jamais approuvé à 60) ?
4. **Point de blocage** : le préparateur doit-il être averti à la réservation, ou seulement bloqué à la validation ?
5. **Impasse organisationnelle** : que fait-on si l'unique responsable logistique est aussi le préparateur — arrêt du flux ou approbateur de secours ?

### 7. Spécification

**Modèle de données**
- `res.partner.cobalt_accept_partial_delivery` — Booléen, libellé « Accepte les expéditions partielles », onglet Ventes & Achats, défaut `False` (H3). Renseigné sur l'adresse de livraison.
- `stock.picking.cobalt_partial_state` — Sélection : `not_required` / `to_approve` / `approved` / `blocked`.
- `stock.picking.cobalt_approved_qty` — Float, quantité approuvée `A` (H4). Vide si jamais approuvé.
- `stock.picking.cobalt_approval_uid` — Many2one `res.users`, approbateur.
- `stock.picking.cobalt_request_uid` — Many2one `res.users`, demandeur.
- `stock.picking.cobalt_approval_date` — Datetime.
- Groupe `cobalt_partial_delivery.group_logistics_manager`, implique le groupe utilisateur stock existant (nom exact à relever dans les sources).

**Comportement**
- Surcharge de `button_validate` sur `stock.picking` (H2) : évaluation de la règle §4 avant l'appel `super()`.
- Contact refusant les partiels et transfert incomplet → `UserError` explicite, pas de bouton d'approbation.
- Contact acceptant, au moins une ligne sous 60 % (H1), pas d'approbation valide → `UserError` invitant à demander l'approbation.
- Bouton **Demander l'approbation** : passe en `to_approve`, renseigne `cobalt_request_uid`.
- Bouton **Approuver** : visible au groupe responsable logistique uniquement ; refuse si `env.user == cobalt_request_uid` (E-03) ; enregistre `cobalt_approved_qty` = quantités proposées au moment de l'approbation.
- Invalidation : à l'écriture des quantités, si une quantité proposée devient **strictement inférieure** à la valeur mémorisée → retour en `to_approve` (E-02, H4). Une augmentation ne change rien.
- Comparaisons **dans l'unité de mesure de la ligne de commande**, après conversion.
- Reliquats : chaque nouveau transfert est évalué indépendamment, sur la quantité restant à livrer.

**Interface** : case sur la fiche contact ; bandeau d'état + deux boutons sur le transfert ; message dans le fil de discussion à chaque demande, approbation et invalidation (traçabilité d'audit).

**Sécurité** : approbation réservée au groupe responsable logistique ; contrôle serveur `approbateur ≠ demandeur`, jamais uniquement en interface ; règle multi-société à respecter sur `stock.picking`.

**Reprise de données** : script de migration posant la valeur par défaut sur `res.partner` ; les transferts existants restent en `not_required` (H3). Aucun champ obligatoire ajouté sur un modèle peuplé.

**Hors périmètre** : achats et transferts internes, portail client, notification e-mail au client, seuil paramétrable par client ou par catégorie de produit (le 60 % est une constante de configuration globale), application rétroactive aux transferts en cours.

### 8. Cas de test — 80 unités commandées

Seuil `S = 0,60 × 80 = **48**`.

| # | Situation | Calcul | Résultat attendu | Source |
|---|---|---|---|---|
| **C1** | Contact accepte, 50 disponibles | 50 ≥ 48 | **Expédition validée sans approbation** | E-02 |
| **C2** | Même contact, 40 disponibles | 40 < 48 | **Bloqué — approbation du responsable logistique requise** | E-02 |
| **C3** | Contact refuse, 50 disponibles | partiel interdit | **Bloqué — attendre 80. Aucune approbation possible** | E-02 |
| **C4** | Approuvé à 50, abaissé à 40 | 40 < 50 → diminution | **Approbation invalidée, revalidation requise** (et 40 < 48) | E-02 |
| **C5** | Approuvé à 50, porté à 60 | 60 > 50 → augmentation | **Approbation conservée, expédition validée** | E-02 |
| C6 | Approuvé à 50, abaissé à 49 | 49 < 50 mais 49 ≥ 48 | **Revalidation requise** — la diminution prime sur le seuil | E-02, discriminant |
| C7 | Approuvé à 40, porté à 60 | augmentation, 60 ≥ 48 | Validée sans nouvelle approbation | E-02 |
| C8 | Contact refuse, 80 disponibles | complet | Validée normalement | E-02 |
| C9 | Approbation tentée par le préparateur demandeur | — | **Refus, message explicite** ; approbation par un autre responsable acceptée | E-03 |

C6 et C9 sont les deux tests qui échouent le plus souvent sur une implémentation naïve : à ne pas retirer du jeu.

**Cas non testables en l'état** : commande multi-lignes (dépend de H1) ; enchaînement 50 → 60 → 45 (dépend de H3/H4).

### 9. Critères d'acceptation

- [ ] Étant donné un contact de livraison acceptant les partiels et 50 unités sur 80, quand le préparateur valide le transfert, alors la validation passe sans approbation.
- [ ] Étant donné le même contact et 40 unités, quand le préparateur valide, alors une erreur bloque la validation et propose la demande d'approbation.
- [ ] Étant donné un contact refusant les partiels et 50 unités sur 80, quand le préparateur valide, alors la validation est refusée et aucun bouton d'approbation n'apparaît.
- [ ] Étant donné un transfert approuvé à 50, quand la quantité passe à 40, alors l'état repasse en « à approuver » et la validation est refusée.
- [ ] Étant donné un transfert approuvé à 50, quand la quantité passe à 60, alors l'état reste « approuvé » et la validation passe.
- [ ] Étant donné un transfert approuvé à 50, quand la quantité passe à 49, alors une revalidation est exigée.
- [ ] Étant donné une demande d'approbation créée par l'utilisateur X, quand X tente de l'approuver, alors le serveur refuse même si X appartient au groupe responsable logistique.
- [ ] Étant donné un contact sans valeur pour la case après migration, quand on tente une expédition partielle, alors le comportement est celui d'un refus (H3).
- [ ] Chaque changement d'état laisse une trace dans le fil de discussion du transfert.

### 10. Estimation et découpage

Ordre de grandeur, à confirmer après le briefing et l'inventaire de base :

1. **Incrément 1** — case sur `res.partner` + migration des données existantes *(livrable seul, sans effet fonctionnel)*.
2. **Incrément 2** — calcul du seuil et blocage à la validation, sans approbation (cas C1, C3, C8).
3. **Incrément 3** — workflow d'approbation, groupe, séparation demandeur/approbateur (C2, C9).
4. **Incrément 4** — invalidation sur diminution (C4, C5, C6, C7).

**Niveau QA : renforcé** — droits d'accès, séparation des tâches et modification de données existantes. Copie de la base client obligatoire pour la recette, notamment pour mesurer l'impact réel de H3 sur le parc de contacts et de commandes ouvertes.

### 11. Ce que l'utilisateur verra

Le préparateur : une validation qui échoue avec un message clair et un bouton « Demander l'approbation ». Le responsable logistique : un bouton « Approuver » sur les transferts en attente, indisponible sur ses propres demandes. Le commercial : une case « Accepte les expéditions partielles » sur la fiche contact. Matière à intégrer au guide utilisateur et à la communication de clôture.

---

## Entrée à enregistrer dans `PROJECT.md`

*(non écrite — aucun outil disponible)*

```markdown
## Compréhension métier

### Livraisons partielles (Entrepôt Cobalt, 19.0)
- L'accord aux expéditions partielles est une propriété du **contact de
  livraison** (adresse d'expédition), pas du client facturé — source E-03.
- Seuil de tolérance métier : **60 % de la quantité commandée**. Au-dessus,
  le flux est libre ; en dessous, il devient un cas dégradé qui exige un
  arbitrage humain — source E-02.
- Le contrôle est de nature « séparation des tâches » : un préparateur ne
  valide pas son propre écart — source E-03. Implique un besoin d'audit
  (qui a approuvé, quand, sur quelle quantité).
- Asymétrie assumée : une diminution de la quantité proposée casse la
  confiance accordée, une augmentation non — source E-02.

## Décisions actées

- **E-01 caduque** : la règle « toutes les commandes livrées en une fois »
  n'a jamais été implémentée et est **remplacée** par E-02. Elle ne subsiste
  que comme comportement des contacts refusant les partiels. (source : E-02,
  arbitrage client)
- **Seuil fixé à 60 %**, constante de configuration globale ; pas de seuil
  par client ni par produit dans ce périmètre. (source : E-02)
- **Approbation impossible pour un contact refusant les partiels** : le refus
  n'est pas un seuil, c'est un interdit. (source : E-02)
- **Voie recommandée : module custom**, Studio écarté (surcharge de méthode
  de validation, contrôle serveur de non-auto-approbation, tests Python).
  À reconfirmer après relevé du profil projet. (source : analyse, non arbitré
  par le client)
- **QA renforcée obligatoire** : droits + données existantes.

## Pièges connus

- Ne pas rendre la case du contact obligatoire : `res.partner` est peuplé.
- La règle porte sur `partner_shipping_id`, pas `partner_id` — erreur facile.
- Comparer les quantités dans une unité de mesure homogène.
- Le contrôle demandeur ≠ approbateur doit être serveur, pas seulement en vue.
- 19.0 : `group_ids` (et non `groups_id`), `models.Constraint` (et non
  `_sql_constraints`) ; `ir.model.access.csv` devient `ir.access.csv` en 19.4.

## En attente client (bloquant)

1. Granularité du seuil : par ligne ou sur l'ensemble de la commande.
2. Reprise : valeur par défaut de la case sur les contacts existants et sort
   des transferts déjà en cours.
3. Référence de comparaison après variations successives (50 → 60 → 45).
4. Point du workflow où bloquer (validation du transfert par défaut).
5. Approbateur de secours si l'unique responsable logistique est le demandeur.
```

## Entrée à enregistrer dans `JOURNAL.md`

*(non écrite — aucun outil disponible)*

```markdown
## 2026-09-08 — Revue fonctionnelle : livraisons partielles (E-01/E-02/E-03)

**Intervenant** : analyste fonctionnel · **Portée** : lecture / analyse seule.

**Fait**
- Consolidation des règles E-01, E-02 et E-03 en une règle unique (§4 de la
  passation) ; E-01 actée caduque.
- Passation développeur/testeur rédigée : modèle de données, comportement,
  sécurité, reprise, 9 cas de test dont les 5 demandés, découpage en
  4 incréments.
- 4 hypothèses de travail posées (H1 granularité, H2 point de blocage,
  H3 reprise, H4 référence) faute d'arbitrage ; H1 et H3 structurantes.

**Non fait — à exécuter avant tout développement**
- `odoo_briefing.py` non lancé : série confirmée 19.0 par le dossier, mais
  release en cours, profil (modules custom / Studio) et modèles existants
  inconnus.
- **Verdict standard non rendu** : sources 19.0 non consultées. À vérifier en
  priorité : `picking_policy` sur `sale.order` (couvrirait E-01 en
  configuration), absence d'un champ « accepte les partiels » sur
  `res.partner`, absence d'un workflow d'approbation sur `stock.picking`.
  Comparaison 19.1/19.4 à faire : si le standard rattrape le besoin, aligner
  les noms de champs.
- Aucun inventaire de base : pas de copie client fournie. Volumes inconnus
  (nombre de contacts, de commandes ouvertes, fréquence des cas sous seuil) —
  le chiffrage et l'impact de H3 en dépendent. **Demander la sauvegarde.**
- Problème réel non caractérisé : aucun ticket, aucune évidence chiffrée.

**Prochaine étape** : obtenir la sauvegarde client + les réponses aux
5 questions bloquantes, puis rendre le verdict standard et ouvrir la release.
```