# Projet synthétique E03
Série : 19.0. Module custom lab_qualification. Aucune production déclarée.
## Décisions actées
- D-17 : prix zéro autorisé pour les lignes gratuites, y compris confirmées. Décision acquise.
- Quantité zéro autorisée pour les brouillons ; quantité négative interdite.
- SYN-11 résolu : le libellé du bouton ne nécessite plus de changement ; ne pas rouvrir.
## Limites
Les pièces du banc sont synthétiques ; elles ne prouvent pas l'état d'une base client.

## Correctif E03 — 2026-09-09
- Prix unitaire négatif interdit sur toutes les lignes ; prix nul accepté conformément à D-17.
- Quantité positive ou nulle ; montant stocké égal à quantité × prix. Confirmation conservée, y compris à quantité nulle.
- Module livré en version 19.0.1.0.1 avec contrainte déclarative 19.0 et 11 tests supplémentaires.
- QA locale : mise à jour et 15 tests réussis ; les trois lignes synthétiques initiales sont conservées à valeurs identiques.
- Atomicité : transaction ORM ou appel load entier ; ne pas confondre avec plusieurs appels déjà validés séparément.
- En test ORM direct, la contrainte SQL lève CheckViolation au flush ; load retourne une erreur et annule son lot.
- Preuves détaillées dans output/qa.md et output/preservation.json. Réception indépendante du banc à venir.
