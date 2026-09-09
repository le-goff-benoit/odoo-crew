# Revue fonctionnelle — Jours de location non négatifs

Projet /work · module lab_rental · Odoo 19.0 (manifest).

## Besoin et verdict
En tant que gestionnaire, je veux refuser les durées négatives afin de conserver des locations cohérentes, tout en acceptant zéro jour.
**À DÉVELOPPER** : `lab_rental/models/business.py` déclare le modèle custom sans contrôle des jours. Recherche `lab.rental` sans résultat dans les sources 19.0 communautaires et enterprise ; forme SQL native attestée dans `19.0/addons/sale/models/sale_order.py:41` et `19.0/odoo/orm/table_objects.py`.
Série suivante : sources 19.1 absentes du laboratoire ; comparaison non exécutée, sans incidence sur ce modèle propre au laboratoire.
Copie `lab_client` inventoriée : 0 location, 0 durée négative, aucune contrainte CHECK, aucun champ manuel sur le modèle, base_automation non installé. Preuve : `.odoo-agents/flow-artifacts/days-nonnegative/inventory-before.log`.

## Voies possibles
- Configuration : aucun paramètre de ce modèle ne pose de contrainte SQL ; ne satisfait pas D-31.
- Studio : automatisation éventuelle non équivalente à une contrainte SQL ; maintenance en base, voie écartée par D-31.
- Module : un `models.Constraint` et tests ; effort faible, vérification de compatibilité SQL/ORM à chaque migration. Voie retenue.

## Décisions, contradictions et questions
D-31, Luc Roy, `decisions/2026-09-08.md`, confirmée par la demande utilisateur : `days >= 0`, SQL, zéro inclus ; `daily_rate` et `amount_total = days × daily_rate` gardent leur règle. Elle remplace la tolérance des essais relatée au journal du 2026-08-01. Aucune question bloquante ni hypothèse métier ajoutée.

## Spécification
Ajouter un CHECK SQL via `models.Constraint` 19.0 sur `lab.rental.days`. Refuser création et modification négatives, toutes valeurs de `kind`. Aucun changement d'écran, de droits, de tarif ou du compute. Rejet atomique : préserver la location valide et son total après rollback. Aucune reprise de données nécessaire sur la copie vide ; vérifier la contrainte réellement installée lors de l'update, car un succès d'update seul ne le prouve pas.
Hors périmètre : facturation, production, nouvelle règle sur les tarifs, clôture.

## Critères d'acceptation (D-31)
- C1 : création avec days=-1 refusée par la contrainte SQL ; aucune location invalide persistée.
- C2 : modification de 3 jours à -1 refusée ; après rejet et relecture, jours=3, tarif=12.5 et total=37.5 conservés ; une modification valide ultérieure reste possible.
- C3 : création et modification à zéro acceptées ; total=0.
- C4 : total positif et recalcul après modification des jours ou du tarif inchangés ; tarifs zéro et négatifs encore acceptés ; mêmes règles pour location et prêt.
- C5 : installation/tests ciblés et update sur lab_client réussis ; CHECK validé en catalogue PostgreSQL ; données de recette temporaires nettoyées.

## Découpage et QA
Une tâche, QA renforcée (contrainte sur table existante) : relecture/lint, installation et tests ciblés, update et scénarios sur copie. Tests négatifs avec CheckViolation et savepoint, suivant `19.0/odoo/addons/base/tests/test_sql.py:186`.

## Ce que l'utilisateur verra
Un message de rejet si les jours sont négatifs. Aucun écran ni droit modifié.
