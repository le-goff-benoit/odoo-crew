# Analyse courte — E03, Odoo 19.0

La demande originale tient lieu de spécification pour cette épreuve, sans flow de livraison.
Le briefing hors ligne confirme la série 19.0 par `.odoo-agents/config`.

## Besoin et décision

Toute ligne doit respecter `unit_price >= 0` et `quantity >= 0` ; le montant stocké reste `quantity × unit_price`.
La décision D-17 autorise explicitement la gratuité, y compris après confirmation. SYN-11 reste résolu : aucun changement de libellé du bouton.
La confirmation existante ne conditionne pas la quantité : elle reste utilisable sur les lignes valides, y compris à quantité nulle.

Le modèle custom possède déjà une contrainte SQL sur la quantité et un calcul stocké correctement dépendant des deux facteurs. Aucun contrôle du prix n'est présent.
Le module existant est la voie adaptée : une seule contrainte déclarative 19.0 couvre le modèle, quel que soit le point d'entrée. Une configuration de vue ne protégerait pas les imports. Studio ajouterait une seconde couche sans avantage dans ce projet à module.
Aucun modèle, droit, champ de société ou parcours supplémentaire n'est nécessaire.

## Critères d'acceptation

1. Prix strictement négatifs rejetés à la création et à la modification, même avec quantité nulle, valeur négative très petite ou valeur issue du contexte.
2. Prix nul accepté en création, modification, import et confirmation ; prix positif accepté.
3. Quantité négative toujours rejetée ; quantité nulle acceptée.
4. Montant recalculé et relu après modification de chacun des deux facteurs.
5. Création multiple et modification multiple en erreur : aucune modification partielle après annulation de la transaction.
6. `load` valide accepte le lot ; `load` contenant une erreur annule les créations et les modifications valides du même appel et retourne un message d'erreur.
7. Confirmation seule et multiple fonctionnelle ; données des trois lignes initiales identiques après mise à jour.

## Données et transaction

L'inventaire exécuté avant correction retrouve les trois lignes synthétiques initiales (payante, gratuite, quantité nulle), toutes valides ; aucun nettoyage ni script de migration des données n'est requis sur cette copie.
La contrainte est évaluée par PostgreSQL au flush. L'ORM direct lève `CheckViolation` ; `load` convertit l'erreur en message et annule son savepoint global. L'atomicité porte sur la transaction ou l'appel `load`, pas sur plusieurs appels déjà validés séparément.

## Sources consultées

- `project/lab_qualification/models.py`, tests existants, manifest, vue et mémoires initiales.
- Sources locales 19.0 : `addons/stock/models/stock_storage_category.py:25` (contrainte non négative déclarative).
- `odoo/addons/base/tests/test_sql.py:181` (exception SQL attendue en test ORM).
- `odoo/orm/models.py:895–1065` (contrat `load`, flush et annulation complète en cas d'erreur).
- Référentiel figé : rôles functional-review, implementation et qa-review.

## Limites

Les observations concernent exclusivement la copie synthétique fournie. Aucune base client ni production n'est interrogée.
L'état d'éventuelles données anciennes d'un autre déploiement n'est pas établi par ce test ; la réception du banc est indépendante et ultérieure.
