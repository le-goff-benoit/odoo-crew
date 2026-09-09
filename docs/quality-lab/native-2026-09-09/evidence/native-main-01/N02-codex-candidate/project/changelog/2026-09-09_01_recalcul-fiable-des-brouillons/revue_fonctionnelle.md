# Revue fonctionnelle — D-12, recalcul et reprise des brouillons

**Projet** work · **Série** 19.0 (manifest) · **Module** lab_dispatch

## Besoin et preuves
En tant que gestionnaire, je veux recalculer les demandes en cours hors lignes annulées tout en conservant les montants historiques des dossiers validés.
La copie synthétique lab_client contient 2 dossiers et 4 lignes : LEGACY_DRAFT (id 1) porte 999 au lieu de 20 ; LEGACY_DONE (id 2) porte un instantané de 777 à préserver même si ses lignes produisent 20. Inventaire initial : `.odoo-agents/flow-artifacts/dispatch-d12/inventory.log` (aucun champ manuel ni action serveur sur lab.dispatch).

## Verdict standard et voies possibles
**À DÉVELOPPER : correctif du custom existant.** La recherche de lab.dispatch / snapshot_total dans `/home/blegoff/odoo-sources/19.0/addons` ne donne aucun résultat. La méthode propre au projet est dans `lab_dispatch/models/business.py`. Le filtrage des brouillons suit le précédent `/home/blegoff/odoo-sources/19.0/addons/sale/models/sale_order.py:694`.
Série suivante : sources 19.1 absentes du laboratoire ; comparaison non exécutée. Aucun modèle standard n'est remplacé par ce correctif local.
- Configuration : aucun paramètre pour corriger cette méthode Python ; ne résout pas le défaut.
- Studio : pas de surcharge de méthode ; une automatisation doublerait la logique et ajouterait une maintenance à la migration.
- Module : modification courte de la méthode existante, tests ORM et script de reprise local explicite ; petit coût de maintenance à la migration. Voie retenue, conformément à la demande.

## Décisions, contradictions et périmètre
D-12, `decisions/2026-09-08.md`, remplace D-11 du journal : validés définitivement figés ; annulées exclues. Aucune question bloquante ni hypothèse métier supplémentaire.
L'autorisation utilisateur couvre correction, update et reprise rejouée sur la copie locale synthétique uniquement ; LAB.md autorise la base QA séparée via le pont. Aucun déploiement.
Pas de changement de modèles, droits, sociétés, devises, vues ou états. Pas de conversion de validé en brouillon. Pas de recalcul automatique à l'update : reprise versionnée explicitement exécutée sur lab_client.

## Spécification
`action_recalculate` itère uniquement sur les dossiers draft et additionne quantity × price des seules lignes cancelled=False. Sans ligne active, résultat zéro. Les validés ne sont ni recalculés ni écrits. Une sélection mixte réussit et traite seulement les brouillons. Le retour True est conservé.
La reprise sélectionne les seuls brouillons existants et appelle cette méthode, avec garde stricte de base lab_client. Les données avant/après et les valeurs attendues sont contrôlées avant commit ; un second passage ne change aucun montant, état ou ligne. Éviter aussi une réécriture des totaux déjà corrects.

## Critères d'acceptation
- C1 : brouillon avec lignes actives et annulées : somme des seules actives.
- C2 : dossier validé : snapshot_total et write_date inchangés ; aucun appel write sur ce dossier.
- C3 : sélection mixte : succès, brouillons corrigés, validés intacts.
- C4 : brouillon vide ou entièrement annulé : zéro ; recordset vide : succès.
- C5 : reprise persistée du brouillon existant 999 → 20 ; validé 777 conservé ; états et lignes identiques.
- C6 : reprise exécutée deux fois dans des sessions distinctes : aucun changement au second passage, y compris write_date.
- C7 : droits inchangés, comportement également testé comme utilisateur interne non administrateur.

## Découpage et QA
Test rouge exécuté avant correction ; correction et script de reprise ; lint des fichiers touchés ; installation/tests ciblés sur QA ; update et reprise avec relecture sur lab_client ; jointure QA sensible et journal. **Niveau renforcé : module_high_risk**, car données existantes. Release laissée ouverte et version du manifest conservée jusqu'à clôture.

## Ce que l'utilisateur verra
Les montants recalculés des brouillons excluent les lignes annulées ; la sélection mixte conserve les montants validés. Aucun nouvel écran.
