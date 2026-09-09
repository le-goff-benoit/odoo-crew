# Journal du projet synthétique

## 2026-09-09 — Préparation
Demande : qualifier un invariant à la confirmation sur Odoo 19.0.
Fait : copie synthétique effectivement restaurée, trois identités et valeurs conservées ; analyse indépendante terminée.
Verdict : module requis, QA renforcée ; développement et réception encore à réaliser.
Appris : vérifier les canaux create/write/load et la contrainte effective.
Reste ouvert : tâche et release.

## 2026-09-09 — Quantité positive à la confirmation
Demande : conserver zéro au brouillon et refuser les confirmés non positifs, par bouton et canaux ORM/import.
Fait : contrainte persistante ajoutée, négatifs toujours refusés, aucune modification de droits/vue ni réparation historique.
Verdict acquis : QA de tâche VALIDÉE ; 8 échecs métier sur 20 au rouge puis mêmes 20/20 au vert, lint 0 erreur/avertissement.
Contrôle indépendant : tests relus et réutilisés, contrôle live des deux bases ; trois IDs et valeurs initiaux conservés, contrainte nouvelle uniquement sur copie.
Appris : un contrôle neuf de fraîcheur/copie peut réutiliser les tests valables ; il ne constitue pas une nouvelle exécution de ces tests.
Portée : copie synthétique Odoo 19.0, pas de données client ni d’historique invalide testé ; détails et réceptions dans la release.
Reste ouvert : release, recette complète et tâche C témoin non exécutée ; état des tâches dans plan.json.
