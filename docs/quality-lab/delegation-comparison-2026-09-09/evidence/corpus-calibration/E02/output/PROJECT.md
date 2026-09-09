# Projet synthétique E02
Série : 19.0. Module custom lab_qualification. Aucune production déclarée.
## Décisions actées
- D-17 : prix zéro autorisé pour les lignes gratuites, y compris confirmées. Décision acquise.
- Quantité zéro autorisée pour les brouillons ; quantité négative interdite.
- SYN-11 résolu : le libellé du bouton ne nécessite plus de changement ; ne pas rouvrir.
## Limites
Les pièces du banc sont synthétiques ; elles ne prouvent pas l'état d'une base client.

## 2026-09-09 — Épreuve
Bug custom : _compute_amount lit unit_price mais @api.depends ne déclare que quantity (project/lab_qualification/models.py). La source 19.0 décrite dans pieces/dependencies-source.md confirme le rôle de déclaration des dépendances. La trace synthétique pieces/orm-trace.jsonl, séquences 1 et 2, montre quantité3 prix10 montant30 puis prix12 montant30, au lieu de36. Le flush et la relecture sont dans la pièce, pas exécutés ici. La séquence3 montre un contournement : réécrire la quantité identique provoque36 ; à valider sur copie réelle avant usage, aucune réparation de production autorisée. La cause touche les montants stockés après modification du prix ; proposer ensuite ajout de dépendance et inventaire/recalcul contrôlé des données existantes dans un périmètre séparé. Test rouge proposé mais non exécuté : créer qty3 prix10, vérifier30, write prix12, flush/relecture, attendu36. Ajouter non-régression gratuité et état confirmé. pieces/decisions.md D-17 autorise déjà prix0 même confirmé, sans nouvelle confirmation ; SYN-11 est un ticket distinct résolu, bouton inchangé. Aucun correctif livré dans ce diagnostic ; limite : pièces synthétiques seulement.
