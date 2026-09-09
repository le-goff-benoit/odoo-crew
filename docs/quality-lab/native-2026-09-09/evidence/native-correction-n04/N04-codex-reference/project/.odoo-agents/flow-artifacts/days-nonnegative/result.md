# Résultat /odoo-new — D-31
lab_rental 19.0 : contrainte SQL CHECK(days >= 0) livrée, zéro valide et calcul conservé. Quatre tests couvrent créations et modifications refusées, conservation de la location après rejet, zéro et calcul rental/loan.
4/4 tests verts, update lab_client et scénarios copie verts, CHECK PostgreSQL effectivement validé ; témoins nettoyés. Ruff vert. Réserve explicite : lint global rouge sur author absent du manifest avant cette tâche, reproduit sur référence Git ; aucun défaut nouveau.
Revue, demande, qa.md et suivi écrits dans changelog/2026-09-09_01_jours-de-location-non-negatifs. Journal et PROJECT mis à jour. Point 1 réalisé ; release ouverte. Aucun écran/droit modifié, aucun commit ni livraison de production. Recette complète à la clôture.
