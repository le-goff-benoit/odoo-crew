Passation fondée uniquement sur le dossier fourni. Aucun fichier, paramétrage, développement, test ou déploiement n’a été réalisé.

**Règle actuelle et historique**

Projet Atelier Boréal, Odoo **19.0**.

- **M-02 remplace D-01** : le seuil de remise sans approbation est de **15 % pour un client partenaire** et de **10 % pour les autres clients**, bornes incluses. Au-delà, l’approbation du directeur est nécessaire.
- **M-03 précise la qualification** : le client est partenaire si la case « partenaire commercial » est cochée sur le **contact de facturation du devis**. La qualification ne doit pas être déduite d’un autre contact.
- **M-03 précise les droits** : un vendeur ne peut pas approuver sa propre demande. Le cumul éventuel des rôles vendeur et directeur ne lève pas cette interdiction.
- **M-02 impose la revalidation** : une augmentation de remise sur un devis déjà approuvé nécessite une nouvelle approbation ; une diminution ne la nécessite pas. Le texte ne prévoit pas d’exception pour une augmentation restant sous le seuil.

D-01, « remise commerciale maximale de 10 % pour tous les clients », reste dans l’historique comme décision remplacée avant développement. Elle ne constitue plus la règle à implémenter.

**Cas fournis**

| Situation | Résultat attendu | Source |
|---|---|---|
| Partenaire à 12 % | Aucune approbation requise au titre du seuil | M-02, M-03 |
| Non-partenaire à 12 % | Approbation du directeur requise | M-02 |
| Partenaire à 16 % | Approbation du directeur requise | M-02 |
| Devis approuvé à 16 %, passage à 17 % | Nouvelle approbation requise ; l’accord à 16 % ne couvre pas 17 % | M-02 |
| Devis approuvé à 16 %, passage à 14 % | Aucune revalidation requise du seul fait de cette diminution | M-02 |

Ces résultats concernent la remise ; ils ne préjugent pas de l’effet d’un changement simultané de contact ou d’autres données du devis.

**Questions ouvertes à conserver dans la spécification et la recette**

| Référence | Arbitrage nécessaire | Conséquence |
|---|---|---|
| Q1 | La remise désigne-t-elle chaque ligne, une remise globale ou un taux effectif calculé ? Quelle précision et quel arrondi appliquer ? | Bloque la définition du calcul et les tests de devis comportant plusieurs lignes. |
| Q2 | Quelle action doit être empêchée tant que l’approbation manque : envoi, confirmation, autre ? Quel parcours prévoir pour demande, refus et nouvelle soumission ? | Bloque la finalisation du workflow et des refus serveur correspondants. |
| Q3 | Qui détient le rôle de directeur ? Comment identifier la « propre demande » après un changement de vendeur ou de demandeur ? | Bloque le détail des habilitations et des cas de réaffectation. |
| Q4 | Que faire si le contact de facturation ou sa case partenaire change après la demande ou l’approbation ? | Bloque les règles de recalcul et de revalidation liées à ces changements. |
| Q5 | Après une approbation à 16 %, puis une baisse à 14 %, une remontée à 15 % exige-t-elle une revalidation ? | La lecture littérale de M-02 conduit à oui ; le traitement des modifications successives reste à confirmer explicitement. |
| Q6 | Quel traitement appliquer aux devis existants lors de la mise en service ? | La politique de reprise reste à arbitrer ; aucune approbation rétroactive ne doit être supposée. |

La lecture proposée pour Q5 n’est pas une décision client acquise. Les cas indépendants de ces réponses peuvent être préparés dès maintenant.

**Vérifications techniques à transmettre au développeur**

L’hébergement, les modules installés, les champs existants et les personnalisations ne sont pas documentés. **La couverture du standard et la voie d’implémentation restent non établies.**

Vérifier sur la série 19.0 la représentation de la remise, le champ partenaire commercial, les possibilités d’approbation, la revalidation et les contrôles serveur.

- **Configuration standard** : à privilégier si elle couvre intégralement les règles ; charge de migration généralement plus faible.
- **Studio** : à évaluer selon l’hébergement et les fonctions disponibles, en démontrant notamment les refus serveur et la revalidation. Ne pas présumer cette couverture.
- **Module spécifique** : envisageable si l’hébergement l’autorise et si les autres voies sont insuffisantes ; maintenance et adaptation aux migrations à prévoir. **Cette voie est exclue sur Odoo Online.**

Aucun chiffrage ferme n’est établi à ce stade.

**Critères d’acceptation pour le testeur**

Les critères suivants sont à exécuter après implémentation ; aucun n’a été testé.

1. Les cinq exemples du tableau produisent les résultats indiqués.
2. Un partenaire à **15 %** et un non-partenaire à **10 %** ne nécessitent pas d’approbation au titre du seuil. Le premier incrément représentable au-dessus de chaque seuil en nécessite une, selon la précision définie en Q1.
3. Si les cases partenaire du contact principal et du contact de facturation divergent, seule celle du contact de facturation détermine le seuil.
4. Un directeur habilité peut approuver une demande qui n’est pas la sienne. Un vendeur ne peut pas approuver sa propre demande, même s’il possède également le rôle directeur.
5. Toute tentative d’approbation sans habilitation ou d’auto-approbation est refusée **côté serveur**, y compris par un appel direct contournant l’écran.
6. Une hausse de 16 % à 17 % ne bénéficie pas de l’approbation antérieure. Une baisse de 16 % à 14 % ne déclenche pas de revalidation du seul fait de la baisse.
7. Après arbitrage de Q2, l’action métier retenue est refusée côté serveur lorsqu’une approbation initiale ou une revalidation manque.

Les scénarios de calcul détaillé, de réaffectation, de changement de qualification, de modifications successives et de reprise restent **en attente de Q1 à Q6**. Leur résultat attendu ne doit pas être inventé.

**Entrée PROJECT.md — prête à enregistrer**

> Projet : Atelier Boréal — Odoo 19.0.  
> Règle active : M-02 remplace D-01. Sans approbation, remise autorisée jusqu’à 15 % inclus pour les partenaires et 10 % inclus pour les autres ; au-delà, approbation du directeur. Selon M-03, partenaire = case partenaire commercial du contact de facturation du devis. Un vendeur ne peut pas approuver sa propre demande. Selon M-02, toute augmentation de remise d’un devis approuvé nécessite une revalidation ; une diminution ne la nécessite pas.  
> Historique : D-01 fixait 10 % pour tous les clients ; décision remplacée avant développement.  
> Questions ouvertes : Q1 assiette/précision de remise ; Q2 action bloquée et workflow ; Q3 habilitations et identité de la propre demande ; Q4 changement de contact/qualification ; Q5 modifications successives ; Q6 reprise des devis existants. Pour Q5, revalidation après remontée proposée selon la lecture littérale, sans validation client acquise.  
> Recette à préparer : seuils inclusifs, exemples 12 %/16 %, variations 16→17 et 16→14, contact de facturation déterminant, refus serveur des approbations interdites. Cas dépendant de Q1–Q6 en attente d’arbitrage.  
> Technique : standard et personnalisations non vérifiés ; hébergement et voie d’implémentation non établis. Aucun module spécifique possible sur Odoo Online.  
> État réel : passation textuelle préparée ; aucun développement, test ou déploiement réalisé.

**Entrée JOURNAL.md — prête à enregistrer**

> Analyse du dossier fourni pour la passation développeur/testeur, sans outils. Consolidation de M-02 et M-03 comme règle actuelle ; conservation de D-01 comme historique remplacé avant développement. Résultats attendus explicités pour les cinq exemples, les bornes et les droits serveur. Questions Q1–Q6 maintenues ouvertes dans la spécification, la recette et la mémoire ; aucune hypothèse transformée en décision client. Vérifications du standard Odoo 19.0 et des personnalisations proposées, sans verdict technique ni chiffrage ferme. Aucun fichier enregistré, aucun développement, test ou déploiement effectué.