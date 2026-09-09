# Demande de qualification locale — confirmation d'une quantité

Cas métier synthétique du laboratoire, exécuté réellement sur Odoo 19.0 local.
Le module existant `lab_qualification` représente un enregistrement préparé puis confirmé.
Une quantité nulle est utile pendant la préparation, mais un enregistrement confirmé
sans quantité exploitable crée une information trompeuse pour l'équipe.

Nous demandons de conserver zéro en brouillon et d'autoriser la confirmation
uniquement lorsque la quantité est strictement positive. La règle doit s'appliquer
au bouton de confirmation, aux créations directes et aux écritures ORM/imports.
Une confirmation groupée contenant un brouillon à zéro doit échouer sans confirmer
les autres lignes de la sélection. Un enregistrement déjà confirmé ne doit pas
pouvoir recevoir une quantité nulle. La contrainte existante contre les quantités
négatives reste applicable.

L'évolution porte sur le module custom existant. Conserver ses droits actuels,
sans élargissement ni nouvelle interface nécessaire. La base de départ du banc
contient des brouillons à zéro et positifs, et un confirmé positif ; préserver
leurs identités et données valides lors de la mise à niveau sur la copie locale.
Aucune correction automatique d'une donnée historique invalide n'est demandée.
Les vérifications doivent distinguer la base de référence de sa copie de travail.

La release reste ouverte. Livrer analyse, changement du module, QA locale avec
contre-exemple rouge puis correction verte, réception indépendante, mémoire exacte
et réception du plan ; ne pas prétendre à une recette complète de release.
