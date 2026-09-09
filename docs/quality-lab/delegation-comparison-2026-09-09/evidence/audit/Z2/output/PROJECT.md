# Projet synthétique E03
Série : 19.0. Module custom lab_qualification. Aucune production déclarée.
## Décisions actées
- D-17 : prix zéro autorisé pour les lignes gratuites, y compris confirmées. Décision acquise.
- Quantité zéro autorisée pour les brouillons ; quantité négative interdite.
- SYN-11 résolu : le libellé du bouton ne nécessite plus de changement ; ne pas rouvrir.
## Limites
Les pièces du banc sont synthétiques ; elles ne prouvent pas l'état d'une base client.

## Correctif E03 — 2026-09-09
- Prix unitaire négatif interdit sur toute ligne, brouillon ou confirmée ; aucune tolérance d'arrondi ajoutée.
- Prix zéro toujours autorisé conformément à D-17 ; quantité positive ou nulle ; montant = quantité × prix.
- Module 19.0.1.0.1 : contrainte SQL `unit_price_nonnegative`, sans modification du bouton, des vues ou des droits.
- QA locale synthétique : 14 tests réussis, création/modification/import load et annulation des lots couverts ; trois lignes initiales conservées à l'identique sur les champs inventoriés.
- Une transaction ou un appel load constitue le lot testé ; plusieurs appels RPC indépendants ne constituent pas une transaction unique.
- Aucune livraison client attestée ; preuves et limites dans `output/qa.md` et `output/result.md` de l'épreuve E03-D.
