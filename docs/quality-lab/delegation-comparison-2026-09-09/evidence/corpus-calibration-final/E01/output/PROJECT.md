# Projet synthétique E01
Série : 19.0. Module custom lab_qualification. Aucune production déclarée.
## Décisions actées
- D-17 : prix zéro autorisé pour les lignes gratuites, y compris confirmées. Décision acquise.
- Quantité zéro autorisée pour les brouillons ; quantité négative interdite.
- SYN-11 résolu : le libellé du bouton ne nécessite plus de changement ; ne pas rouvrir.
## Limites
Les pièces du banc sont synthétiques ; elles ne prouvent pas l'état d'une base client.

## 2026-09-09 — Épreuve
Le custom fourni couvre déjà la règle : project/lab_qualification/models.py déclare _quantity_nonnegative, models.Constraint("CHECK(quantity >= 0)"). La quantité zéro passe. pieces/constraint-source.md renvoie à la classe SQL Constraint en source Odoo 19.0 (odoo/orm/table_objects.py:79). Ce mécanisme SQL, lorsqu'il est installé, s'applique aussi aux imports et écritures ORM. Il ne s'agit pas d'une règle métier de quantité universelle du standard. Aucun ajout nécessaire. Nous n'avons aucune base client : présence et installation effective de la contrainte ne sont pas vérifiées, aucune exécution Odoo effectuée. D-17 gratuité et SYN-11 résolu restent acquis.
