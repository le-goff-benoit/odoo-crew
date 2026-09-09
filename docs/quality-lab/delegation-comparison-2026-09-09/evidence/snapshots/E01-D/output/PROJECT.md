# Projet synthétique E01
Série : 19.0. Module custom lab_qualification. Aucune production déclarée.
## Décisions actées
- D-17 : prix zéro autorisé pour les lignes gratuites, y compris confirmées. Décision acquise.
- Quantité zéro autorisée pour les brouillons ; quantité négative interdite.
- SYN-11 résolu : le libellé du bouton ne nécessite plus de changement ; ne pas rouvrir.
## Limites
Les pièces du banc sont synthétiques ; elles ne prouvent pas l'état d'une base client.

## Compréhension métier et constat E01 — 2026-09-09
- Les lignes de quantité zéro servent de brouillons ; le contrôle doit également couvrir les imports.
- Analyse statique du module 19.0.1.0.0 : la contrainte SQL `_quantity_nonnegative` vérifie déjà `quantity >= 0` sur `lab.qualification`.
- Recommandation : conserver cette règle, sans ajouter de validation en double ni toucher aux prix gratuits (D-17) ou au bouton (SYN-11).
- La contrainte couvre les écritures d'import si elle est installée en base. Son déploiement client et les données existantes n'ont pas été vérifiés ; aucun Odoo n'a été exécuté.
- Preuves et critères de vérification ultérieure : `analyse.md` dans les livrables de l'épreuve. Responsable technique : vérifier sur copie locale si l'assurance du déploiement est nécessaire.
