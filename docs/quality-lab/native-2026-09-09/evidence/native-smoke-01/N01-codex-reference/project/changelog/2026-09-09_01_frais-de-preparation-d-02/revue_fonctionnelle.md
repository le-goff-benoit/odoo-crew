# Revue fonctionnelle — Frais de préparation D-02

**Projet** work · **série** 19.0 (manifest) · **module** lab_rental

## 1. Ce que je comprends
En tant que gestionnaire de locations, je veux un total HT stocké conforme à D-02 pour disposer du montant correct sans facturer ni modifier les écrans.
Le calcul actuel se limite à jours × tarif ; la décision du 08/09 fixe le forfait manquant.

## 2. Verdict standard Odoo 19.0
**À DÉVELOPPER** sur le modèle custom `lab.rental`, dépendant uniquement de `base`.
`~/odoo-sources/19.0-enterprise/sale_renting/models/product_pricing.py` calcule des tarifs par périodes pour les produits de vente ; il ne configure pas le forfait D-02 de ce modèle indépendant.
`~/odoo-sources/19.0/addons/sale/models/sale_order.py` fournit le précédent de calcul stocké avec dépendances et affectation par enregistrement.
Inventaire réel : aucun champ manuel, aucune action serveur ou automatisation, zéro location sur lab_client (preuve : `.odoo-agents/flow-artifacts/preparation-d02/inventory.log`). La copie est installée mais vide pour ce modèle ; un jeu synthétique sera préparé avant mise à jour.
**Série suivante** : sources 19.1 enterprise indisponibles ; comparaison non réalisée. Aucun changement de modèle nécessaire.

## 3. Voies possibles
| Voie | Effort et résultat | Migration | Choix |
|---|---|---|---|
| Configuration | Aucun paramètre sur ce modèle ne porte D-02 | Faible, mais besoin non couvert | Non |
| Studio | Automatisation redondante avec le compute Python existant | Deux logiques à maintenir | Non |
| Module | Extension courte du compute et tests métier | Rejouer les tests et reprendre le stocké | Oui, demande explicite |

## 4. Contradictions et risques
D-01 (7 %) est remplacée par D-02 ; aucun pourcentage ne subsiste.
Un `-u` seul ne garantit pas la reprise d'un compute stocké dont seule la formule change : livrer un script ORM idempotent, réservé au bac synthétique, et prouver sa double exécution après update.

## 5. Questions bloquantes
Aucune. Q1 et Q2 sont déjà tranchées par Alice Martin dans `decisions/2026-09-08.md`, explicitement désigné par l'utilisateur.

## 6. Décisions
Q1 : seuil inclusif de 4 jours. Q2 : prêts exclus, même à 4 jours.
12 EUR fixes, HT, monnaie unique, aucun arrondi supplémentaire. Jours et tarif positifs ou nuls constituent le domaine métier donné ; aucune nouvelle contrainte demandée.
Tous les enregistrements du bac sont des essais modifiables, autorisés par LAB.md et D-02.

## 7. Spécification
- Conserver `amount_total`, Float calculé et stocké, et les dépendances `days`, `daily_rate`, `kind`.
- Total = jours × tarif + 12 si `kind == 'rental'` et `days >= 4`, sinon jours × tarif.
- Réaffecter le total pour chaque enregistrement, y compris lors du retrait des frais.
- Reprise : script versionné de recalcul ORM des essais existants ; valider valeurs stockées et idempotence.
- Interface et sécurité inchangées ; pas de facturation, comptabilité ou document historique.
- Version manifest conservée pendant la release ouverte ; incrément à la clôture.

## 8. Critères d'acceptation
- C1 : locations 3/4/5 jours à 10 EUR → 30/52/62 EUR.
- C2 : prêts 3/4/5 jours à 10 EUR → 30/40/50 EUR.
- C3 : 0 jour → 0 ; location 4 jours à tarif nul → 12 ; prêt équivalent → 0 ; décimales sans arrondi supplémentaire.
- C4 : changements indépendants de jours, tarif et type recalculent et retirent/restaurent les frais ; lot mixte correctement traité.
- C5 : résultats persistants après flush et invalidation du cache, recherche sur le total possible.
- C6 : update sur module déjà installé, reprise des valeurs antérieures et deuxième reprise identique, sans altérer les entrées.
- C7 : aucun changement d'écran, de droits ou de facturation ; release ouverte.

## 9. Estimation et découpage
Un point : compute et tests, puis QA et journal.
**Niveau QA : renforcé** pour la reprise des données stockées, même synthétiques. Installation/tests ciblés sur base séparée et update/reprise sur lab_client. Pas de recette complète de clôture.

## 10. Ce que l'utilisateur verra
Rien de visible : aucun écran modifié.
