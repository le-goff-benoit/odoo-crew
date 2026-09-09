# Revue fonctionnelle — jours de location non négatifs

Projet work · Odoo 19.0 (manifest) · lab_rental · décision D-31 dans decisions/2026-09-08.md.

## Besoin et verdict
En tant que gestionnaire, je veux refuser une durée négative pour conserver des locations cohérentes, tout en autorisant zéro jour.
**À DÉVELOPPER** : lab_rental/models/business.py définit lab.rental sans contrainte ; aucune configuration ne garantit le CHECK SQL demandé. Précédent 19.0 : addons/stock/models/stock_storage_category.py, `_positive_max_weight = models.Constraint('CHECK(max_weight >= 0)', ...)`. Recherche de lab.rental dans les sources 19.0 sans résultat. Sources 19.1 indisponibles : comparaison suivante non vérifiable, sans incidence sur ce modèle custom.

## Voies et décisions
Configuration : faible effort mais ne crée pas la contrainte SQL ; Studio : automatisation possible mais ne satisfait pas ce contrat SQL, avec maintenance à la migration ; module : ajout minimal et tests, contrôle de compatibilité à chaque migration. Voie module explicitement arbitrée par D-31.
Aucune question bloquante. D-31 remplace la tolérance historique du journal. La règle s'applique aux locations et prêts ; daily_rate et amount_total gardent leur règle actuelle, jours × tarif.

## Spécification
Ajouter une contrainte SQL Odoo 19.0 CHECK(days >= 0). Zéro explicite et zéro par défaut sont valides. Rejeter create et write négatifs ; après rollback du rejet, la location valide, son tarif et son total restent identiques et modifiables.
Aucun écran, droit, champ ni calcul à modifier. Pas de facturation, production, changement de version ou clôture.
Inventaire préalable sur lab_client : 0 location, 0 durée négative, 0 champ manuel sur lab.rental (preuve .odoo-agents/flow-artifacts/days-nonnegative/inventory.log). Aucune reprise de données nécessaire. Créer un témoin synthétique valide avant update pour prouver sa conservation, puis nettoyer les témoins de QA.

## Critères d'acceptation
- C1 : une création avec days = -1 est refusée par le CHECK SQL et ne laisse aucun enregistrement.
- C2 : une modification négative est refusée ; les valeurs persistées de la location valide sont conservées après rejet, puis une modification valide réussit.
- C3 : zéro explicite, par défaut et en modification est accepté, total nul.
- C4 : total = jours × tarif pour rental et loan ; recalcul sur changement des jours ou du tarif, tarifs négatif et nul toujours possibles.
- C5 : installation/tests ciblés et update sur lab_client passent ; contrainte présente et validée en PostgreSQL, données témoins conservées.

## QA et livraison
Un seul point, QA de tâche renforcée (contrainte sur table existante) : lint des fichiers touchés, tests ciblés avec preuve rouge puis verte, update et scénarios sur copie. Release laissée ouverte.
Ce que l'utilisateur verra : le message de rejet « Le nombre de jours doit être positif ou nul. » lors d'une durée négative ; aucun écran modifié.
