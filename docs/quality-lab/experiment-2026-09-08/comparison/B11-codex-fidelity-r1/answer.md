La règle cible est définie par **E-02 et E-03**, qui corrigent E-01. **Le standard Odoo 19.0 et la voie technique restent non établis faute de preuves.** Aucun développement, déploiement ou test n’est attesté. Voici la passation et les entrées documentaires proposées, **à enregistrer ; aucun fichier n’a été écrit**.

# Revue fonctionnelle — Autorisation des livraisons partielles

**Projet** Entrepôt Cobalt · **Série** 19.0 · **Modules concernés** à identifier  
**Destination proposée** `.odoo-agents/revue_en_cours.md`, aucune release n’étant renseignée.

## 1. Ce que je comprends

En tant que préparateur, je veux savoir si une livraison peut partir selon l’accord du contact de livraison, la quantité disponible et l’approbation logistique, afin de respecter les conditions acceptées par le client.

**Problème réel :** encadrer les expéditions partielles et leurs approbations. E-02 et E-03 établissent les règles métier ; la fréquence, les volumes et le coût du problème ne sont pas fournis.

La règle initiale de livraison intégrale systématique, E-01, est corrigée par E-02. **E-01 n’a jamais été implémentée selon le dossier : aucune ancienne logique ne peut être présumée présente.**

## 2. Verdict standard Odoo 19.0

**NON ÉTABLI.** Aucun extrait des sources ni inventaire de la base n’est fourni. Aucun module, champ ou mécanisme standard ne peut donc être cité comme preuve de couverture.

**Série suivante :** couverture non établie également.

Avant de choisir une solution, vérifier le standard de la série, les personnalisations existantes, les droits et les données client. Il ne serait pas justifié de conclure « à développer » à ce stade.

## 3. Voies possibles

| Voie | Effort | Résultat possible, à vérifier | Coût à la migration | Recommandée |
|---|---|---|---|---|
| Configuration | Non chiffrable sans examen du standard | Règle couverte par des mécanismes existants, si disponibles | Généralement faible ; contrôles à rejouer | À déterminer |
| Studio / configuration en base | Dépend de l’existant et des possibilités de contrôle | Case dédiée et éventuels contrôles ; robustesse des approbations à démontrer | Revalidation des personnalisations et automatisations | À déterminer |
| Code custom | Dépend du workflow et du delta standard | Contrôles complémentaires si nécessaires | Maintenance et adaptation à chaque migration | À déterminer |

**Voie technique non choisie.** Le profil du projet, l’hébergement et l’inventaire de base manquent. La valeur économique n’est pas chiffrable avec le dossier.

## 4. Contradictions et risques

| # | Sévérité | Point | Pourquoi c’est un problème | Proposition |
|---|---|---|---|---|
| 1 | P1 | Appliquer E-01 comme règle cible | Interdirait des partiels explicitement autorisés par E-02 | Retenir E-02 et E-03 ; conserver E-01 comme historique |
| 2 | P1 | Calcul et point de blocage indéfinis | Le résultat et l’action empêchée varient selon l’interprétation | Arbitrer avant de finaliser le contrôle |
| 3 | P1 | Auto-approbation | Interdite par E-03, y compris si le préparateur possède aussi des droits de responsable | Contrôler l’identité du demandeur et de l’approbateur |
| 4 | P1 | Quantité approuvée après plusieurs variations | Une approbation ancienne pourrait être réutilisée à tort | Définir la référence et le cycle de revalidation |
| 5 | P1 | Commandes ouvertes et contacts existants | Une valeur initiale ou une reprise implicite changerait les autorisations | Faire arbitrer la reprise ; examiner une copie client |
| 6 | P2 | Présumer une ancienne implémentation | Aucun état technique ne l’atteste | Inventorier avant toute suppression ou extension |

## 5. Questions bloquantes — attendent le client

1. **Calcul :** le seuil s’applique-t-il à chaque ligne ou à l’ensemble de la commande ? Comment traiter les unités différentes et les reliquats après une première livraison ?
2. **Workflow :** à quelle action faut-il empêcher la poursuite, et à quel moment recalculer la disponibilité et contrôler l’approbation ?
3. **Reprise :** quelles règles appliquer aux commandes déjà ouvertes et quelle valeur attribuer à la case dédiée des contacts existants ?
4. **Variations :** après des changements successifs, compare-t-on à la quantité initialement approuvée, à la dernière quantité approuvée ou à la dernière proposée ? Une baisse restant au-dessus de 60 % impose-t-elle aussi une revalidation ? Que devient l’ancienne approbation après une baisse puis une remontée ?
5. **Quantité de référence :** que signifie « disponible » — stock physique, réservable, réservé, périmètre d’entrepôt — et comment cette quantité se relie-t-elle à la quantité effectivement proposée à l’expédition ?

## 6. Hypothèses proposées, non actées

- Pour isoler les cinq cas demandés, utiliser une commande d’une seule ligne de **80 unités**, sans livraison antérieure, avec une quantité proposée égale à la quantité disponible.
- Pour préparer la traçabilité, envisager de conserver l’auteur de la demande, l’approbateur, la date et la quantité approuvée. Le support technique reste à définir.

Ces propositions ne valent pas décisions client. Le silence ne les valide pas. La préparation des scénarios peut avancer ; les comportements dépendant des cinq arbitrages restent ouverts.

## 7. Spécification

### Modèle de données

**Acté par E-03 :** l’accord aux expéditions partielles est porté par une **case dédiée du contact de livraison**.

Le nom technique, l’existence éventuelle d’un champ équivalent, sa valeur initiale et les droits de modification restent à déterminer. Ne pas substituer implicitement l’accord du contact de facturation ou de la société parente.

L’approbation concerne une quantité proposée. Son support, sa portée et sa référence après plusieurs changements ne sont pas arrêtés.

### Comportement

| Situation | Règle métier actée | Source |
|---|---|---|
| Contact acceptant les partiels ; disponibilité ≥ 60 % | Livraison permise sans approbation au titre de cette règle | E-02 |
| Contact acceptant les partiels ; disponibilité < 60 % | Approbation du responsable logistique nécessaire | E-02 |
| Contact refusant les partiels | Attendre la quantité complète ; aucune dérogation par approbation n’est prévue | E-02 |
| Livraison partielle approuvée ; quantité proposée diminuée | Revalidation nécessaire | E-02 |
| Livraison partielle approuvée ; quantité proposée augmentée | Pas de revalidation pour cette seule augmentation | E-02 |
| Préparateur approuvant sa propre demande | Interdit | E-03 |

Ces règles ne dispensent pas des autres conditions de livraison. Leur combinaison lors de variations successives reste à arbitrer.

### Interface

La case dédiée doit être accessible sur le contact de livraison. Son emplacement et ses droits d’édition restent à définir.

La présentation de la demande d’approbation et des motifs de blocage dépend du workflow choisi. Aucun bouton précis n’est encore spécifié.

### Sécurité

L’approbation sous le seuil relève du responsable logistique. Un préparateur ne peut pas approuver sa propre demande, même s’il cumule les rôles. La correspondance avec les groupes et droits existants doit être vérifiée.

Le contrôle doit rester effectif sur tous les chemins permettant l’action retenue, au-delà du seul affichage des boutons.

### Reprise de données

Aucune modification automatique des contacts, commandes ouvertes ou approbations existantes n’est spécifiée. La politique de reprise attend l’arbitrage client et l’inventaire de base.

### Hors périmètre

Aucune dérogation au refus des partiels n’est demandée. Aucun changement de facturation, tarification ou allocation de stock n’est spécifié.

## 8. Critères d’acceptation

Les cinq premiers scénarios utilisent le jeu de données isolé proposé en section 6. Ils définissent le **résultat métier attendu** ; le geste de test exact dépendra du point de blocage choisi.

| Cas | Données et événement | Résultat attendu |
|---|---|---|
| A | 80 commandées ; contact acceptant ; 50 disponibles et proposées | **50 / 80 = 62,5 %** : autorisation sans approbation au titre de cette règle |
| B | 80 commandées ; contact acceptant ; 40 disponibles et proposées | **40 / 80 = 50 %** : approbation du responsable logistique nécessaire |
| C | 80 commandées ; contact refusant ; 50 disponibles et proposées | Attendre les **80 unités** ; une approbation ne constitue pas une dérogation prévue |
| D | 80 commandées ; contact acceptant ; livraison approuvée à 50, puis proposée à 40 | L’approbation à 50 ne suffit plus : revalidation nécessaire |
| E | 80 commandées ; contact acceptant ; livraison approuvée à 50, puis proposée à 60 | Aucune revalidation pour cette augmentation |

Dans D et E, l’approbation à 50 est une **précondition du scénario fourni**, même si 50 sur 80 ne nécessite pas d’approbation selon le seuil.

Critères complémentaires :

- [ ] Étant donné 80 unités commandées et un contact acceptant, quand 48 unités sont disponibles et proposées, alors le seuil exact de **60 %** autorise la livraison sans approbation.
- [ ] Étant donné une demande nécessitant une approbation, quand son préparateur tente de l’approuver, alors l’approbation est refusée, même s’il possède aussi le rôle de responsable.
- [ ] Étant donné cette demande, quand un autre responsable logistique habilité l’approuve, alors la condition d’approbation est satisfaite.
- [ ] Étant donné un contact refusant les partiels, quand les 80 unités sont disponibles, alors cette règle n’exige aucune approbation de livraison partielle.

**À compléter après arbitrage :** commandes multilignes, reliquats, variations successives, disponibilité différente de la proposition, commandes ouvertes et chemins de contournement du contrôle.

**Aucun de ces tests n’a été exécuté.**

## 9. Estimation et découpage

1. **Dès maintenant :** valider la table métier et préparer les données de test isolées.
2. **Avant choix technique :** obtenir les arbitrages, examiner standard, personnalisations, droits et volumes.
3. **Après cadrage :** chiffrer et réaliser le delta retenu, avec sa reprise de données.
4. **Avant livraison :** exécuter la recette des règles, des droits et de la reprise sur copie client.

**Estimation : non établie.** Un chiffrage ferme serait prématuré.  
**Niveau QA : renforcé**, pour les droits et les données existantes ; copie client nécessaire à cette validation.

## 10. Ce que l’utilisateur verra

Une case dédiée sur le contact de livraison déterminera l’acceptation des partiels. Selon le cas, le préparateur pourra poursuivre, devra obtenir une approbation ou devra attendre la quantité complète. Une baisse d’une quantité approuvée nécessitera une revalidation.

Les écrans, boutons et messages précis attendent l’arbitrage du workflow.

---

# Entrées proposées pour `.odoo-agents/PROJECT.md`

## Compréhension métier

- **[E-02]** L’autorisation de livrer partiellement dépend de l’accord du contact de livraison et du rapport entre quantité disponible et quantité commandée.
- **[E-03]** Cet accord est matérialisé par une case dédiée du contact de livraison.
- **[Dossier]** Fréquence, utilisateurs concernés, volumes et coût actuel non renseignés.

## Décisions actées et sources

- **[E-01, corrigée par E-02]** La livraison intégrale systématique était la règle initiale. Elle n’a pas été implémentée ; elle ne constitue plus la règle cible générale.
- **[E-02 — arbitrage client]** Contact acceptant : sans approbation dès 60 % disponibles ; en dessous, approbation du responsable logistique nécessaire.
- **[E-02 — arbitrage client]** Contact refusant : attendre la quantité complète.
- **[E-02 — arbitrage client]** Après approbation d’un partiel, une diminution de la quantité proposée exige une revalidation ; une augmentation n’en exige pas.
- **[E-03 — confirmation client]** Case dédiée sur le contact de livraison ; auto-approbation du préparateur interdite.

## Attend le client

- Granularité du calcul, unités et reliquats.
- Point de blocage et moment du contrôle.
- Reprise des commandes ouvertes et valeur initiale des contacts.
- Référence après variations successives et articulation avec le seuil.
- Définition de la disponibilité et relation avec la quantité proposée.

## Propositions non actées

- Jeu de recette isolé : une ligne de 80 unités, sans livraison antérieure, quantité proposée égale à la disponibilité.
- Traçabilité envisagée : demandeur, approbateur, date et quantité approuvée.
- Aucune voie technique retenue.

## État réel de réalisation

- E-01 explicitement non implémentée.
- Aucun inventaire de base ni état de code fourni.
- Couverture standard et couverture par les personnalisations non établies.
- Aucune réalisation, migration de données, exécution de tests ou mise en production attestée.
- Passation préparée dans la conversation ; enregistrement documentaire restant à effectuer.

# Entrée proposée pour `JOURNAL.md`

**Date : à renseigner lors de l’enregistrement — Analyse du dossier E-01 à E-03.**

- **Travail réalisé :** synthèse documentaire, table de décision, cinq scénarios chiffrés et critères complémentaires préparés dans la conversation, sans outils.
- **Correction de référence :** E-02 corrige E-01 ; E-03 précise le support de l’accord et interdit l’auto-approbation. Aucune décision technique ajoutée.
- **Résultats attendus documentés :** 50/80 avec accord → sans approbation ; 40/80 avec accord → approbation ; 50/80 sans accord → attente du complet ; approbation 50 puis 40 → revalidation ; approbation 50 puis 60 → pas de revalidation pour l’augmentation.
- **Points ouverts :** calcul, workflow, reprise, variations successives et définition de la disponibilité.
- **État technique :** aucune inspection, modification, restauration, exécution de tests ou opération de déploiement réalisée.
- **Suite :** recueillir les arbitrages et les preuves d’existant avant de sélectionner la voie technique et de chiffrer.