# Projet synthétique E01
Série : 19.0. Module custom lab_qualification. Aucune production déclarée.
## Décisions actées
- D-17 : prix zéro autorisé pour les lignes gratuites, y compris confirmées. Décision acquise.
- Quantité zéro autorisée pour les brouillons ; quantité négative interdite.
- SYN-11 résolu : le libellé du bouton ne nécessite plus de changement ; ne pas rouvrir.
## Limites
Les pièces du banc sont synthétiques ; elles ne prouvent pas l'état d'une base client.

## Analyse E01 — 2026-09-09
- Compréhension métier : bloquer les quantités négatives en saisie et import, conserver les brouillons à quantité zéro, éviter les contrôles en double.
- Constat sur le module fourni : models.py:16–18 contient déjà CHECK(quantity >= 0), porté par models.Constraint en 19.0.
- Recommandation : conserver ce contrôle ; aucun développement supplémentaire justifié. Ne pas durcir la règle de confirmation ni modifier les prix.
- Couverture des imports déduite de la contrainte SQL, sous réserve de sa présence effective en base ; aucun essai Odoo exécuté.
- Suite si validation réelle nécessaire : responsable technique pour version/contrainte sur copie locale, QA pour saisie et imports aux bornes négative, zéro et positive.
- Preuve détaillée : output/analyse.md. SYN-11 clos et D-17 restent applicables.
