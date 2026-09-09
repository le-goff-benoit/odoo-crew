# Revue fonctionnelle — frais de préparation D-02

Projet Atelier Boréal (`/work`) · Odoo 19.0 (manifest) · module `lab_rental`.

## 1. Ce que je comprends
En tant que gestionnaire des locations, je veux un total HT stocké conforme à D-02 pour disposer du montant incluant la préparation. Demande exacte : `demande.md` ; décision : `decisions/2026-09-08.md`.

## 2. Verdict standard Odoo 19.0
**À DÉVELOPPER** sur le modèle custom existant. `19.0-enterprise/sale_renting/models/product_pricing.py`, `product.pricing._compute_price`, multiplie un tarif par des périodes ; `sale_order.py` gère des commandes commerciales. Ces mécanismes ne configurent pas `lab.rental`, module dépendant uniquement de `base`, ni son forfait conditionnel D-02.
La copie `lab_client` contient 0 location, 0 champ manuel, 0 vue et 0 action serveur sur ce modèle ; `base.automation` absent. Preuve : `.odoo-agents/flow-artifacts/preparation/inventory.log`.
Série suivante : sources 19.1 enterprise absentes ; comparaison non réalisable, sans incidence sur la cible 19.0.

## 3. Voies possibles
| Voie | Effort et résultat | Migration | Choix |
|---|---|---|---|
| Configuration | Aucun paramètre du module pour ce forfait | Faible mais besoin non couvert | Non |
| Studio | Doublerait un champ Python ; pas de tests Python de la configuration | Personnalisation supplémentaire à maintenir | Non |
| Module | Adapter le compute existant et livrer les tests métier | Faible, tests à rejouer | Oui, demandé explicitement |

## 4. Contradictions et risques
D-01 (7 %) est historique et remplacée par D-02. Un simple changement du compute stocké ne garantit pas la reprise des anciennes valeurs : prévoir un script ORM idempotent et le vérifier sur la copie synthétique.

## 5. Questions bloquantes
Aucune. Q1 : seuil inclusif 4 jours ; Q2 : prêts exclus, décidés par Alice Martin le 08/09 dans D-02. Aucune nouvelle autorisation requise pour les essais locaux (LAB.md).

## 6. Décisions
EUR uniquement, HT, aucun arrondi supplémentaire. Domaine d'entrée convenu : jours et tarif positifs ou nuls ; pas d'ajout de contrainte de saisie dans cette tâche.

## 7. Spécification
Conserver `lab.rental.amount_total`, Float calculé et stocké, dépendant de `days`, `daily_rate`, `kind`.
Total = jours × tarif + 12 si `kind == 'rental'` et jours >= 4 ; sinon jours × tarif. Le prêt conserve son montant de base, sans frais. Aucun nouveau champ, vue, droit, flux de facturation ou dépendance.
Reprise : après mise à jour, script ORM versionné dans la release pour recalculer les essais existants ; deux passages doivent laisser les mêmes montants. La copie étant vide, créer des témoins avant modification du code, puis les supprimer après validation. Toute livraison ultérieure devra rejouer la reprise adaptée à son périmètre ; aucune production concernée ici.

## 8. Critères d'acceptation
- C1 : locations 3/4/5 jours à 10 EUR → 30/52/62 EUR ; forfait unique et fixe.
- C2 : prêts 3/4/5 jours à 10 EUR → 30/40/50 EUR.
- C3 : zéro jour → 0 ; location 4 jours à tarif nul → 12 ; prêt à tarif nul → 0 ; décimales conservées sans arrondi ajouté.
- C4 : création multiple et écritures séparées sur jours, tarif et type recalculent le total, y compris le retrait du forfait en repassant sous le seuil ou en prêt.
- C5 : total réellement persisté après flush et invalidation du cache ; reprise des témoins antérieurs validée deux fois, puis relue dans une nouvelle session.
- C6 : aucune modification d'écran, droits, facturation ni version du manifest pendant cette release ouverte.

## 9. Estimation et découpage
Un point : compute, tests, reprise ORM, QA de tâche et journal. Niveau QA **renforcé** (`module_high_risk`) pour les valeurs stockées existantes ; installation/tests sur base QA et mise à jour/reprise sur copie.

## 10. Ce que l'utilisateur verra
Rien de nouveau dans les écrans. Le total serveur intègre les frais convenus. Release laissée ouverte.
