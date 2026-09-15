# QA exécution — Odoo 19.0, tâche B-42

Pont réel `/bridge/labctl qa lab_register --quick --tags /lab_register:TestRepair`, base séparée lab_qa.
- Code initial conservé dans business-before.py ; `red.log` : 5 failed, 0 errors, 5 tests. Les échecs portent sur valeurs, périmètre et refus AccessError manquant, pas sur un problème de fixture. Durée pont : 17 s.
- Même fichier de tests après correctif, `green.log` : 0 failed, 0 errors, 5 tests, 0 skipped ; install=ok, update=ok, durée 6 s. La statistique interne affiche 7 avec les étapes de fixture, le nombre de scénarios est bien 5.
- Cas réellement joués : sélection mixte hors ordre, égalité de date départagée par ID, brouillon non sélectionné, deux sociétés autorisées et changement d'active, sélection vide, total sans ligne/annulé/précision 0.001, références émises, idempotence instrumentée.
- Utilisateurs internes non sudo : succès permis, société interdite refusée, allowed_company_ids forgé refusé, règle de refus write testée même sur valeurs déjà correctes. Les assertions contrôlent l'état après refus ; aucune règle du projet n'a été modifiée.
- 3 warnings auteur absent : même dette manifest qu'en statique. Aucun autre échec ni test ignoré.
Pas de recette intégrale de release (désinstallation/tours) : tâche uniquement, release ouverte. Aucune preuve de navigateur ou de RPC externe revendiquée ; les droits sont prouvés par ORM sous utilisateurs ordinaires. Relecture non indépendante.
