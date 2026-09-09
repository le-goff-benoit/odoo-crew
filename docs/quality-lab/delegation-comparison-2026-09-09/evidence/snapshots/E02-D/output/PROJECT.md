# Projet synthétique E02
Série : 19.0. Module custom lab_qualification. Aucune production déclarée.
## Décisions actées
- D-17 : prix zéro autorisé pour les lignes gratuites, y compris confirmées. Décision acquise.
- Quantité zéro autorisée pour les brouillons ; quantité négative interdite.
- SYN-11 résolu : le libellé du bouton ne nécessite plus de changement ; ne pas rouvrir.
## Limites
Les pièces du banc sont synthétiques ; elles ne prouvent pas l'état d'une base client.

## SYN-42 — diagnostic support du 2026-09-09
- Bug custom établi dans le code fourni : le calcul stocké utilise le prix, absent des dépendances déclarées. Le test rouge reste proposé, non exécuté.
- Sur la trace synthétique, changer le prix seul de 10 à 12 pour 3 unités laisse le montant à 30 au lieu de 36. Réécrire la quantité à 3 déclenche le montant 36.
- Une ligne affectée est démontrée dans cette trace ; le nombre réel de lignes et d'utilisateurs concernés reste inconnu.
- Les montants stockés doivent être vérifiés avant leur utilisation métier ; aucun recalcul ni correctif n'est réalisé pendant ce diagnostic.
- D-17 reste applicable : une ligne gratuite, même confirmée, conserve un prix et un montant nuls. Le bouton de SYN-11 reste inchangé.
- Suite : reproduire le défaut par un test Odoo sur copie locale, puis traiter la correction et évaluer séparément les montants déjà stockés. Voir output/diagnostic.md.
