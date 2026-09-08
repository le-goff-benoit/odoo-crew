Voici la passation et les contenus proposés pour `PROJECT.md` et `JOURNAL.md`. Ils sont à enregistrer : aucun fichier, état de base, développement, déploiement ou test n’a été consulté ou exécuté.

**Passation développeur/testeur**

Entrepôt Cobalt — série Odoo 19.0. Le besoin concerne l’autorisation des livraisons partielles selon le consentement du contact de livraison, la disponibilité et, si nécessaire, l’approbation logistique.

| Source | Décision fournie | Statut |
|---|---|---|
| E-01 | Toutes les commandes doivent être livrées en une fois. | Règle historique, non implémentée, remplacée par E-02. |
| E-02 | Contact acceptant les partiels : livraison sans approbation dès 60 % disponibles ; en dessous, approbation du responsable logistique. | Règle actuelle. |
| E-02 | Contact refusant les partiels : attendre la quantité complète. | Règle actuelle ; aucune dérogation par approbation n’est prévue. |
| E-02 | Une livraison partielle approuvée doit être revalidée si la quantité proposée diminue, pas si elle augmente. | Règle actuelle ; référence lors de variations successives non arbitrée. |
| E-03 | Le consentement est une case dédiée du contact de livraison. | Règle actuelle ; existence du champ en base non vérifiée. |
| E-03 | Un préparateur ne peut pas approuver sa propre demande. | Règle actuelle, y compris s’il possède aussi le rôle de responsable logistique. |

Les acteurs sont le préparateur, le responsable logistique et le contact de livraison porteur du consentement. Le droit d’approbation appartient au responsable logistique, sous réserve de l’interdiction d’autoapprobation. L’autorisation décrite ici concerne cette règle métier ; elle ne dispense pas des autres contrôles de livraison.

Les points suivants attendent une décision client. Ils doivent rester ouverts dans la spécification et la recette :

| Point à arbitrer | Conséquence |
|---|---|
| Calcul par ligne ou sur l’ensemble de la commande | Empêche de définir le comportement multiligne. Si le calcul est global, préciser l’agrégation de produits et unités différents. |
| Point du workflow où bloquer | Empêche de fixer l’action exacte à refuser et le contrôle serveur associé. |
| Reprise des commandes ouvertes | Empêche de déterminer quelles commandes existantes doivent appliquer la nouvelle règle et comment les traiter. |
| Référence après variations successives | Empêche de décider, par exemple, du cas « approuvée à 50, augmentée à 60, puis diminuée à 55 ». |

Pour rendre la règle implémentable, il faut également préciser la définition de la « quantité disponible » et son articulation avec la quantité proposée à la livraison. Ce sont deux notions distinctes dans E-02 ; leur équivalence ne doit pas être supposée. Les droits de modification de la case de consentement et son initialisation restent à définir si aucune règle existante de la série ne les couvre.

Les vérifications techniques à prévoir portent sur les paramètres de livraison, les quantités disponibles/réservées, les mécanismes d’approbation, les droits et les personnalisations existantes de la série. Aucun résultat n’est disponible.

| Voie | Évaluation à mener |
|---|---|
| Configuration standard | À retenir si elle couvre toutes les règles, notamment le seuil, la revalidation et les refus serveur. Coût de maintenance et de migration généralement plus limité. |
| Studio | À évaluer pour le champ et les mécanismes configurables. La couverture des transitions et de la sécurité serveur reste à démontrer ; aucune promesse de contournement de ses limites. |
| Module spécifique | À envisager si les autres voies sont insuffisantes et si l’hébergement l’autorise. Implique maintenance et adaptation aux migrations. Impossible sur Odoo Online. |

L’hébergement, les applications installées et les personnalisations ne sont pas fournis. **Le verdict sur le standard et la voie de réalisation restent non établis**, sans chiffrage ferme.

La recette ci-dessous exprime les résultats attendus, sans prétendre à leur exécution. Pour isoler les règles connues, les cas utilisent une commande d’une seule ligne de 80 unités dans une même unité de mesure. Cette convention de recette ne tranche pas le calcul multiligne.

| Cas demandé | Résultat attendu selon E-02 |
|---|---|
| Contact acceptant les partiels, 50 disponibles | 50/80 = 62,5 % : livraison partielle permise sans approbation au titre du seuil. |
| Même contact, 40 disponibles | 40/80 = 50 % : approbation du responsable logistique nécessaire. |
| Contact refusant les partiels, 50 disponibles | Livraison partielle interdite ; attendre les 80 unités. Une approbation ne lève pas ce refus. |
| Livraison approuvée à 50, quantité proposée abaissée à 40 | Nouvelle approbation nécessaire ; l’approbation à 50 ne suffit plus. |
| Livraison approuvée à 50, quantité proposée portée à 60 | Pas de revalidation du seul fait de l’augmentation. |

Cas complémentaires discriminants à conserver :

- Contact acceptant : 48/80, soit exactement 60 %, ne nécessite pas d’approbation ; 47/80 en nécessite une.
- Livraison approuvée à 60 puis abaissée à 50 : revalidation nécessaire malgré un ratio restant supérieur à 60 %.
- Contact refusant : à 80 disponibles, l’exigence de quantité complète est satisfaite.
- Responsable logistique distinct du demandeur : approbation recevable. Préparateur approuvant sa propre demande, même également responsable logistique : refus serveur.
- Utilisateur sans droit d’approbation : refus serveur, y compris par appel direct hors écran. Vérifier également l’impossibilité de franchir le blocage sans l’approbation requise, une fois l’étape choisie.
- Séquence 50 approuvées → 60 → 55, commandes multiligne et commandes ouvertes : résultats attendus suspendus aux arbitrages correspondants.

**Contenu proposé pour `PROJECT.md`**

```markdown
# Entrepôt Cobalt — Livraisons partielles
Série : Odoo 19.0.

## Sources et règle actuelle
- E-02 remplace E-01 : contact de livraison acceptant les partiels,
  livraison sans approbation dès 60 % de la quantité commandée disponible ;
  en dessous, approbation du responsable logistique.
- E-02 : contact refusant les partiels, attendre la quantité complète.
  Aucune dérogation par approbation n'est prévue.
- E-02 : livraison partielle approuvée, revalidation si la quantité proposée
  diminue ; pas de revalidation du seul fait d'une augmentation.
- E-03 : consentement porté par une case dédiée du contact de livraison.
- E-03 : un préparateur ne peut pas approuver sa propre demande.

## Historique
- E-01 : livraison intégrale obligatoire pour toutes les commandes.
  Non implémentée ; décision remplacée par E-02.

## Arbitrages client ouverts
- Granularité du calcul : ligne ou ensemble.
- Point du workflow où bloquer.
- Politique de reprise des commandes ouvertes.
- Référence de comparaison après variations successives.
Aucune hypothèse n'est validée par silence.

## Précisions à obtenir ou à vérifier dans l'existant
- Définition de la quantité disponible et relation avec la quantité proposée.
- Initialisation et droits de modification du consentement.
- Hébergement, applications, configurations et personnalisations existantes.

## Recette attendue — non exécutée
Convention : une ligne de 80 unités ; ne tranche pas le multiligne.
- Consentement oui, disponibles 50 : sans approbation (62,5 %).
- Consentement oui, disponibles 40 : approbation requise (50 %).
- Consentement non, disponibles 50 : attendre 80.
- Approuvée à 50 puis proposée à 40 : revalidation.
- Approuvée à 50 puis proposée à 60 : pas de revalidation pour l'augmentation.
- Seuil : 48 sans approbation ; 47 avec approbation.
- Approuvée à 60 puis abaissée à 50 : revalidation malgré le seuil atteint.
- Refus serveur : autoapprobation et approbation sans rôle autorisé.
- Contrôle serveur du blocage à définir après choix de l'étape.
- Attendus ouverts : multiligne, reprise et séquences de variations.

## État et voie technique
Analyse textuelle sur dossier uniquement.
Aucun état de base, développement, déploiement ou test fourni.
Standard et personnalisations non vérifiés ; voie non établie.
Comparer configuration, Studio et module selon couverture et migration.
Odoo Online exclut le module spécifique.
Aucun chiffrage ferme.
```

**Entrée proposée pour `JOURNAL.md`**

```markdown
## Analyse du dossier E-01 à E-03 — exercice sans outils
- Passation développeur/testeur et contenus documentaires préparés en texte.
- E-01 conservée comme historique non implémenté.
- E-02 retenue comme correction client actuelle ; E-03 précise le support
  du consentement et l'interdiction d'autoapprobation.
- Cinq cas demandés qualifiés ; critères de seuil, revalidation et refus
  serveur ajoutés à la recette proposée.
- Arbitrages maintenus ouverts : granularité, étape de blocage, reprise
  des commandes ouvertes, référence après variations successives.
- Précisions à obtenir : disponibilité, relation à la quantité proposée,
  initialisation et droits du consentement.
- Vérification du standard, des personnalisations et de l'hébergement
  à réaliser avant choix technique.
- Aucun outil utilisé ; aucun fichier enregistré, aucune base consultée,
  aucun développement, test ou déploiement exécuté.
```