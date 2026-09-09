# Revue fonctionnelle — D-22

Projet work · Odoo 19.0 (LAB.md, config et version RPC 19.0+e-20260817) · aucun module custom.

## Compréhension et verdict
En tant que coordinateur, je veux identifier les locations de 7 jours ou plus pour les revoir.
**PARTIEL** : le modèle et les trois champs existent ; seul l'indicateur manque (inventory-before.json).
Le standard permet un champ manuel calculé stocké : sources 19.0 `odoo/addons/base/models/ir_model.py:47` (safe_eval et dépendances), `:566` (compute/depends/store), `:1285` (attributs du champ). Studio crée ses XML-ID avec `web_studio/models/studio_mixin.py:18`.
Série suivante : sources 19.1 indisponibles dans ce laboratoire ; comparaison non effectuée. Ce modèle propre au laboratoire ne justifie pas une extension standard.

## Voies possibles
| Voie | Effort et résultat | Migration |
|---|---|---|
| Paramètre standard | Aucun paramètre portant D-22 sur le modèle manuel | Faible, ne couvre pas le besoin |
| Studio — retenue, explicitement demandée | Un champ calculé, pack JSON | Rejouer pack et scénarios |
| Module custom | Disproportionné et exclu | Maintenance de code à chaque migration |

## Décisions, contradictions et limites
D-22 dans decisions/2026-09-08.md remplace D-21 : 7 inclus, prêts exclus. Aucun champ de durée supplémentaire.
Aucune question bloquante métier. safe_eval suffit ; aucun import, JS, surcharge, automatisation ou test de module.
Le modèle n'a aucune ACL : les scénarios RPC utiliseront une action serveur temporaire avec sudo explicitement réservé à la recette locale, puis la supprimeront. Aucune ACL ni règle ne sera changée ; l'accès métier reste hors périmètre et non validé.

## Spécification
Ajouter uniquement `x_studio_needs_review`, boolean manuel, stocké, readonly, non copié, calculé pour chaque record par `x_studio_days >= 7 and x_studio_kind == 'rental'`.
Dépendances : `x_studio_days,x_studio_kind`. Utiliser `x_name`, `x_studio_days`, `x_studio_kind` existants sans les modifier. Création en contexte studio=True, XML-ID automatique relevé.
Interface : aucune modification. Droits, envois, module et déploiement : exclus.
Données existantes : calcul initial par l'ORM à vérifier sur la copie, conservation des valeurs sources.

## Critères d'acceptation
- C1 : un seul nouveau champ boolean stocké avec les deux dépendances et XML-ID Studio ; champs et XML-ID initiaux conservés.
- C2 : locations à 5 et 6 jours fausses, 7 et 8 vraies ; prêts à 6, 7 et 8 faux ; valeurs absentes et zéro fausses.
- C3 : recalcul dans les deux sens après modification séparée de chaque dépendance et écriture en lot ; relecture serveur et recherche sur l'indicateur stocké.
- C4 : données préexistantes correctement calculées et valeurs sources conservées ; données de recette nettoyées.
- C5 : pack limité au nouveau champ, sans unresolved ; deux applications réelles, sans doublon ni différence ; scénario vert après chacune.
- C6 : aucune vue, ACL, automatisation ou action permanente ajoutée ; release ouverte, QA et journal livrés.

## QA et découpage
Un point Studio. QA de tâche sur copie synthétique avec contrôle des données existantes, scénario rouge avant, vert après, puis deux applications du pack. Pas de restauration fraîche supplémentaire disponible ni de recette de clôture dans cette tâche ; le champ est initialement absent sur la copie fournie. Pas de capture : aucun écran touché.

## Ce que l'utilisateur verra
Rien de visible ; seul un indicateur technique est ajouté.
