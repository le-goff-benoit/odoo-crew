## Cadre de cet exercice

Je travaille **sans outils** : je n'ai lancé ni `odoo_briefing.py`, ni `odoo-config-inventory.sh`, ni aucun `grep` dans `~/odoo-sources/19.0`. Aucun chemin de fichier n'est donc cité comme preuve, et **le verdict standard n'est pas rendu** : il reste à faire, c'est la première tâche de la passation. Tout ce qui touche au standard Odoo 19.0 ci-dessous est marqué comme *piste à vérifier*, pas comme constat. Rien n'a été écrit sur disque.

---

# Revue fonctionnelle — Plafond de remise commerciale et approbation directeur

**Projet** Atelier Boréal · **série** 19.0 · **modèle concerné** `sale.order` (+ `res.partner`)

## 1. Ce que je comprends

En tant que commercial, je veux appliquer une remise sur un devis dans la limite autorisée pour ce client, et déclencher une approbation du directeur au-delà, afin que les marges soient tenues sans bloquer les cas légitimes.

Périmètre : devis de vente uniquement ; plafond variable selon la qualité « partenaire commercial » du contact de facturation ; approbation hiérarchique au-delà du plafond ; revalidation d'un devis approuvé dont la remise augmente.

**Problème réel** : non établi. Aucune évidence fournie — pas de ticket, pas de volume, pas de fréquence, pas de coût constaté des remises hors normes. Je ne sais pas combien de devis par mois dépasseraient 10 %, ni combien de contacts porteraient la case « partenaire ». **C'est une lacune à combler avant le développement** : elle conditionne le choix Studio / module et le dimensionnement de l'écran d'approbation.

## 2. Règle actuelle — la version qui fait foi

Consolidation de D-01 + M-02 + M-03 :

| Cas | Plafond sans approbation |
|---|---|
| Contact de facturation du devis avec « partenaire commercial » coché | **15 %** |
| Tous les autres | **10 %** |
| Au-delà du plafond applicable | **approbation du directeur obligatoire** |

Compléments :
- « Partenaire » se lit sur le **contact de facturation du devis** (`partner_invoice_id`), pas sur le client du devis (`partner_id`). Les deux peuvent différer.
- **Un vendeur ne peut pas approuver sa propre demande**, même s'il a par ailleurs le droit d'approuver.
- Un devis déjà approuvé dont la remise **augmente** repasse en attente d'approbation ; s'il **diminue**, l'approbation reste acquise.

### Ce qui remplace l'ancienne décision

**D-01 (remise maximale 10 % pour tous les clients) est révoquée et remplacée par D-02.** D-01 n'a jamais été développée : il n'y a **aucun code, aucune donnée, aucune configuration à défaire**. La substitution est purement documentaire. D-01 doit être marquée « révoquée par D-02 » dans `PROJECT.md` et non supprimée, pour que la trace du changement de doctrine reste lisible.

Différences de fond entre D-01 et D-02 : (a) le plafond devient variable au lieu d'être uniforme ; (b) le plafond cesse d'être un **maximum dur** pour devenir un **seuil d'approbation** — au-dessus, ce n'est plus interdit, c'est soumis à validation ; (c) apparition d'un état de workflow sur le devis, donc d'un objet de sécurité (qui approuve) et d'un cycle de vie (revalidation).

Le point (b) est le vrai changement structurant : on passe d'une contrainte de saisie à un workflow d'approbation. Le coût n'est pas du même ordre.

## 3. Verdict standard Odoo 19.0 — **NON RENDU**

À produire avant toute ligne de code. Pistes à confirmer dans les sources, dans cet ordre :

1. **Règles d'approbation Studio (Enterprise)** — un mécanisme générique d'approbation sur bouton, avec notion d'approbateur exclusif (interdisant l'auto-approbation), existe à ma connaissance dans l'offre Studio. **À vérifier** : présence dans la série 19.0, capacité à conditionner la règle à un domaine dynamique dépendant du plafond, et gestion de l'invalidation quand la valeur augmente après approbation. Si ce dernier point n'est pas couvert nativement, le delta est précisément là.
2. **Assistant de remise standard sur `sale.order`** — un mécanisme d'application de remise globale existe côté vente. **À vérifier** : offre-t-il un plafond configurable ? Probablement non, mais c'est le point d'accroche naturel.
3. **Champ « partenaire » existant sur `res.partner`** — il existe des notions de partenaire revendeur avec niveau/grade dans le domaine CRM. **À vérifier** : est-ce déjà installé chez Atelier Boréal, et la case demandée doit-elle réutiliser un champ existant plutôt que d'en créer un ? Créer un booléen qui double un champ standard ou un champ Studio déjà en base serait un défaut.
4. **Base client** — inventaire de la copie obligatoire : un champ Studio « partenaire » et/ou une automatisation de contrôle de remise peuvent déjà exister. Aucun développement ne doit être lancé avant ce relevé.
5. **Série 19.1 / 19.4** — vérifier qu'Odoo n'ajoute pas ce contrôle en standard dans la série suivante ; si oui, calquer les noms de champs sur le futur standard pour que la migration soit une suppression.

Rappels de série à ne pas oublier au développement : `res.users.groups_id` → `group_ids`, `_sql_constraints` → `models.Constraint`, et `ir.model.access.csv` → `ir.access.csv` à partir de 19.4.

## 4. Voies possibles

Le choix dépend du profil du projet, que je n'ai pas pu relever (nombre de modules custom, présence de Studio, hébergement Online ou non). Grille de décision à appliquer une fois le briefing lancé :

| Voie | Effort | Ce que l'utilisateur obtient | Coût migration | Recommandée |
|---|---|---|---|---|
| Configuration seule | nul | rien : aucun paramètre standard ne porte un plafond de remise | nul | non |
| Studio / configuration en base | moyen | case partenaire, champ calculé de plafond, règle d'approbation, contrôle à la confirmation | faible à moyen | **oui si Online/SaaS, ou si le projet est déjà Studio-only** |
| Module custom | moyen à élevé | idem + tests Python, invalidation d'approbation propre, messages précis | payé à chaque migration | **oui si le projet a déjà des modules, ou si Studio bute sur l'invalidation** |

Limite Studio à surveiller précisément ici : la **revalidation automatique quand la remise augmente** suppose de réagir à une écriture et de comparer à une valeur mémorisée. C'est faisable par automatisation, mais sans test Python. Si le contrôle est jugé critique pour la marge, la voie module est plus sûre.

## 5. Contradictions et risques

| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|---|---|---|---|
| 1 | **majeure** | Granularité de la remise non définie | En standard, la remise est portée **par ligne**. « 12 % » désigne-t-il une ligne, la moyenne pondérée du devis, ou la remise globale appliquée par l'assistant ? Un devis à 3 lignes remisées 0 / 0 / 30 % est-il à 30 % ou à 10 % ? Les deux lectures donnent des résultats opposés sur les exemples fournis. | Question bloquante n° 1. Recommandation : remise **effective au niveau devis** = (montant sans remise − montant net) / montant sans remise, seul indicateur qui ne se contourne pas en découpant les lignes. |
| 2 | **majeure** | Remises issues des listes de prix | Une liste de prix peut produire mécaniquement plus de 10 % sans intervention du commercial. Si elles comptent dans le calcul, tout un pan du catalogue passe en approbation permanente et le dispositif s'effondre. | Question bloquante n° 2. Trancher : contrôler la remise saisie, ou la remise totale. |
| 3 | **majeure** | Définition d'« approuvé » | M-02 parle d'un « devis déjà approuvé ». Est-ce l'approbation directeur, ou la confirmation du devis en commande par le client ? Les deux existent et ne sont pas au même endroit du cycle. | Question bloquante n° 3. |
| 4 | moyenne | Auto-approbation par le directeur | Si le directeur est lui-même vendeur sur un devis, la règle M-03 le bloque, et personne d'autre ne peut approuver. Blocage total, découvert en production. | Prévoir un approbateur suppléant, ou nommer au moins deux membres dans le groupe d'approbation. À arbitrer. |
| 5 | moyenne | Changement du contact de facturation après approbation | Passer d'un contact partenaire à un non-partenaire fait baisser le plafond sans que la remise bouge : le devis devient non conforme, et la règle « seule une hausse revalide » ne le rattrape pas. Faille exploitable. | Recommandation : recalculer l'exigence d'approbation sur **conformité au plafond courant**, pas seulement sur la variation de la remise. |
| 6 | moyenne | Reprise des devis existants | Des devis ouverts dépassent probablement déjà 10 %. À la mise en service, sont-ils bloqués rétroactivement ? | Recommandation : n'appliquer la règle qu'aux devis créés ou modifiés après la mise en service ; ne pas invalider l'existant en masse. Volume à mesurer sur la copie. |
| 7 | moyenne | Multi-société | Le plafond 10 / 15 % est-il commun à toutes les sociétés ? Le groupe directeur aussi ? | Recommandation : plafonds en paramètres de société, pas en dur dans le code. |
| 8 | mineure | Portail client | Le client doit-il voir « en attente d'approbation interne » sur son devis ? Non souhaitable. | Recommandation : état d'approbation invisible au portail. |
| 9 | mineure | Modification post-confirmation | Une remise modifiée sur une commande déjà confirmée relève-t-elle du même contrôle ? | Hors périmètre par défaut, à confirmer. |

## 6. Questions bloquantes

1. **Granularité** : le seuil s'applique-t-il à la remise d'une ligne, ou à la remise effective de l'ensemble du devis ?
2. **Périmètre du calcul** : les remises issues des listes de prix comptent-elles dans le pourcentage contrôlé, ou seulement la remise saisie manuellement ?
3. **Sens d'« approuvé »** dans M-02 : approbation directeur, ou confirmation du devis ?
4. **Approbateur** : quel groupe précisément, et qui approuve quand le seul approbateur est le vendeur du devis ?
5. **Champ partenaire** : la case existe-t-elle déjà (champ standard, champ Studio en base), ou est-elle à créer ? Réponse attendue de l'inventaire de la copie, pas du client.

Cinq questions : la demande est à la limite de maturité, mais elle est traitable.

## 7. Hypothèses retenues à défaut de réponse

Le développeur les applique **telles quelles** si les réponses tardent, et les signale au testeur :

- **H1** — Le seuil porte sur la remise **effective du devis entier** : `(total hors remise − total net) / total hors remise`, arrondi à deux décimales.
- **H2** — Seule la remise portée par le champ remise des lignes est comptée ; les prix issus des listes de prix ne sont pas requalifiés en remise.
- **H3** — « Approuvé » = **approbation directeur accordée**, indépendante de la confirmation client.
- **H4** — Un devis dont la remise dépasse le plafond et qui n'est pas approuvé **ne peut pas être confirmé** ; la saisie de la remise elle-même reste libre.
- **H5** — L'approbation est mémorisée avec **le taux approuvé**. Toute valeur ultérieure inférieure ou égale à ce taux reste couverte ; toute valeur supérieure exige une nouvelle approbation.
- **H6** — L'exigence d'approbation est réévaluée sur la situation courante : si la remise repasse sous le plafond, le devis est confirmable sans approbation, quel qu'ait été son passé.
- **H7** — Les plafonds 10 % et 15 % sont des paramètres de société, modifiables sans intervention technique.
- **H8** — Aucune reprise rétroactive sur les devis existants à la mise en service.

## 8. Traitement des exemples demandés

Sous H1 à H8, avec un devis à ligne unique pour la lisibilité :

| # | Situation | Plafond applicable | Résultat attendu |
|---|---|---|---|
| A | **Partenaire, 12 %** | 15 % | **Aucune approbation.** Devis confirmable directement par le commercial. Aucun message, aucun blocage. |
| B | **Non-partenaire, 12 %** | 10 % | **Approbation directeur requise.** Le devis reste saisissable, mais la confirmation est refusée tant que l'approbation n'est pas accordée. Le commercial voit qu'il dépasse et par qui cela doit être validé. |
| C | **Partenaire, 16 %** | 15 % | **Approbation directeur requise.** Le statut « partenaire » relève le plafond mais ne dispense pas de l'approbation au-delà de 15 %. |
| D | **Devis approuvé à 16 %, passé à 17 %** | 15 % | **L'approbation tombe.** Le devis repasse en attente d'approbation, la confirmation est de nouveau bloquée. 17 % dépasse le taux approuvé (16 %). Une nouvelle décision du directeur est nécessaire, et elle ne peut pas venir du vendeur du devis. |
| E | **Devis approuvé à 16 %, passé à 14 %** | 15 % | **L'approbation reste valable.** Aucune revalidation. Le devis est confirmable. Deux raisons concordantes : la remise baisse par rapport au taux approuvé (H5), et 14 % est de toute façon sous le plafond partenaire de 15 % (H6). |

Précision utile au testeur : l'exemple E est **surdéterminé** — il serait validé par deux règles différentes. Il ne prouve donc pas à lui seul que H5 est bien implémentée. Il faut lui adjoindre un cas discriminant, décrit au § 10 (cas F).

## 9. Spécification

### Modèle de données
- `res.partner` : booléen « partenaire commercial ». **Réutiliser un champ existant si l'inventaire de la copie en révèle un** ; n'en créer un que si aucun ne convient.
- `sale.order` : remise effective (calculée, stockée pour la recherche et le filtrage), plafond applicable (calculé depuis le partenaire de facturation et les paramètres société), indicateur « approbation requise », état d'approbation, taux approuvé, approbateur, date d'approbation.
- Paramètres de société : plafond standard (défaut 10 %), plafond partenaire (défaut 15 %).
- Le plafond applicable se lit sur le **contact de facturation** du devis. Si celui-ci est vide, retomber sur le client du devis, et le documenter.

### Comportement
- Recalcul du plafond et de la remise effective à chaque modification des lignes ou du contact de facturation.
- Approbation requise dès que remise effective > plafond applicable.
- Confirmation refusée si approbation requise et non accordée, avec message explicite indiquant la remise, le plafond et le motif.
- Approbation accordée : mémorise le taux au moment de l'approbation.
- Toute remise ultérieure strictement supérieure au taux approuvé invalide l'approbation.
- Toute remise inférieure ou égale au taux approuvé la conserve.
- Toute remise repassant sous le plafond rend le devis confirmable sans approbation.

### Interface
- Case « partenaire commercial » sur la fiche contact.
- Sur le devis : remise effective, plafond applicable, statut d'approbation visibles sans clic.
- Bouton d'approbation visible **uniquement** pour les approbateurs habilités, et **masqué au vendeur du devis**.
- Journalisation au fil de discussion du devis : demande, approbation, invalidation, avec auteur et taux.

### Sécurité
- Groupe « approbateur de remise ». L'appartenance seule ne suffit pas : le contrôle d'auto-approbation est une règle métier, appliquée **côté serveur**, pas seulement par masquage du bouton. Un test doit prouver que l'appel direct est refusé.
- Le vendeur ne doit pas pouvoir modifier l'état d'approbation ni le taux approuvé.

### Reprise de données
- Aucune modification des devis existants.
- Aucun champ obligatoire ajouté sur un modèle peuplé.
- La case partenaire est décochée par défaut : conséquence directe, tous les contacts partenaires actuels doivent être cochés manuellement ou par import avant la mise en service. **Cette liste est à demander au client** — sans elle, tous les partenaires basculent à 10 % du jour au lendemain. C'est le principal risque de mise en service.

### Hors périmètre
- Remises sur commandes confirmées, factures, notes de crédit.
- Remises sur abonnements et devis récurrents.
- Notification par courriel de l'approbateur (à traiter dans un second incrément si demandé).
- Historique ou reporting des dérogations.

## 10. Critères d'acceptation

- [ ] Étant donné un contact de facturation partenaire, quand le devis porte 12 % de remise, alors aucune approbation n'est requise et le devis est confirmable.
- [ ] Étant donné un contact de facturation non partenaire, quand le devis porte 12 %, alors l'approbation est requise et la confirmation est refusée avec un message citant le plafond de 10 %.
- [ ] Étant donné un contact de facturation partenaire, quand le devis porte 16 %, alors l'approbation est requise.
- [ ] Étant donné un devis partenaire approuvé à 16 %, quand la remise passe à 17 %, alors l'approbation est invalidée et la confirmation est de nouveau refusée.
- [ ] Étant donné un devis partenaire approuvé à 16 %, quand la remise passe à 14 %, alors l'approbation reste valable et le devis est confirmable.
- [ ] **Cas F, discriminant** : étant donné un devis **non partenaire** approuvé à 16 %, quand la remise passe à 14 %, alors le devis reste confirmable sans nouvelle approbation — alors même que 14 % dépasse toujours le plafond de 10 %. Ce cas seul prouve que la baisse est bien couverte par le taux approuvé et non par un simple retour sous le plafond.
- [ ] Étant donné un devis approuvé à 16 % ramené à 14 % puis remonté à 15 %, alors aucune nouvelle approbation n'est requise (15 ≤ 16).
- [ ] Étant donné un devis approuvé à 16 % ramené à 14 % puis remonté à 17 %, alors une nouvelle approbation est requise.
- [ ] Étant donné un devis en attente d'approbation, quand son propre vendeur tente d'approuver, alors l'action est refusée — y compris par appel direct au serveur sans passer par le bouton.
- [ ] Étant donné un devis approuvé porté par un contact de facturation partenaire à 15 %, quand le contact de facturation est remplacé par un non-partenaire, alors le devis n'est plus confirmable sans approbation.
- [ ] Étant donné un devis à plusieurs lignes remisées inégalement, quand la remise effective de l'ensemble dépasse le plafond, alors l'approbation est requise — le découpage en lignes ne permet pas de contourner le contrôle.
- [ ] Étant donné une remise exactement égale au plafond (10 % non partenaire, 15 % partenaire), alors **aucune approbation n'est requise** : le seuil est un maximum inclus.
- [ ] Étant donné un devis en attente d'approbation, quand le client l'ouvre depuis le portail, alors aucune mention de l'approbation interne ne lui est visible.
- [ ] Étant donné les devis existants au moment de la mise en service, quand ils ne sont pas modifiés, alors leur état de confirmation est inchangé.

## 11. Estimation et découpage

Trois incréments livrables indépendamment, dans cet ordre :

1. **Socle de qualification** — case partenaire, plafond applicable, remise effective, affichage. Aucun blocage. Permet de mesurer sur la copie combien de devis dépasseraient, donc de valider le dimensionnement avant d'aller plus loin. C'est aussi ce qui comble le trou d'évidence du § 1.
2. **Blocage et approbation** — groupe approbateur, bouton, refus de confirmation, interdiction d'auto-approbation, journalisation.
3. **Cycle de revalidation** — mémorisation du taux approuvé, invalidation à la hausse, conservation à la baisse.

**Niveau QA : renforcé, obligatoire.** Deux motifs cumulés : le dispositif crée un droit d'approbation (sécurité), et il porte sur des données existantes en volume (devis ouverts). Copie client indispensable. Le test d'auto-approbation par appel serveur direct n'est pas optionnel.

## 12. Ce que l'utilisateur verra

Le commercial voit sur son devis la remise effective, le plafond auquel il a droit pour ce client, et un statut d'approbation. Au-delà du plafond, la confirmation lui est refusée avec un message qui explique pourquoi et ce qui manque. Le directeur voit un bouton d'approbation sur les devis concernés, sauf sur ceux dont il est le vendeur. Le client ne voit rien de nouveau. Sur la fiche contact, une case « partenaire commercial » apparaît.

Communication de mise en service à prévoir : **les contacts partenaires doivent être cochés avant la bascule**, faute de quoi ils seront traités à 10 %.

---

# Entrées à enregistrer

Je n'ai écrit aucun fichier. Les deux blocs suivants sont prêts à être collés tels quels.

## Pour `.odoo-agents/PROJECT.md`

```markdown
### Décisions actées

- **D-01 — Remise commerciale plafonnée à 10 % pour tous les clients.**
  *Statut : RÉVOQUÉE, remplacée par D-02 (M-02 du client).* Jamais développée :
  aucun code, aucune donnée, aucune configuration à défaire. Conservée pour la
  trace du changement de doctrine.

- **D-02 — Plafond de remise différencié avec approbation directeur.**
  Remplace D-01. Plafond sans approbation : 15 % si la case « partenaire
  commercial » est cochée sur le **contact de facturation du devis**, 10 % sinon.
  Au-delà du plafond applicable, approbation du directeur obligatoire avant
  confirmation. Un vendeur ne peut pas approuver un devis dont il est le vendeur,
  contrôle appliqué côté serveur et non par simple masquage du bouton.
  Un devis approuvé dont la remise augmente au-delà du taux approuvé perd son
  approbation ; une baisse la conserve.
  Sources : D-01, M-02 (client), M-03 (arbitrage humain).

- **D-03 — Le plafond se lit sur le contact de facturation, pas sur le client
  du devis.** Les deux peuvent différer ; c'est le contact de facturation qui
  fait foi. Conséquence actée : changer le contact de facturation d'un devis
  approuvé peut le rendre non conforme.

### Compréhension métier

- La remise commerciale n'est pas un interdit mais un **seuil de délégation** :
  au-delà, la décision remonte au directeur. C'est un workflow d'approbation,
  pas une contrainte de saisie. Changement de nature par rapport à D-01.
- Le client distingue deux populations, « partenaires commerciaux » et autres,
  et accorde 5 points de remise supplémentaires aux premiers. La qualité de
  partenaire n'est pas encore matérialisée dans le système : sa définition
  technique (champ existant ou à créer) reste à établir sur la copie de base.
- Principe de séparation des rôles explicitement posé par le client : demandeur
  et approbateur doivent être deux personnes distinctes.

### Pièges connus

- Aucune évidence chiffrée n'accompagne la demande : ni volume de devis
  dépassant les seuils, ni fréquence, ni coût constaté. À mesurer sur la copie
  avant de dimensionner.
- La case « partenaire » sera décochée par défaut : sans import préalable de la
  liste des partenaires, tous basculent à 10 % à la mise en service.
- Granularité du pourcentage (ligne ou devis) et traitement des remises issues
  des listes de prix : non tranchés, hypothèses H1 et H2 appliquées à défaut.
```

## Pour `.odoo-agents/JOURNAL.md`

```markdown
## 2026-09-08 — Revue fonctionnelle : plafond de remise et approbation directeur

**Intervenant** analyste fonctionnel · **série** 19.0 · **modèles** sale.order, res.partner

**Objet** Consolidation de D-01, M-02 et M-03 en une règle unique et préparation
de la passation développeur / testeur.

**Fait**
- Règle consolidée : 15 % pour les contacts de facturation marqués partenaire
  commercial, 10 % sinon, approbation directeur au-delà, pas d'auto-approbation,
  revalidation à la hausse seulement.
- D-01 déclarée révoquée et remplacée par D-02. Jamais développée : aucune
  dette technique à reprendre.
- Spécification, huit hypothèses de travail (H1–H8) et quatorze critères
  d'acceptation rédigés, dont un cas discriminant (non-partenaire approuvé à
  16 % ramené à 14 %) sans lequel la règle de baisse n'est pas réellement testée.
- Découpage en trois incréments, le premier servant à mesurer les volumes réels
  avant d'engager le workflow.

**Non fait — à faire avant tout développement**
- Briefing projet non lancé : série confirmée par la consigne, mais profil du
  projet (modules custom, présence de Studio, hébergement) inconnu. La voie
  Studio ou module n'est donc **pas tranchée**.
- Verdict standard Odoo 19.0 **non rendu** : aucune recherche dans les sources.
  Pistes à vérifier en priorité — règles d'approbation Studio et leur notion
  d'approbateur exclusif, assistant de remise sur sale.order, champ partenaire
  existant côté CRM, et présence éventuelle de la fonction en 19.1 / 19.4.
- Inventaire de la copie client non réalisé : un champ Studio « partenaire » ou
  une automatisation de contrôle de remise peuvent déjà exister. Développer sans
  ce relevé risque de doubler une personnalisation en place.

**Questions ouvertes (bloquantes)**
1. Seuil par ligne ou sur la remise effective du devis entier ?
2. Les remises issues des listes de prix entrent-elles dans le calcul ?
3. « Devis approuvé » dans M-02 = approbation directeur ou confirmation client ?
4. Quel groupe approbateur, et qui approuve si le seul approbateur est le vendeur ?
5. La case « partenaire commercial » existe-t-elle déjà en base ?

**Risque principal de mise en service** Liste des contacts partenaires à obtenir
et à importer avant la bascule, sinon tous les partenaires sont traités à 10 %.

**Niveau QA retenu** renforcé (droits d'approbation + devis existants en base),
copie client obligatoire.

**Suite** Lancer le briefing et l'inventaire de la copie, rendre le verdict
standard, trancher la voie, puis ouvrir la release.
```

---

**Compte rendu.** Règle consolidée : 15 % partenaire / 10 % sinon, approbation directeur au-delà, sans auto-approbation, revalidation à la hausse uniquement. D-01 est révoquée par D-02 et n'a laissé aucune dette : la substitution est documentaire. Verdict standard **non rendu** faute d'outils — c'est le premier travail à reprendre, avec l'inventaire de la copie, et la voie Studio / module reste ouverte tant que le profil du projet n'est pas relevé. Cinq questions bloquantes, huit hypothèses appliquées à défaut. Les cinq exemples sont traités au § 8 ; j'y ajoute un sixième cas, non demandé mais nécessaire : sans lui, l'exemple 16 → 14 est validé par deux règles à la fois et ne prouve rien. Risque de mise en service à traiter tôt : sans import des partenaires, tous passent à 10 %. Rien n'a été écrit sur disque ; les deux entrées ci-dessus sont prêtes à coller dans `PROJECT.md` et `JOURNAL.md`.