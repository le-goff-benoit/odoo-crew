# Revue fonctionnelle — Recalcul des brouillons D-12

Projet work · série 19.0 (manifest) · module lab_dispatch.

## Besoin et verdict
En tant que gestionnaire, je veux un montant exact sur les brouillons sans altérer les montants validés.
**À DÉVELOPPER** : défaut de la méthode custom `lab_dispatch/models/business.py:13` ; aucun `lab.dispatch` ni `snapshot_total` trouvé dans les sources 19.0 community/enterprise. Le standard `19.0/addons/sale/models/sale_order.py:694` fournit le précédent de filtrage des brouillons, pas cette action métier. Sources 19.1 absentes du banc : comparaison suivante non vérifiable.
Inventaire réel : `.odoo-agents/flow-artifacts/dispatch-d12/inventory.log`. Deux dossiers : LEGACY_DRAFT (999, attendu 20), LEGACY_DONE (777, à conserver). Chacun porte 20 actifs et 90 annulés. Aucun champ manuel ni action serveur sur ces modèles.

## Voies possibles
| Voie | Effort et résultat | Coût migration |
|---|---|---|
| Configuration | Aucun paramètre ne corrige la méthode Python | Nul, mais besoin non couvert |
| Studio | Ne permet pas de surcharger cette méthode ; doublonnerait l'action | Automatisation à maintenir, défaut original persistant |
| Module (retenu) | Petit correctif de l'action existante, tests et reprise explicite | Tests à rejouer à chaque migration |

## Décisions et risques
D-12 du 08/09 remplace D-11 et répond définitivement à Q1/Q2. Aucune question bloquante. Autorisation explicite reçue : corriger et rejouer la reprise sur la copie synthétique locale uniquement ; ni production ni autre copie métier.
Risque sensible : valeurs déjà stockées. Une mise à jour du module seule ne les répare pas. QA renforcée obligatoire avec reprise et relecture persistée sur lab_client.

## Spécification
- Modèles, champs, états et droits inchangés. Pas de compute automatique du snapshot.
- `action_recalculate` ne traite que `state == 'draft'`, somme `quantity * price` des lignes non annulées, renvoie True.
- Les validés sont ignorés avant accès aux lignes et avant toute écriture, même en sélection mixte. Ils ne redeviennent jamais brouillons.
- Une somme vide vaut zéro. Aucune écriture si le montant est déjà exact, afin que le rejeu soit également sans modification de write_date.
- Reprise versionnée dans la release, exécutable au shell du pont, bornée à lab_client et aux brouillons ; appeler la méthode corrigée. Contrôler avant/après, validés et lignes inchangés, committer puis rejouer dans une seconde transaction.
- Hors périmètre : changement des droits, nouvelle interface, gel de toute modification manuelle des validés, déploiement, clôture.

## Critères d'acceptation
- C1 : brouillon avec 20 actifs + 90 annulés → 20, persisté.
- C2 : validé à 777 → 777 ; aucune écriture ni lecture des lignes par l'action.
- C3 : sélection mixte → brouillon corrigé et validé intact, sans erreur.
- C4 : sans ligne, ou uniquement des lignes annulées → 0 ; sélection vide acceptée.
- C5 : reprise des données existantes : 1 brouillon 999 → 20 ; validé 777 conservé ; lignes et états inchangés.
- C6 : seconde exécution persistée : zéro dossier modifié, y compris write_date.

## Découpage et ce que l'utilisateur verra
Test rouge sur le code initial → correction et script de reprise → lint/install/update/tests ciblés → mise à niveau et deux reprises locales → journal. QA sensible.
Même action ; montant du brouillon exact, validés ignorés. Aucun nouvel écran. Release laissée ouverte ; documentation et recette complète à la clôture.
