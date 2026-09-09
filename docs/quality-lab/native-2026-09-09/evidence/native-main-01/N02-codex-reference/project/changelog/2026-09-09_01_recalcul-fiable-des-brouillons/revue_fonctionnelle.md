# Revue fonctionnelle — Recalcul des brouillons (point 1)

Projet work · Odoo 19.0 (manifest) · module lab_dispatch.

## Besoin et preuve
En tant qu'utilisateur interne, je veux des montants de brouillons exacts sans altérer les montants validés.
La copie synthétique lab_client contient deux dossiers : LEGACY_DRAFT (999, attendu 20) et LEGACY_DONE (777, à conserver). Chacun possède une ligne active de 20 et une ligne annulée de 90. Inventaire : `.odoo-agents/flow-artifacts/recalculate/inventory.log` ; aucun champ Studio ni action serveur sur ces modèles.

## Verdict standard et voies
**À DÉVELOPPER** : méthode et modèle propres à `lab_dispatch/models/business.py`. Recherche de lab.dispatch, snapshot_total et action_recalculate sans résultat dans les sources 19.0 communautaires et enterprise. Le filtrage de brouillons a un précédent dans `/home/blegoff/odoo-sources/19.0/addons/sale/models/sale_order.py:694`.
Série suivante : sources 19.1 absentes du laboratoire, comparaison non exécutée.

| Voie | Effort / résultat | Migration |
|---|---|---|
| Configuration | Aucun paramètre ne corrige cette méthode custom | Sans objet |
| Studio | Ne permet pas la surcharge ; doublonnerait la logique existante | Automatisation supplémentaire à maintenir |
| Module (retenu) | Correction courte, tests et script local de reprise explicite | Maintenir la méthode et ses tests |

## Décisions, contradictions et risques
D-12 du 08/09 remplace D-11 et toute suggestion ancienne de reconstruire les validés. Q1 et Q2 sont résolues : aucune question bloquante, aucune hypothèse métier nouvelle.
Reprise de données existantes : voie **module_high_risk**, QA renforcée sur copie obligatoire. Autorisation utilisateur déjà donnée pour corriger et rejouer sur lab_client uniquement ; aucune porte de production applicable.
Le modèle n'a pas de société ni devise. Aucun changement de droits, de schéma ou de flux comptable.

## Spécification
- L'action conserve son retour True ; elle traite uniquement state=draft, y compris en sélection mixte ou vide.
- Pour chaque brouillon, snapshot_total = somme(quantity × price) des lignes cancelled=False ; zéro si aucune ligne active.
- Les validés sont ignorés sans erreur : aucune recomputation ni écriture, même si leur montant diffère des lignes.
- Reprise ORM explicite versionnée dans la release, limitée par garde de base lab_client, sur les brouillons existants. Deux exécutions et relecture indépendante après commit prouvent l'idempotence.
- Pas d'exécution automatique à l'installation : l'autorisation est locale uniquement. Version inchangée jusqu'à clôture.

## Critères d'acceptation
1. Brouillon avec lignes actives et annulées : total actif seul.
2. Validé : total et write_date inchangés ; aucun appel write, même si le total égale déjà la somme.
3. Sélection mixte : brouillons recalculés, validés ignorés, retour True sans erreur.
4. Brouillon vide ou entièrement annulé : zéro ; sélection vide sans erreur.
5. Reprise réelle : LEGACY_DRAFT 999 → 20, LEGACY_DONE 777 → 777 ; lignes et états inchangés.
6. Deuxième passage : mêmes valeurs et aucune écriture ; relecture dans un nouveau shell après commit.

## Découpage et effet utilisateur
Test rouge → correction et lint → tests verts et update → reprise locale deux fois → QA sensible et journal.
Ce que l'utilisateur verra : montant corrigé sur les brouillons ; les validés gardent leur montant. Aucune vue modifiée. Release à laisser ouverte, documentation et recette complète à la clôture.
