# Revue fonctionnelle — frais de préparation D-02

Projet work (Atelier Boréal synthétique), module lab_rental, série 19.0 établie par le manifest.

## 1. Besoin
En tant que gestionnaire des locations, je veux un total stocké intégrant le forfait décidé pour disposer du montant HT correct. La demande et D-02 sont les preuves du besoin ; fréquence et coût non renseignés, sans incidence sur ce calcul borné.

## 2. Verdict standard
**À DÉVELOPPER** sur le modèle existant. `lab_rental/models/business.py` calcule déjà `days * daily_rate` dans `amount_total`, stocké, avec les trois dépendances nécessaires. Le standard 19.0 `~/odoo-sources/19.0-enterprise/sale_renting/models/sale_order_line.py`, `_get_pricelist_price`, calcule des tarifs de location sur des lignes de vente et des règles `product.pricing` ; il ne configure pas ce modèle autonome dépendant seulement de base. L'inventaire réel de lab_client ne trouve ni enregistrement, ni champ manuel, action serveur ou vue de lab.rental : pas de personnalisation à doubler (preuve inventory.log).
Série suivante : sources 19.1 et 19.1-enterprise absentes du laboratoire ; comparaison non vérifiable, aucun alignement futur affirmé.

## 3. Voies possibles
| Voie | Effort / résultat | Migration |
|---|---|---|
| Configuration | Aucun paramètre du modèle ne porte le forfait | Faible mais ne couvre pas le besoin |
| Studio | Dupliquerait le compute Python existant, tests métier Python indisponibles | Personnalisation supplémentaire à maintenir |
| Module — retenu, demandé explicitement | Petite extension du compute, tests et reprise | Faible, conserver le modèle et le champ existants |

## 4. Contradictions et risques
D-01 (7 %) est historique et remplacée par D-02 : aucune ambiguïté résiduelle. Un changement de corps d'un compute stocké ne recalcule pas automatiquement les anciennes lignes à l'update (`odoo/orm/models.py`, `_auto_init`). Une reprise idempotente est nécessaire et sera prouvée sur essais créés avant modification. La copie est synthétique et modifiable selon LAB.md et D-02 ; aucune production concernée.

## 5. Questions bloquantes
Aucune : Q1 seuil inclusif et Q2 exclusion des prêts sont déjà tranchées dans decisions/2026-09-08.md.

## 6. Décisions
D-02 : forfait de 12 EUR HT si location et jours >= 4. Sinon seul le produit jours × tarif. Monnaie unique EUR, aucun arrondi supplémentaire. Jours et tarif positifs ou nuls. Les essais existants sont recalculables. Pas de droits, écran ou facturation à modifier.

## 7. Spécification
- Conserver les champs days, daily_rate, kind et amount_total (Float, compute, store=True).
- Calcul : days × daily_rate + 12 uniquement si kind='rental' et days >= 4.
- Recalcul automatique à chaque modification de chacun des trois champs, y compris en lot ; retrait du forfait quand on repasse sous 4 jours ou en prêt.
- Faire respecter les valeurs positives ou nulles par deux contraintes 19.0, sans modifier les droits.
- Reprise idempotente via migration post de la prochaine version 19.0.1.0.1. Version actuelle 19.0.1.0.0 conservée pendant la release ; incrément à sa clôture. Pendant la QA locale, exécuter explicitement cette même migration après update puisque l'incrément est différé.
- Hors périmètre : factures, taxes, multi-devise, écrans, documents historiques, déploiement.

## 8. Critères d'acceptation
- C1 : location 3 jours à 10 → 30 ; 4 jours → 52 ; 5 jours → 62.
- C2 : prêt 3/4/5 jours à 10 → 30/40/50.
- C3 : durée nulle → 0 ; location 4 jours à tarif nul → 12 ; prêt à tarif nul → 0 ; tarif décimal sans arrondi ajouté.
- C4 : changer jours, tarif ou type actualise la valeur persistée, dans les deux sens et en lot.
- C5 : jours ou tarif négatifs sont refusés en création et modification ; zéro reste accepté.
- C6 : la reprise corrige les anciens totaux sans modifier les entrées, et un second passage ne change rien ; valeurs relues après vidage du cache et dans SQL.
- C7 : aucun fichier de vue, droit ou facturation modifié ; version inchangée ; release ouverte.

## 9. Découpage et QA
Un point, réalisation courte puis QA de tâche **renforcée** : lint ciblé, installation et tests métier sur base QA, update et reprise sur copie avec états avant/après. Pas de recette de clôture. Pas de sous-agent selon LAB.md.

## 10. Ce que l'utilisateur verra
Aucun changement d'écran ; seul le total serveur change selon D-02.
