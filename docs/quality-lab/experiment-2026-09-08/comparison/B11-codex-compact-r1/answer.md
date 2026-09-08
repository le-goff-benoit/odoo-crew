**Passation développeur / testeur — Entrepôt Cobalt, Odoo 19.0**

Document préparé uniquement à partir du dossier fourni. Aucune consultation de base, modification de fichier, réalisation technique ou exécution de test. Les entrées de mémoire ci-dessous restent à enregistrer.

**Besoin et règles applicables**

Le besoin est de permettre les expéditions partielles selon l’accord du contact de livraison et la disponibilité, tout en contrôlant les dérogations et la validité des approbations.

| Référence | Règle et statut |
|---|---|
| E-01 | Ancienne décision : toutes les commandes devaient être livrées en une fois. Non implémentée selon le dossier. Remplacée par E-02 ; à conserver comme historique. |
| E-02 | Si le contact de livraison accepte les partiels, une livraison est autorisée sans approbation dès que la disponibilité atteint **60 %** de la quantité commandée. En dessous, l’approbation du responsable logistique est nécessaire. |
| E-02 | Si le contact refuse les partiels, attendre la quantité complète. Aucune dérogation par approbation n’est prévue dans cette branche. |
| E-02 | Une livraison partielle déjà approuvée doit être revalidée si la quantité proposée diminue ; une augmentation ne demande pas de revalidation. La référence lors de variations successives reste à arbitrer. |
| E-03 | L’accord aux partiels est porté par une **case dédiée du contact de livraison**. |
| E-03 | Un préparateur ne peut pas approuver sa propre demande. Cette interdiction s’applique également s’il possède par ailleurs le rôle de responsable logistique. |

Acteurs : le préparateur propose la livraison et, lorsque nécessaire, demande une approbation ; le responsable logistique approuve les demandes admissibles ; le contact de livraison porte le choix autorisant ou refusant les partiels.

La disponibilité détermine le seuil ; la quantité proposée détermine les variations à contrôler après approbation. Ces deux notions doivent rester distinctes dans la conception.

**Cas demandés et résultats attendus**

Pour ces exemples, les 80 unités constituent un seul périmètre de calcul. Cela permet de traiter les cas sans décider du calcul sur une commande multiligne.

| Situation | Calcul | Résultat attendu |
|---|---:|---|
| Contact acceptant les partiels, 50 disponibles sur 80 | 62,5 % | Livraison partielle autorisée sans approbation au titre de cette règle. |
| Même contact, 40 disponibles sur 80 | 50 % | Approbation du responsable logistique nécessaire avant d’autoriser la livraison partielle. Le préparateur demandeur ne peut pas l’accorder lui-même. |
| Contact refusant les partiels, 50 disponibles sur 80 | 62,5 % | Livraison partielle bloquée ; attendre les 80 unités. Une approbation ne lève pas ce refus. |
| Livraison approuvée à 50, puis proposition abaissée à 40 | Diminution | Nouvelle validation nécessaire ; l’approbation à 50 ne suffit plus pour autoriser 40. |
| Livraison approuvée à 50, puis proposition portée à 60 | Augmentation | Aucune revalidation requise pour cette augmentation. |

Dans les deux derniers cas, on suppose que le contact accepte les partiels et que les autres paramètres sont inchangés. L’approbation initiale à 50 est une donnée du scénario, même si le seuil permettrait une livraison sans approbation.

« Autorisée » signifie ici que cette règle métier ne bloque pas ; cela ne dispense pas des autres contrôles Odoo.

**Arbitrages client encore ouverts**

| Question | Conséquence sur la réalisation et la recette |
|---|---|
| Le seuil s’applique-t-il par ligne ou à l’ensemble de la commande ? | Bloque la définition du calcul multiligne. Si le calcul est global, préciser comment agréger des produits et unités différents. |
| À quelle étape du workflow faut-il bloquer ? | Bloque le placement définitif du contrôle : préparation, validation du transfert ou autre étape à nommer. |
| Quelle politique pour les commandes ouvertes ? | Bloque la définition de la reprise : périmètre, traitement de la case et des éventuelles approbations antérieures. Aucun rattrapage implicite. |
| Quelle quantité sert de référence après plusieurs variations ? | Bloque les scénarios successifs, notamment approbation à 50 → proposition à 60 → proposition à 55 : référence à la dernière approbation ou à la proposition précédente ? |

Ces points restent ouverts dans la spécification, la recette et la mémoire. Le silence du client ne valide aucune option. Les règles établies, les cinq cas ci-dessus et l’étude des capacités techniques peuvent être préparés sans attendre.

**Vérifications techniques et choix de réalisation**

Le dossier ne permet pas de conclure sur la couverture du standard Odoo 19.0 ou des personnalisations de cette série. L’hébergement, les modules installés, les règles de livraison, les champs existants et les mécanismes d’approbation sont à vérifier.

| Voie à examiner | Couverture à démontrer | Maintenance et migration |
|---|---|---|
| Configuration standard | Accord au niveau du contact, seuil de 60 %, approbation conditionnelle, revalidation et interdiction d’auto-approbation. | À privilégier si la couverture est complète ; moins de composants spécifiques à maintenir. |
| Studio | Capacité à porter les champs et le workflow nécessaires, avec des refus effectifs côté serveur. | Vérifier les limites réelles et la portabilité des automatisations lors des migrations. Une restriction d’écran ne suffit pas. |
| Module spécifique | Possibilité de couvrir les règles non satisfaites par les autres voies et les contrôles serveur. | Développement, maintenance et adaptations de migration à prévoir. Voie exclue si l’hébergement est Odoo Online. |

**Verdict et voie retenue : non établis.** Aucun chiffrage ferme n’est justifié à ce stade.

La conception devra permettre d’identifier le demandeur, l’approbateur et la quantité approuvée pour contrôler les droits et la revalidation. Leur représentation technique reste à choisir après inspection de l’existant.

Les refus doivent être effectifs côté serveur, y compris lors d’un appel direct contournant l’interface :

- refuser l’approbation par une personne sans le rôle requis ;
- refuser l’auto-approbation du préparateur demandeur ;
- empêcher le franchissement de l’étape retenue quand une approbation manque ou doit être renouvelée ;
- empêcher une approbation de contourner le refus des partiels du contact.

**Recette à préparer — non exécutée**

Reprendre les cinq cas demandés, puis ajouter les cas discriminants suivants :

| Cas | Attendu ou état |
|---|---|
| Contact acceptant, 48 disponibles sur 80 | Exactement 60 % : aucune approbation nécessaire. |
| Contact acceptant, 47 disponibles sur 80 | Sous 60 % : approbation nécessaire. |
| Contact refusant, 80 disponibles sur 80 | La règle de livraison complète ne bloque plus. |
| Approbation à 60, proposition abaissée à 50 | Revalidation nécessaire selon E-02, même si 50 représente encore 62,5 %. Le contrôle de diminution doit rester distinct du seuil. |
| Préparateur également responsable logistique, approbation de sa propre demande | Refus côté serveur. |
| Autre responsable logistique approuvant une demande sous le seuil | Approbation possible sous réserve des autres contrôles applicables. |
| Deux lignes de 40 unités, disponibles respectivement à 40 et à 8 | Total de 60 %, mais seconde ligne à 20 % : attendu suspendu à l’arbitrage de granularité. |
| Approbation à 50 → proposition à 60 → proposition à 55 | Attendu suspendu à l’arbitrage sur la référence successive. |
| Commande ouverte avant activation de la règle | Attendu suspendu à la politique de reprise. |

Les tests de blocage au workflow seront finalisés après désignation de l’étape à contrôler. Aucun de ces tests n’est déclaré passé.

**Entrée PROJECT.md proposée — à enregistrer**

- **Projet / série :** Entrepôt Cobalt — Odoo 19.0.
- **Objet :** encadrement des expéditions partielles.
- **Règle actuelle :** E-02 remplace E-01. Accord aux partiels via la case dédiée du contact de livraison [E-03]. Avec accord : disponibilité ≥ 60 % de la quantité commandée, sans approbation ; sous 60 %, approbation du responsable logistique [E-02]. Sans accord : attendre la quantité complète [E-02].
- **Approbations :** diminution de la quantité proposée après approbation ⇒ revalidation ; augmentation ⇒ aucune revalidation [E-02]. Auto-approbation du préparateur interdite [E-03], contrôle serveur requis.
- **Historique :** E-01 imposait la livraison en une fois ; règle non implémentée selon le dossier, remplacée par E-02.
- **Arbitrages client ouverts :** calcul par ligne ou global ; étape de blocage ; reprise des commandes ouvertes ; référence après variations successives.
- **Hypothèses de recette limitées :** les exemples à 80 unités utilisent un seul périmètre de calcul ; les variations après approbation supposent un contact acceptant les partiels. Aucune de ces hypothèses ne vaut décision générale.
- **Voie technique :** non établie ; standard et personnalisations à examiner. Hébergement inconnu ; module spécifique exclu sur Odoo Online.
- **État réel :** passation textuelle préparée sur dossier uniquement. Aucun état de base fourni, aucun développement, déploiement ou résultat de test attesté. Recette définie partiellement ; cas dépendant des arbitrages maintenus ouverts.

**Entrée JOURNAL.md proposée — à enregistrer**

- **Objet :** préparation de la passation développeur/testeur sur dossier E-01, E-02 et E-03.
- **Décisions consolidées :** E-01 conservée comme historique non implémenté ; E-02 retenue comme règle actuelle ; E-03 précise le support de l’accord et interdit l’auto-approbation.
- **Analyse produite :** cinq cas à 80 unités, seuil exact à 48 unités, contrôles serveur, cas discriminants de revalidation et de granularité.
- **Points laissés ouverts :** granularité, étape du workflow, reprise des commandes ouvertes et référence des variations successives. Aucun arbitrage déduit du silence.
- **Limites :** aucune vérification du standard ou des personnalisations ; aucune voie technique choisie ; aucun fichier enregistré et aucun test exécuté.
- **Suite :** obtenir les quatre arbitrages client, examiner les capacités de la série et l’hébergement, puis finaliser la conception et les attendus de recette concernés.