# Résultat /odoo-new — D-22
VALIDÉ sur la copie locale Odoo 19.0. Un seul champ Studio ajouté : x_studio_needs_review, boolean stocké dépendant des deux champs existants, vrai pour les locations de 7 jours ou plus, faux pour les prêts.
Pack versionnable et scripts RPC livrés dans changelog/2026-09-09_01_indicateur-de-revue-d-22/studio/. Première application : 1 création ; seconde : aucun changement ; diff nul, scénarios verts et aucun doublon. Données et actions de recette nettoyées.
QA dans la release, JOURNAL.md et PROJECT.md actualisés. Point 1 réalisé, release ouverte. Aucun écran, module custom ni déploiement.
Limite : modèle préexistant sans ACL ; scénarios exécutés via action temporaire avec sudo local documenté. Accès métier non validé. Comparaison 19.1 indisponible ; recette de clôture non exécutée.
