# Projet synthétique de qualification 19.0

## Compréhension métier
La quantité peut être nulle pendant la préparation ; une confirmation doit garantir une quantité positive par tous les canaux. Le montant est quantity × unit_price.

## Décisions actées
Module existant lab_qualification, voie module, aucune interface ou permission nouvelle. Jeu initial valide de trois lignes, copie locale restaurée depuis ordered_seed. Écritures et tests uniquement sur ordered_copy ; référence conservée. Aucun redressement automatique.

## Pièges connus
Une garde dans le seul bouton ne couvre pas les imports ni les écritures directes. Les preuves backend ne valent pas recette complète de release.

## Résultat acquis de la tâche A
La règle persistante impose quantity > 0 pour state=confirmed, tout en autorisant zéro au brouillon et en conservant le refus des négatifs. Les canaux bouton, create, write et load ont été contrôlés, y compris confirmation groupée et utilisateur interne non superutilisateur.
QA de tâche validée : mêmes 20 tests, 8 échecs métier sur le code initial puis 20/20 après correction ; 16 nouveaux tests et quatre anciens. La QA indépendante réutilise ces exécutions après contrôle de fraîcheur et vérifie directement images, schéma et conservation des trois lignes de chaque base.
La copie synthétique porte la nouvelle contrainte ; ordered_seed conserve le schéma initial. ACL, vue et version manifest 19.0.1.0.0 conservées. Aucun redressement historique.
Portée : Odoo 19.0, données synthétiques valides ; pas de navigateur, recette complète, copie client ni qualification d’un historique invalide. Les réceptions et l’état opérationnel sont dans le plan de la release ; celle-ci reste ouverte.
