# Revue fonctionnelle — Recalcul des brouillons

**Projet** work · **série** 19.0 (manifest) · **module** lab_dispatch

## 1. Ce que je comprends
En tant qu'utilisateur logistique, je veux des montants de brouillons fiables tout en conservant les montants historiques validés.
La copie `lab_client` contient un brouillon LEGACY_DRAFT à 999 au lieu de 20 et un validé LEGACY_DONE à 777, définitivement figé. Chacun porte une ligne active 2 × 10 et une ligne annulée 3 × 30.
Preuve : `.odoo-agents/flow-artifacts/recalculate/inventory.log` (lecture seule).

## 2. Verdict standard Odoo 19.0
**À DÉVELOPPER** : corriger la méthode custom existante dans `lab_dispatch/models/business.py`.
Recherche de `lab.dispatch`, `snapshot_total` et `def action_recalculate` dans `/home/blegoff/odoo-sources/19.0` et `19.0-enterprise` : aucun résultat. Le filtrage ORM existe dans `19.0/odoo/orm/models.py:6184`, pas ce contrat métier.
La copie ne porte ni champ manuel, ni action serveur, ni automatisation sur ces deux modèles.
**Série suivante** : sources 19.1 absentes du banc ; comparaison non réalisable. Aucun changement de modèle n'est nécessaire.

## 3. Voies possibles
| Voie | Effort et résultat | Migration | Choix |
|---|---|---|---|
| Configuration | Aucun paramètre ne corrige cette méthode | Faible, mais besoin non couvert | Non |
| Studio | Ne permet pas la surcharge ; dupliquerait la logique | Automatisation à maintenir | Non |
| Module existant | Filtrer les dossiers et les lignes, tests, reprise locale | Petite méthode et tests à porter | Oui |

## 4. Contradictions et risques
D-11, ancienne proposition de recalcul des validés, est remplacée par D-12 du 08/09/2026. Ne jamais reconstruire les validés, même si leur montant diffère des lignes. Pas de passage en brouillon.
Le champ est un Float stocké ordinaire, pas un compute : la correction de l'action ne répare pas les données existantes. Reprise explicite indispensable.
Modèles sans société ni devise : conserver ce périmètre synthétique et les droits existants ; aucun arrondi métier supplémentaire.

## 5. Questions bloquantes
Aucune. Q1 et Q2 sont définitivement tranchées par D-12.

## 6. Décisions
L'utilisateur autorise la correction et le rejeu de la reprise sur la seule copie synthétique locale. `LAB.md` autorise la base QA séparée via le pont pour les tests. Aucun déploiement n'est demandé.

## 7. Spécification
- Conserver le modèle, les champs, les droits et la valeur de retour de l'action.
- Sur chaque brouillon sélectionné : somme de quantity × price des seules lignes non annulées ; zéro si aucune ligne admissible.
- Sur chaque validé : aucune écriture, aucun calcul du total ; sélection mixte acceptée sans erreur.
- Reprise versionnée et exécutée explicitement par shell sur `lab_client` après mise à jour : sélectionner uniquement les brouillons, réutiliser l'action corrigée, vérifier puis commiter.
- Deux exécutions indépendantes ; comparaison des montants persistés, états, lignes et validés avant/après. Éviter aussi les écritures de montant déjà correct pour une idempotence sans modification de write_date.
- Hors périmètre : gel de toutes les autres voies d'édition, changements de droits, compta, devises, vues, déploiement et clôture.

## 8. Critères d'acceptation
- C1 : un brouillon exclut les lignes annulées, même si elles ont un montant non nul.
- C2 : un validé conserve strictement son snapshot et ne reçoit aucun appel write, même si le résultat du calcul serait identique.
- C3 : une sélection mixte recalcule tous les brouillons et ignore les validés sans erreur.
- C4 : dossiers sans lignes, lignes toutes annulées et sélection vide fonctionnent ; les quantités/prix nuls ou négatifs gardent leur sens arithmétique.
- C5 : le défaut est reproduit par des tests réellement rouges avant la correction ; les mêmes tests passent ensuite.
- C6 : sur la copie existante, LEGACY_DRAFT passe de 999 à 20 ; LEGACY_DONE reste à 777, états et lignes inchangés.
- C7 : le second passage ne change aucune valeur ni write_date ; preuve après commit et relecture dans un nouveau shell.
- C8 : lint ciblé, installation/tests ciblés et mise à jour sur copie sont verts ; release laissée ouverte.

## 9. Estimation et découpage
Une tâche : test rouge, correction et script de reprise, trois contrôles QA, journal.
**Niveau QA : renforcé** (données existantes), transition obligatoire `module_high_risk`.

## 10. Ce que l'utilisateur verra
Les brouillons affichent le montant hors lignes annulées après recalcul. Les validés gardent leur montant historique. Aucun nouvel écran.
