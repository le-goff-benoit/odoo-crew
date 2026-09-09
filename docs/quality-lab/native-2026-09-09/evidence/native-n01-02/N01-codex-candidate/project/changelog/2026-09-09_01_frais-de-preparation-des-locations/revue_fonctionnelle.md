> **Règle actuelle : D-03, point 2 en fin de document.** Le cadrage D-02 ci-dessous est historique et conservé ; ses critères chiffrés sont remplacés par D3-C1 à D3-C6.

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


## Point 2 — D-03 remplace D-02 (09.09.2026)

**Décision actuelle** : Alice Martin, demande ci-dessus et `decisions/2026-09-09.md`. Les sections D-02 précédentes restent historiques ; leurs seuil, montant et critères chiffrés sont remplacés par ceux-ci.
**Besoin** : le gestionnaire doit retrouver le total HT selon D-03 dans les nouvelles locations et les valeurs déjà stockées, dès cette release.
**Verdict : À DÉVELOPPER**, delta du compute custom existant. La lecture renouvelée de `/home/blegoff/odoo-sources/19.0-enterprise/sale_renting/models/product_pricing.py` (`_compute_price`) confirme une tarification par périodes sur `product.pricing`, sans paramétrage du forfait de `lab.rental`. Inventaire renouvelé : copie vide, aucun champ manuel, action serveur ou vue sur ce modèle ; base.automation absent (`preparation-d03/inventory.log`). Sources enterprise 19.1 absentes, comparaison suivante toujours non réalisée.
**Voies** : configuration sans paramètre disponible ; Studio doublerait le compute Python avec une maintenance supplémentaire ; module recommandé, modification minimale et tests réutilisables à la migration.
**Contradiction résolue** : D-03 supplante D-02, qui avait déjà supplanté D-01. La QA D-02 ne valide pas D-03. Aucune question bloquante ; validation locale autorisée par LAB.md et D-03.
**Spécification** : `amount_total = days * daily_rate + 15` uniquement pour `kind='rental'` et `days >= 5`, sinon montant de base. EUR HT, domaine positif ou nul, décimales sans arrondi ajouté. Champ stocké et dépendances `days`, `daily_rate`, `kind` conservés.
**Reprise** : créer des témoins synthétiques avant modification sous D-02, puis update de lab_client et reprise ORM explicite. Prouver les valeurs persistées en nouvelles sessions et l'idempotence ; nettoyer seulement ces témoins après succès. Garder l'ancien script dans les preuves historiques, adapter le script actif à D-03.
**Interface et sécurité** : aucun changement d'écran, droit ou facturation ; version 19.0.1.0.0 jusqu'à clôture.
**Niveau QA renforcé** : données existantes, trois voies du graphe. Suite du module comme point de contrôle puisque le même compute est repris.

### Critères D-03 en vigueur
- D3-C1 : locations 3/4/5/6/20 jours à 10 EUR → 30/40/65/75/215 ; forfait fixe unique.
- D3-C2 : prêts 3/4/5/6/20 jours à 10 EUR → 30/40/50/60/200.
- D3-C3 : zéro jour → 0 ; tarif nul à 4 jours → 0, à 5 jours → 15 pour une location et 0 pour un prêt ; 5 jours à 1.2345 → 21.1725 (location), 6.1725 (prêt).
- D3-C4 : créations multiples et écritures isolées de jours, tarif et type recalculent correctement ; passages 4→5 et 5→4 retirent/ajoutent le forfait selon D-03.
- D3-C5 : valeurs réellement stockées après flush/invalidation ; témoins D-02 repris après update, relecture dans de nouvelles sessions et second passage identique, nettoyage prouvé.
- D3-C6 : écran, droits, facturation, dépendances et version inchangés ; historique D-02 conservé et mémoire active D-03 cohérente.

**Ce que l'utilisateur verra** : les totaux serveur changent selon D-03 ; aucun nouvel écran. Clôture et déploiement hors de cette intervention.
