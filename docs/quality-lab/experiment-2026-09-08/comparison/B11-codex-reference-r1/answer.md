# Passation développeur / testeur — Entrepôt Cobalt

**Odoo 19.0 — analyse du dossier uniquement.** Aucun fichier écrit, aucune base ni source inspectée, aucun développement ou test exécuté. Les entrées ci-dessous sont proposées pour enregistrement.

**Conclusion :** E-02 corrige E-01 et E-03 précise le consentement et la séparation des rôles. Les cinq cas demandés sont déterminables ; le développement complet reste conditionné aux arbitrages listés ci-dessous.

## 1. Besoin et décisions acquises

« En tant que préparateur, je veux savoir si une quantité peut être expédiée et obtenir, lorsque nécessaire, une approbation indépendante afin de respecter le choix du contact de livraison. »

**Problème réel :** encadrer les expéditions partielles. Le dossier indique que la règle initiale n’était pas implémentée ; fréquence, volumes et coût opérationnel ne sont pas documentés.

| Source | Décision | Statut |
|---|---|---|
| E-01 | Toutes les commandes doivent être livrées en une fois. | Exigence initiale, corrigée par E-02 ; non implémentée selon le dossier. |
| E-02 | Contact acceptant les partiels : expédition sans approbation dès **60 % inclus** de disponibilité. En dessous, approbation logistique nécessaire. | Acquis. |
| E-02 | Contact refusant les partiels : attendre la quantité complète. | Acquis ; aucune dérogation par approbation n’est prévue. |
| E-02 | Une livraison partielle approuvée doit être revalidée si la quantité proposée diminue, pas si elle augmente. | Acquis ; référence après plusieurs variations à préciser. |
| E-03 | Le consentement est une case dédiée du **contact de livraison**. | Acquis. |
| E-03 | Un préparateur ne peut pas approuver sa propre demande. | Acquis, y compris s’il possède aussi un rôle de responsable. |

## 2. Standard et voie de réalisation

**Verdict standard Odoo 19.0 : non établi.** Le dossier ne contient aucun extrait des sources ni inventaire de configuration permettant de conclure « ça existe », « partiel » ou « à développer ». Aucun chemin de preuve ne peut être cité honnêtement.

**Série suivante :** couverture non vérifiée ; aucune conclusion de migration possible à ce stade.

| Voie | Effort indicatif | Résultat envisageable | Coût de migration |
|---|---|---|---|
| Configuration | Faible si couverture suffisante | Réutilisation des mécanismes existants, couverture à vérifier | Généralement faible, avec recontrôle |
| Studio / configuration en base | Faible pour la case ; logique à évaluer | Consentement et éventuellement circuit d’approbation | Revalidation des vues, droits et automatisations |
| Code custom | À estimer après arbitrage | Delta métier non couvert, blocage et invalidation contrôlés | Maintenance et tests à chaque migration |

**Recommandation :** rechercher d’abord la couverture standard et l’existant client. Ne décider d’un module qu’après identification du delta. Le profil custom/Studio et l’hébergement ne sont pas fournis.

## 3. Questions bloquantes — en attente du client

1. **Calcul :** les 60 % s’apprécient-ils par ligne ou sur un ensemble ? Quelle quantité constitue la « disponibilité », et doit-elle être égale à la quantité proposée à l’expédition ? Comment traiter les unités différentes et les reliquats ?
2. **Workflow :** à quelle action exacte bloquer ou demander l’approbation, et sur quel objet porte celle-ci : commande, livraison ou ligne ?
3. **Commandes ouvertes :** quelles commandes existantes entrent dans la règle, à quelle date, et comment renseigner les contacts dont le consentement n’est pas connu ?
4. **Variations successives :** compare-t-on à la dernière quantité explicitement approuvée ou à la dernière quantité proposée ? Exemple : **40 approuvées → 45 proposées → 42 proposées**, sur 80 commandées.
5. **Priorité des règles :** une quantité déjà approuvée qui diminue tout en restant à au moins 60 % doit-elle être revalidée ? Exemple : **55 approuvées → 50 proposées**, sur 80.

La question 5 oppose l’exemption d’approbation au-dessus du seuil à l’exigence de revalidation après diminution. Le dossier ne tranche pas explicitement leur priorité.

## 4. Spécification acquise et limites

### Données à porter

- Consentement aux expéditions partielles sur le contact de livraison effectivement utilisé.
- Demande d’approbation rattachée au périmètre qui sera arbitré.
- Identité du demandeur et de l’approbateur, décision, date et quantité couverte par l’approbation.
- Référence permettant de vérifier la validité de l’approbation après modification.

Les noms techniques et le support standard/custom restent à déterminer. Ces besoins ne justifient pas à eux seuls la création d’un nouveau modèle.

### Comportement

Pour une première décision, avant toute variation d’une quantité approuvée :

| Consentement | Disponibilité | Résultat métier |
|---|---|---|
| Refus | Inférieure à la quantité complète | Attendre la quantité complète ; l’approbation ne constitue pas une voie de dérogation. |
| Accord | Inférieure à 60 % | Approbation logistique nécessaire avant expédition. |
| Accord | Égale ou supérieure à 60 % | Aucune approbation nécessaire au titre de cette règle. |

Une augmentation de la quantité proposée ne déclenche pas, à elle seule, une nouvelle approbation. Une diminution impose une revalidation selon E-02 ; la référence de comparaison et la priorité au-dessus du seuil restent à arbitrer.

Ces règles ne dispensent pas des autres conditions nécessaires à une livraison.

### Interface et sécurité

- Afficher la case dédiée sur le contact de livraison.
- Rendre visible la raison du blocage et l’état de l’approbation.
- Réserver l’approbation au responsable logistique et refuser l’auto-approbation, même en cas de cumul de rôles.
- Faire respecter les contrôles au niveau métier, y compris pour les actions hors écran ; masquer un bouton ne suffit pas.
- Faire confirmer les personnes habilitées à modifier le consentement et le périmètre société de l’approbateur.

### Reprise et hypothèses

- **Aucune reprise implicite** des commandes ou consentements existants.
- Pour les exemples ci-dessous uniquement : une ligne de 80 unités homogènes, aucune livraison antérieure, disponibilité égale à la quantité proposée.
- Les deux cas de variation concernent un contact acceptant les partiels.
- L’approbation préalable à 50 est une donnée du scénario, même si le seuil permettrait initialement d’expédier 50 sans approbation.

**Hors périmètre :** modification des règles de réservation, d’approvisionnement, de valorisation ou de facturation.

## 5. Cas attendus pour 80 unités commandées

Le seuil est **80 × 60 % = 48 unités**.

| Cas | Calcul | Résultat attendu | Source |
|---|---|---|---|
| Contact acceptant, 50 disponibles | 62,5 % | Expédition partielle sans approbation au titre de cette règle. | E-02 |
| Contact acceptant, 40 disponibles | 50 % | Approbation logistique nécessaire ; pas d’expédition avant décision favorable valide. | E-02 |
| Contact refusant, 50 disponibles | 62,5 % | Attendre 80 unités ; le seuil de 60 % ne s’applique pas. | E-02 |
| Livraison approuvée à 50, abaissée à 40 | Diminution ; nouvelle quantité à 50 % | L’approbation à 50 ne suffit plus : revalidation nécessaire avant expédition de 40. | E-02 |
| Livraison approuvée à 50, portée à 60 | Augmentation ; nouvelle quantité à 75 % | Aucune revalidation du seul fait de l’augmentation. | E-02 |

## 6. Critères d’acceptation complémentaires

**À exécuter après choix du point de contrôle ; résultats attendus, non résultats de tests.**

- [ ] Étant donné un contact acceptant et 80 unités commandées, quand 48 sont disponibles et proposées, alors aucune approbation n’est exigée.
- [ ] Dans les mêmes conditions avec 47 unités, une approbation est exigée.
- [ ] Étant donné une demande créée par un préparateur, quand ce même utilisateur tente de l’approuver, alors l’action est refusée, même s’il est responsable logistique.
- [ ] Un utilisateur sans habilitation logistique ne peut pas approuver.
- [ ] Une approbation devenue insuffisante après passage de 50 à 40 ne permet pas de franchir le point de contrôle.
- [ ] Lorsque le client commercial et le contact de livraison ont des consentements différents, celui du contact de livraison gouverne la décision.
- [ ] Les cinq scénarios du tableau produisent les résultats indiqués.

**Tests suspendus à l’arbitrage :** commandes multilignes, reliquats, variations successives, baisse restant au-dessus de 60 %, commandes ouvertes et moment exact du blocage.

## 7. Risques et découpage

| Priorité | Risque | Traitement |
|---|---|---|
| P1 | Développer encore la règle absolue E-01 | Utiliser E-02 corrigé et E-03 comme référence active. |
| P1 | Appliquer 60 % à un contact refusant les partiels | Évaluer d’abord le consentement. |
| P1 | Réutiliser une approbation après une baisse qui nécessite revalidation | Conserver sa quantité de référence et contrôler sa validité. |
| P1 | Permettre l’auto-approbation ou un contournement hors écran | Contrôle métier des habilitations et identités. |
| P1 | Présumer le consentement ou appliquer rétroactivement la règle | Faire arbitrer la reprise avant activation. |

**Ordre proposé :** arbitrages client → inventaire sources/base et choix de voie → consentement → décision et approbation → reprise éventuelle et recette.

**Estimation :** chiffrage non fiable avant résolution des blocages et connaissance de l’existant.

**Niveau QA : renforcé**, du fait des droits et de la reprise potentielle. Prévoir une copie client ; aucune n’est fournie.

**Ce que l’utilisateur verra :** la case de consentement, l’indication « approbation nécessaire » ou « quantité complète requise », et l’état d’approbation. L’écran et l’action portant le blocage attendent l’arbitrage client.

---

## Entrée proposée — `<projet>/.odoo-agents/PROJECT.md`

### Compréhension métier

Entrepôt Cobalt, Odoo 19.0. La politique de livraison dépend du consentement du contact de livraison aux expéditions partielles. Le seuil d’autonomie est fixé à 60 % inclus ; en dessous, une approbation logistique est nécessaire. Le dossier ne documente ni volumes ni coût opérationnel.

### Décisions actées

- **E-01, corrigée par E-02 :** la livraison systématique en une fois n’est plus la règle générale. E-01 était non implémentée selon le dossier.
- **E-02 :** contact acceptant les partiels : aucune approbation dès 60 % ; approbation logistique nécessaire en dessous.
- **E-02 :** contact refusant les partiels : attendre la quantité complète.
- **E-02 :** diminution d’une quantité proposée déjà approuvée : revalidation ; augmentation : pas de revalidation du seul fait de cette hausse.
- **E-03 :** consentement porté par une case dédiée du contact de livraison.
- **E-03 :** interdiction pour le préparateur d’approuver sa propre demande.

### En attente du client

Calcul et définition des quantités ; point de contrôle et portée de l’approbation ; reprise des commandes ouvertes et consentements inconnus ; référence après variations successives ; priorité entre diminution et exemption à partir de 60 %.

### État connu

Aucun inventaire de base, code, déploiement ou résultat de test fourni. Couverture standard 19.0 et série suivante non vérifiée. Voie technique non actée.

## Entrée proposée — `JOURNAL.md`

**Nature :** revue fonctionnelle sur dossier synthétique, à dater lors de l’enregistrement.  
**Sources :** E-01, E-02, E-03.

- Consolidation de la correction E-02 et des précisions E-03, avec conservation de l’historique E-01.
- Production d’une passation et des résultats attendus pour les cinq cas à 80 unités ; seuil calculé à 48 unités.
- Identification de cinq arbitrages client bloquant la spécification complète.
- Préconisation d’un inventaire standard/base avant choix de réalisation et d’une QA renforcée.
- **Exécution :** aucune opération sur fichiers, base ou graphe ; aucun développement, déploiement ou test exécuté.
- **Suite :** obtenir les arbitrages, vérifier l’existant, finaliser la spécification et chiffrer. Aucune réalisation ni recette déclarée terminée.