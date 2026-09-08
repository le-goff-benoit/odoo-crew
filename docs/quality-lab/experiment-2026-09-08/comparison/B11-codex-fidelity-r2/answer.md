# Passation développeur/testeur — Entrepôt Cobalt

**Série : Odoo 19.0.** Analyse limitée au dossier fourni. Aucun fichier écrit, aucune base ni source consultée, aucun développement, déploiement ou test exécuté. Les contenus ci-dessous sont à enregistrer.

## 1. Ce que je comprends

En tant que préparateur, je veux savoir si une livraison peut partir et obtenir, lorsque nécessaire, une approbation indépendante du responsable logistique.

**Problème réel :** encadrer les expéditions partielles selon l’accord du destinataire et la quantité disponible. Le dossier ne chiffre ni fréquence, ni volumes réels, ni coût actuel.

**E-02 corrige E-01** : l’obligation générale de livrer en une fois est remplacée par une règle conditionnelle. E-01 n’avait pas été implémentée ; il ne s’agit donc pas d’une correction de développement démontré.

## 2. Verdict standard Odoo 19.0

**Non établi.** Aucune preuve issue des sources ou de la base ne permet de conclure « existe », « partiel » ou « à développer ».

**Série suivante :** couverture non vérifiée. Aucun chemin de source ne peut être cité sur la base du dossier.

La vérification du standard et l’inventaire des personnalisations devront précéder le choix technique.

## 3. Voies possibles

**Voie technique non établie** : hébergement, modules installés et présence de Studio inconnus.

| Voie à examiner | Effort | Résultat à vérifier | Coût à la migration |
|---|---|---|---|
| Configuration | Non chiffrable avant vérification | Couverture des conditions, blocages et approbations | Faible si entièrement standard |
| Studio / configuration en base | Non chiffrable avant inventaire | Champ d’accord et capacité à imposer les contrôles nécessaires | Revalidation des champs, vues et automatisations |
| Code custom | Non chiffrable avant analyse des écarts | Complément limité aux besoins non couverts | Maintenance et adaptation à chaque migration |

**Recommandation immédiate :** vérifier l’existant puis retenir la voie la moins coûteuse qui impose réellement les règles, y compris l’interdiction d’auto-approbation.

## 4. Contradictions et risques

| # | Sévérité | Point | Conséquence / traitement |
|---|---|---|---|
| 1 | P1 | Appliquer encore E-01 sans sa correction | Refuserait des partiels autorisés par E-02. Utiliser E-02 comme règle métier actuelle. |
| 2 | P1 | Confondre quantité disponible et quantité proposée | Le seuil porte sur la disponibilité ; la revalidation porte sur la proposition. Ne pas les fusionner sans arbitrage. |
| 3 | P1 | Approbation considérée comme dérogation au refus du contact | E-02 impose d’attendre la quantité complète. Aucune dérogation n’est autorisée par le dossier. |
| 4 | P1 | Contrôle limité à l’écran ou approbation personnelle | Risque de contournement. Imposer les droits et règles au point de contrôle retenu. |
| 5 | P1 | Référence de revalidation implicite | Des variations successives pourraient autoriser une baisse sans revalidation. Arbitrage nécessaire. |
| 6 | P1 | Application aux commandes ouvertes sans règle de reprise | Risque de blocage ou de départ indu. Aucun traitement rétroactif n’est acté. |

## 5. Questions bloquantes — attendent le client

1. **Calcul :** le seuil s’applique-t-il par ligne ou à l’ensemble de la commande ? Quelles quantités retenir : commande initiale ou reliquat, disponibilité physique ou réservable pour cette commande, et quelles règles pour unités et arrondis ?
2. **Workflow :** à quel événement faut-il bloquer, puis revérifier disponibilité et approbation : préparation, réservation, validation de livraison ou autre ?
3. **Commandes ouvertes :** lesquelles doivent suivre la nouvelle règle, à quelle date, et comment traiter leurs livraisons ou accords déjà engagés ?
4. **Variations successives :** quelle référence utiliser après plusieurs changements ? Exemple discriminant : approuvé à 50, augmenté à 60, puis diminué à 55.
5. **Case du contact :** comment initialiser les contacts existants et nouveaux, qui peut modifier cette case, et quel effet a une modification ou un changement de contact sur une livraison en cours ?

L’absence de réponse ne valide aucune hypothèse.

## 6. Hypothèses proposées, non actées

- Contrôler la règle lors de la validation de livraison.
- Comparer la proposition à la dernière quantité explicitement approuvée.
- Initialiser la case à « refus des partiels » en l’absence d’accord documenté.

Ces propositions ne sont **ni des décisions client ni des critères définitifs**. La préparation des scénarios simples et l’analyse de couverture restent possibles indépendamment.

## 7. Spécification fonctionnelle

### Modèle de données

**Acté :**

- L’accord aux expéditions partielles est une **case dédiée du contact de livraison** — E-03.
- Une approbation concerne une quantité proposée, puisque sa diminution impose une revalidation — E-02.

**À concevoir après vérification de l’existant :**

- Support de la demande et de l’approbation, identité du demandeur et de l’approbateur, quantité approuvée et historique utile.
- Noms techniques, modèle porteur et mécanisme de droits : non établis.

### Comportement

| Situation | Règle actée | Source |
|---|---|---|
| Contact acceptant les partiels ; disponibilité ≥ 60 % de la quantité commandée | Autorisation sans approbation au titre de cette règle | E-02 |
| Même contact ; disponibilité < 60 % | Approbation du responsable logistique nécessaire | E-02 |
| Contact refusant les partiels | Attendre la quantité complète ; une approbation ne constitue pas une dérogation | E-02 |
| Proposition approuvée puis diminuée | Revalidation nécessaire | E-02 |
| Proposition approuvée puis augmentée | Pas de revalidation exigée du seul fait de l’augmentation | E-02 |

La règle de revalidation doit être traitée explicitement : le simple recalcul du seuil ne suffit pas à représenter une approbation devenue insuffisante après une baisse.

### Interface

La case dédiée du contact est exigée. L’écran de demande, les commandes d’approbation et les messages de blocage restent à définir selon le workflow et les possibilités existantes.

L’utilisateur doit pouvoir comprendre le motif applicable : quantité complète attendue, approbation nécessaire ou revalidation nécessaire.

### Sécurité

- L’approbation relève du responsable logistique — E-02.
- Un préparateur ne peut pas approuver sa propre demande — E-03.
- Un cumul de rôles ne doit pas permettre de contourner cette interdiction.
- La correspondance avec les groupes et droits techniques reste à établir.

### Reprise de données

Aucune reprise actée. Ne pas déduire un consentement aux partiels ni une approbation à partir de livraisons historiques.

L’initialisation des contacts et le traitement des commandes ouvertes dépendent des réponses client.

### Hors périmètre

Aucune modification des règles de facturation, des reliquats, ni aucun envoi automatique au client n’est demandé.

## 8. Critères d’acceptation

Les cinq cas utilisent **une seule ligne de 80 unités homogènes**, sans livraison antérieure. Ils ne tranchent pas le calcul multilignes. Le seuil est **48 unités**.

| Cas | Données / action | Résultat attendu |
|---|---|---|
| A | Contact acceptant les partiels ; 50 disponibles | 62,5 % : livraison autorisée sans approbation au titre de cette règle. |
| B | Même contact ; 40 disponibles | 50 % : approbation du responsable logistique nécessaire avant autorisation. |
| C | Contact refusant les partiels ; 50 disponibles | Livraison partielle interdite ; attendre 80. Une approbation ne lève pas ce refus. |
| D | Livraison approuvée à 50 ; proposition abaissée à 40 | L’approbation précédente ne suffit plus ; revalidation nécessaire. |
| E | Livraison approuvée à 50 ; proposition portée à 60 | Aucune revalidation exigée du seul fait de cette hausse. |

**Contrôles complémentaires :**

- [ ] À 48 disponibles, contact acceptant les partiels : aucune approbation nécessaire au titre du seuil.
- [ ] À 47 disponibles : approbation nécessaire.
- [ ] Le préparateur demandeur tente d’approuver sa demande : refus, même s’il possède aussi le rôle de responsable.
- [ ] Un utilisateur sans droit d’approbation tente d’approuver : refus.
- [ ] Pour le cas D, une revalidation valable permet de satisfaire l’exigence d’approbation.
- [ ] Après arbitrage du workflow, les mêmes règles sont vérifiées sur tous les chemins disponibles permettant de franchir ce point.

**Cas en attente d’oracle client :** calcul multilignes, reliquats, variations successives, commandes ouvertes et changements de contact ou d’accord.

Ces scénarios sont préparés ; **aucun n’a été exécuté**.

## 9. Estimation et découpage

1. Vérifier la couverture Odoo 19.0, la série suivante et les personnalisations en base.
2. Obtenir les cinq arbitrages ; finaliser les résultats attendus correspondants.
3. Choisir la voie technique et chiffrer le seul écart restant.
4. Réaliser puis vérifier les règles et les droits ; préparer la reprise approuvée.
5. Recetter sur copie client avant déploiement.

**Estimation : non établie.** Le dossier ne permet pas un chiffrage fiable.

**Niveau QA : renforcé**, en raison des droits et des données existantes ; copie client nécessaire à cette recette.

## 10. Ce que l’utilisateur verra

Une case d’accord sur le contact de livraison et, selon la situation, une autorisation de poursuivre ou un motif de blocage. Les modalités d’approbation et de revalidation restent à préciser. Aucun changement visible n’est actuellement démontré.

---

# Entrées PROJECT.md à enregistrer

## Compréhension métier

- **Entrepôt Cobalt — Odoo 19.0.**
- L’expédition partielle dépend de l’accord explicite du **contact de livraison**, matérialisé par une case dédiée — E-03.
- Le seuil d’autonomie est de 60 % de la quantité commandée ; sous ce seuil, l’approbation relève du responsable logistique — E-02.

## Décisions actées et sources

- **E-01, remplacée par E-02 :** livraison systématiquement en une fois. Cette règle n’avait pas été implémentée.
- **E-02, arbitrage client :** si le contact accepte les partiels, autoriser sans approbation dès 60 % disponibles ; en dessous, exiger une approbation logistique.
- **E-02 :** si le contact refuse les partiels, attendre la quantité complète.
- **E-02 :** revalider une livraison approuvée lorsque la quantité proposée diminue ; aucune revalidation imposée du seul fait d’une augmentation.
- **E-03, précision client :** accord porté par une case dédiée du contact de livraison ; interdiction pour un préparateur d’approuver sa propre demande.

## Arbitrages ouverts

- Granularité et bases du calcul.
- Point de contrôle dans le workflow.
- Reprise des commandes ouvertes.
- Référence après variations successives.
- Initialisation, droits de modification et effet des changements de la case ou du contact.

## Propositions non actées

Contrôle à la validation de livraison ; référence à la dernière quantité explicitement approuvée ; refus par défaut sans consentement documenté. Aucune de ces propositions ne vaut accord client.

## État réel de réalisation

Analyse documentaire et scénarios préparés dans la conversation. Couverture standard et voie technique non établies. Aucun inventaire, développement, déploiement ou test fourni ou exécuté. Entrées non enregistrées sur disque.

---

# Entrée JOURNAL.md à enregistrer

**Objet :** passation fonctionnelle préparatoire — expéditions partielles, Entrepôt Cobalt, Odoo 19.0.  
**Sources :** E-01, E-02 et E-03 du dossier fourni.

- Correction de référence identifiée : E-02 remplace l’obligation générale E-01, non implémentée.
- Décisions conservées avec leur provenance : accord du contact, seuil inclusif de 60 %, approbation logistique, revalidation à la baisse et interdiction d’auto-approbation.
- Résultats attendus documentés pour les cinq cas à 80 unités ; seuil calculé à 48 unités.
- Cinq arbitrages client identifiés ; propositions conservées séparément des décisions.
- Standard, inventaire client, choix technique et estimation : non établis.
- Aucune opération réelle effectuée ; aucun résultat de test disponible.
- **Suite attendue :** arbitrages client et vérification de l’existant avant finalisation de la spécification et engagement de réalisation.