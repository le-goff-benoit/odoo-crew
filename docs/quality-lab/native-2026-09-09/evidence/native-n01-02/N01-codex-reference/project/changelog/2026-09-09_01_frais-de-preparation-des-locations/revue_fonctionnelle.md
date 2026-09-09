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

## Point 1 — Révision D-03, 2026-09-09 (en vigueur)

La revue D-02 ci-dessus reste historique. Alice Martin acte D-03 dans `decisions/2026-09-09.md` et la demande reçue : **D-03 remplace D-02 dans cette même release**. Aucun nouvel arbitrage nécessaire.

**Besoin / verdict : À DÉVELOPPER**, delta du compute existant pour obtenir les totaux HT conformes au nouveau forfait. Revue limitée au changement : le choix module reste justifié. Vérification des sources 19.0 : `19.0-enterprise/sale_renting/models/sale_order_line.py:340` (`_get_pricelist_price`, règles `product.pricing`) ne configure pas `lab.rental`, modèle autonome. Inventaire actualisé dans `preuves/d03/inventory.log`. La comparaison 19.1 reste non vérifiable (sources absentes au laboratoire).

**Voies** : configuration sans paramètre utilisable ; Studio doublerait le calcul Python et sa maintenance ; module retenu (petit delta, mêmes champs et migration à maintenir).

**Spécification actuelle** : `amount_total = days * daily_rate + 15` si `kind == 'rental'` et `days >= 5`, sinon `days * daily_rate`. Prêts exclus, EUR HT, aucun arrondi supplémentaire. Dépendances jours/tarif/type, stockage, contraintes positives ou nulles inchangés. Pas de nouvel écran, droit, facture ni déploiement.

**Risque / reprise** : les valeurs D-02 à 4 jours doivent perdre 12 EUR ; celles à 5 jours ou plus gagner 3 EUR. Le compute seul ne reprend pas l'existant (`19.0/odoo/orm/models.py`, `_auto_init`). Conserver la migration non livrée `19.0.1.0.1`, qui appelle le compute courant ; préciser D-03 et prouver son double passage sur copie. Manifest 19.0.1.0.0 maintenu, déclenchement automatique à vérifier après incrément à la clôture.

**Critères D-03 (remplacent C1–C7 D-02 pour le verdict actuel)**
- C1 : locations 3/4/5/6 jours à 10 → 30/40/65/75.
- C2 : prêts 3/4/5/6 jours à 10 → 30/40/50/60.
- C3 : durée nulle → 0 ; location 4 jours gratuite → 0, 5 jours gratuite → 15 ; prêt gratuit → 0 ; 5 × 10.1234 + 15 → 65.617 sans arrondi ajouté.
- C4 : jours 4→5→4, tarif 10→20→0 et type location→prêt→location recalculés et persistés, y compris en lot.
- C5 : jours et tarif négatifs refusés en création/modification ; zéro admis.
- C6 : essais stockés réellement sous D-02 avant modification, update puis reprise D-03 deux fois ; entrées et write_date conservés, SQL/ORM concordants après vidage cache et nouvelle session ; nettoyage des seuls essais créés.
- C7 : historique des preuves D-02 préservé, mémoire courante D-03 sans ambiguïté, release ouverte et manifest inchangé ; aucun écran/droit/facture modifié.

**QA renforcée**, données existantes : nouvelle relecture/lint, install/update et suite TestPreparation, reprise sur lab_client. La première QA reste valide uniquement pour D-02 ; elle ne vaut pas validation de D-03.
**Ce que l'utilisateur verra** : aucun écran modifié ; total serveur conforme à D-03.

### Rectification technique C6 après première QA D-03
La conservation de write_date ajoutée ci-dessus n'est pas une règle métier de D-03. Elle est retirée du critère courant : **C6 exige la conservation de name, kind, days, daily_rate**, des IDs et des totaux idempotents. Les métadonnées d'audit peuvent être actualisées par le recalcul ORM standard (`19.0/odoo/orm/models.py:4536`). Leur évolution est tracée dans les preuves copie. Aucun changement du périmètre métier décidé par Alice Martin. Historique de la QA rouge conservé.
