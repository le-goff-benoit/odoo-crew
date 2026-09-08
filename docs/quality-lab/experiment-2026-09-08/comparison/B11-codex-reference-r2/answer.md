Passation proposée ci-dessous, avec les entrées à enregistrer. **Aucun fichier, contrôle du standard, inventaire de base ou test n’a été exécuté.** La règle métier est partiellement arbitrée ; quatre décisions client restent nécessaires avant de figer l’implémentation.

## Passation développeur/testeur

**Projet :** Entrepôt Cobalt · **Série :** Odoo 19.0  
**Destination proposée :** `.odoo-agents/revue_en_cours.md`, faute de release indiquée.

### 1. Besoin et décisions applicables

En tant que préparateur, je veux savoir si une quantité proposée peut être livrée ou nécessite une approbation, afin de respecter l’accord du contact de livraison et les seuils décidés par le client.

Le besoin documenté est une règle de contrôle des livraisons. La fréquence, les volumes réels et le coût des difficultés actuelles ne sont pas fournis.

| Source | Décision | Statut |
|---|---|---|
| E-01 | Toutes les commandes doivent être livrées en une fois. | Règle initiale, signalée non implémentée ; remplacée par E-02. |
| E-02 | Contact acceptant les partiels : livraison sans approbation à partir de 60 % de la quantité commandée ; approbation logistique nécessaire en dessous. | Actée. Le seuil de 60 % est inclusif. |
| E-02 | Contact refusant les partiels : attendre la quantité complète. | Actée. Aucune dérogation par approbation n’est prévue. |
| E-02 | Après approbation d’une livraison partielle, une diminution de quantité impose une revalidation ; une augmentation ne l’impose pas. | Actée pour une variation simple ; référence des variations successives à arbitrer. |
| E-03 | L’accord aux expéditions partielles est une case dédiée du contact de livraison. | Actée. Ne pas substituer l’accord du contact de facturation ou de la société parente. |
| E-03 | Un préparateur ne peut pas approuver sa propre demande. | Actée, y compris s’il dispose également du rôle de responsable logistique. |

### 2. Standard et voie d’implémentation

**Verdict standard Odoo 19.0 : non établi sur le dossier fourni.** Aucun extrait de source ni inventaire client ne permet de conclure « ça existe », « partiel » ou « à développer ». Aucun chemin de preuve ne peut être cité honnêtement. La couverture en série suivante est également inconnue.

| Voie | Effort et résultat possibles | Coût de migration | Recommandation |
|---|---|---|---|
| Configuration standard | À vérifier ; retenir si elle couvre intégralement les règles. | Généralement faible. | Première vérification. |
| Studio / configuration en base | À vérifier pour la case et l’interface ; capacité à garantir les contrôles d’approbation non démontrée. | Maintenance des personnalisations et automatismes. | Selon l’existant et les limites constatées. |
| Code custom | Delta éventuel pour contrôle, approbation et revalidation ; chiffrage impossible actuellement. | Adaptation et vérification à chaque migration. | Seulement pour les écarts prouvés. |

**Voie recommandée :** vérifier le standard et l’existant client, puis implémenter uniquement le delta. Le profil du projet — modules, Studio, hébergement — n’est pas fourni et ne permet pas de choisir définitivement la voie technique.

### 3. Questions bloquantes — attendent le client

1. **Granularité :** le seuil est-il calculé par ligne ou sur l’ensemble de la commande ? Si c’est un ensemble, comment agréger des produits et unités différents ?
2. **Point de blocage :** à quelle étape exacte faut-il empêcher la poursuite : préparation, réservation, validation de livraison ou autre étape désignée ?
3. **Reprise :** la règle s’applique-t-elle aux commandes déjà ouvertes ? Comment renseigner l’accord des contacts existants et traiter les éventuelles approbations antérieures ?
4. **Variations successives :** quelle quantité sert de référence après une augmentation sans revalidation ? Exemple : approuvé à 50, porté à 60, puis ramené à 55 — faut-il revalider ?

Ces réponses bloquent les parties correspondantes de la spécification. Les exemples simples ci-dessous sont déjà déterminés.

### 4. Spécification fonctionnelle disponible

**Modèle de données**

- Accord aux expéditions partielles porté par une case dédiée sur le contact de livraison — **décision E-03**.
- Réutiliser une donnée existante si elle répond au besoin après inventaire ; aucun nom technique de champ n’est arrêté.
- Prévoir la traçabilité de la demande, du demandeur, de l’approbateur, de la date et de la quantité approuvée — **proposition technique à confirmer lors de la conception**.
- Le support de l’approbation — commande, ligne, livraison — dépend des réponses sur la granularité et le workflow.

**Comportement**

Au point de contrôle restant à choisir :

| Situation | Résultat attendu |
|---|---|
| Contact refusant les partiels, quantité inférieure au total commandé | Livraison bloquée jusqu’à disponibilité complète. |
| Contact acceptant les partiels, quantité atteignant au moins 60 %, sans approbation antérieure à revalider | Approbation non nécessaire. |
| Contact acceptant les partiels, quantité inférieure à 60 % | Approbation du responsable logistique nécessaire. |
| Quantité d’une livraison partielle approuvée diminuée | Revalidation nécessaire. |
| Quantité d’une livraison partielle approuvée augmentée | Revalidation non nécessaire. |

La revalidation après diminution est une obligation distincte du seuil. E-02 ne prévoit pas d’exception lorsque la quantité diminuée reste au-dessus de 60 %.

**Interface et sécurité**

- Afficher la case dédiée sur le contact de livraison.
- Au point de contrôle choisi, expliquer le motif : quantité complète attendue, approbation requise ou revalidation requise.
- Réserver l’approbation au responsable logistique et interdire l’approbation de sa propre demande.
- Contrôler ces droits au niveau de l’opération, sans dépendre uniquement de la visibilité d’un bouton.
- L’identification du groupe de responsables logistiques reste à vérifier dans l’existant.

**Reprise et limites**

- Ne pas assimiler l’absence actuelle de donnée à un refus métier déjà exprimé.
- Ne pas appliquer silencieusement une valeur aux contacts existants ni modifier les commandes ouvertes avant l’arbitrage de reprise.
- Pour les exemples suivants uniquement : une commande d’une ligne, 80 unités, une première livraison, et une quantité proposée égale à la quantité disponible.
- La définition opérationnelle de « disponible », les reliquats, les livraisons successives, les changements de contact et les arrondis restent à préciser lors de la conception. Aucune couverture n’est revendiquée sur ces sujets.

### 5. Cas d’acceptation pour les 80 unités

Le seuil est **80 × 60 % = 48 unités**.

| Cas | Données | Résultat attendu | Source |
|---|---|---|---|
| T01 | Contact acceptant les partiels ; 50 disponibles et proposées | 50/80 = **62,5 %** : pas d’approbation nécessaire au titre de cette règle. | E-02 |
| T02 | Même contact ; 40 disponibles et proposées | 40/80 = **50 %** : approbation logistique nécessaire avant de poursuivre au point retenu. | E-02 |
| T03 | Contact refusant les partiels ; 50 disponibles | Livraison partielle bloquée ; attendre **80 unités**. Une approbation ne permet pas de contourner ce refus. | E-02 |
| T04 | Livraison approuvée à 50, puis abaissée à 40 | L’approbation antérieure ne suffit plus ; revalidation nécessaire. | E-02 |
| T05 | Livraison approuvée à 50, puis portée à 60 | Aucune revalidation nécessaire du seul fait de cette augmentation. | E-02 |

**Remarque sur T04 et T05 :** l’approbation à 50 est une précondition fournie par le scénario ; avec 80 unités commandées, la règle de seuil seule ne l’exigerait pas.

Critères complémentaires :

- [ ] À exactement **48 unités sur 80**, avec accord aux partiels et sans revalidation en attente, aucune approbation n’est requise.
- [ ] Un préparateur disposant aussi des droits logistiques ne peut pas approuver sa propre demande.
- [ ] Un autre responsable logistique habilité peut approuver une demande sous le seuil.
- [ ] Une diminution après approbation exige une revalidation même si la quantité reste au-dessus de 60 % : par exemple **60 → 50**, sur 80 commandées.
- [ ] Le cas **50 approuvé → 60 → 55** recevra un résultat attendu après réponse client ; aucun résultat n’est fixé ici.

Il s’agit de **tests à exécuter**, sans résultat d’exécution disponible.

### 6. Risques, découpage et QA

| Priorité | Risque | Traitement |
|---|---|---|
| P1 | Appliquer encore E-01 comme interdiction générale des partiels. | Utiliser E-02 et E-03 comme référence active. |
| P1 | Autoriser une auto-approbation par cumul des rôles. | Vérifier l’identité du demandeur en plus des droits. |
| P1 | Coder le calcul ou la revalidation avant les arbitrages. | Faire répondre aux quatre questions bloquantes. |
| P1 | Réimplémenter une fonction ou une personnalisation déjà présente. | Vérifier sources et inventaire avant conception technique. |
| P2 | Modifier le traitement des commandes ouvertes par une valeur implicite. | Définir et tester la reprise explicitement. |

Ordre proposé : **preuves standard/existant et arbitrages → conception du delta → implémentation → reprise éventuelle et recette**. Un chiffrage fiable attend les preuves et les réponses ; aucun effort de développement n’est engagé par cette revue.

**Niveau QA : renforcé**, car des droits d’approbation sont concernés. Prévoir une copie client, notamment pour vérifier les personnalisations et la reprise. Aucune copie n’est fournie ici.

L’utilisateur verra une case d’accord sur le contact de livraison, le motif d’un blocage et le statut d’approbation au point du workflow retenu.

## Entrée PROJECT.md à enregistrer

**Destination proposée :** `.odoo-agents/PROJECT.md`

### Compréhension métier

Entrepôt Cobalt utilise Odoo 19.0. L’autorisation d’expédier partiellement dépend du **contact de livraison**, puis d’un seuil de **60 % de la quantité commandée**. Sous ce seuil, un responsable logistique doit approuver. Le dossier ne fournit ni volumes réels ni état de la base.

### Décisions actées

- **E-02 remplace E-01** : l’obligation générale de livraison en une fois devient conditionnelle à l’accord du contact.
- **E-02** : accord aux partiels et quantité ≥ 60 % → sans approbation ; quantité < 60 % → approbation logistique.
- **E-02** : refus des partiels → attendre la quantité complète.
- **E-02** : diminution après approbation → revalidation ; augmentation → aucune revalidation.
- **E-03** : accord matérialisé par une case dédiée du contact de livraison.
- **E-03** : interdiction pour un préparateur d’approuver sa propre demande.

### En attente du client

Granularité du calcul ; étape de blocage ; reprise des commandes ouvertes et des contacts ; référence de comparaison après variations successives.

### État des connaissances

E-01 est déclarée non implémentée. L’état réel de la base, les personnalisations, la couverture standard 19.0 et celle de la série suivante sont inconnus. Aucune voie technique, livraison ou réussite de test n’est actée.

## Entrée JOURNAL.md à enregistrer

**2026-09-08 — Revue fonctionnelle sur dossier, préparée pour enregistrement**

- Sources utilisées : **E-01, E-02, E-03** exclusivement.
- Correction de référence identifiée : **E-02 remplace la règle générale E-01** ; E-03 précise le support de l’accord et interdit l’auto-approbation.
- Passation développeur/testeur préparée, avec les cinq scénarios demandés sur 80 unités et les contrôles de seuil et de droits.
- Quatre arbitrages client restent ouverts : granularité, workflow, reprise, référence après variations successives.
- Prochaine étape : obtenir ces arbitrages et vérifier le standard ainsi que l’existant client avant de choisir et chiffrer le delta.
- **Aucune opération réelle effectuée : ni lecture de sources ou de base, ni écriture de fichier, ni développement, déploiement ou test.**