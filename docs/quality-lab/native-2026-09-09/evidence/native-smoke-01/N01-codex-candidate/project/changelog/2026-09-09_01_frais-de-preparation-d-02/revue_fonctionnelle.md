# Revue fonctionnelle — Frais de préparation D-02

Projet work (Atelier Boréal), module lab_rental, Odoo 19.0 (manifest).

## 1. Besoin
En tant que gestionnaire des locations, je veux un total HT stocké incluant les frais décidés afin de disposer du bon montant sans facturer ni modifier les écrans.
La demande et decisions/2026-09-08.md font foi ; aucun coût ni fréquence d'usage réelle dans ce laboratoire synthétique.

## 2. Verdict standard
**À DÉVELOPPER** : `lab_rental/models/business.py` définit déjà `lab.rental.amount_total`, calculé et stocké, mais ne calcule que jours × tarif.
Le standard 19.0 `sale_renting/models/sale_order_line.py::_get_pricelist_price` (sources enterprise) tarifie des lignes de vente par produit, période et liste de prix. Il ne configure pas la règle D-02 de ce modèle indépendant, qui ne dépend que de base. `addons/sale/models/sale_order.py` fournit un précédent de total calculé stocké.
Inventaire réel : `.odoo-agents/flow-artifacts/preparation-d02/inventory.log` : zéro location, aucun champ manuel ni action serveur sur ce modèle, Studio non installé.
Série suivante : sources 19.1 absentes du laboratoire ; comparaison non réalisée, à revoir lors d'une migration.

## 3. Voies possibles
| Voie | Effort et résultat | Migration |
|---|---|---|
| Configuration | Aucun paramètre disponible pour ce calcul custom | Faible, mais ne couvre pas le besoin |
| Studio | Dupliquerait la logique Python existante ; tests Python métier indisponibles | Maintenance de l'automatisation en plus du module |
| Module (retenu) | Petite extension du calcul existant, tests ORM, reprise explicite | Rejouer les tests et réévaluer la reprise à la clôture |

## 4. Contradictions et risques
D-01 (7 %) est historique, remplacée par D-02. Un changement de compute stocké ne remet pas seul à niveau les totaux déjà persistés : prévoir une reprise ORM idempotente, validée sur copie avec témoins créés avant modification. Tous les essais sont modifiables selon LAB.md. Aucun document historique concerné.

## 5. Questions bloquantes
Aucune : Q1 = 4 inclus ; Q2 = prêts exclus, décision Alice Martin du 08/09/2026.

## 6. Décisions
EUR uniquement, HT, sans arrondi supplémentaire ; jours et tarif positifs ou nuls. La release reste ouverte et le manifest reste à sa version actuelle jusqu'à clôture.

## 7. Spécification
- Conserver les champs et dépendances `days`, `daily_rate`, `kind` du total stocké.
- Total = days × daily_rate + 12 si kind = rental et days >= 4 ; sinon days × daily_rate.
- Garantir days >= 0 et daily_rate >= 0 par contraintes de modèle ; zéro accepté.
- Recalcul à la création et après modification de chacune des trois dépendances, y compris les bascules dans les deux sens et les opérations par lots.
- Reprise explicite ORM versionnée dans la release, rejouable sans effet cumulatif ; pas de déclenchement implicite à chaque démarrage. À intégrer au protocole de livraison lors de la clôture.
- Interface, droits, dépendances du manifest et facturation inchangés ; pas de multi-devise, taxe, ni pourcentage.

## 8. Critères d'acceptation
- C1 : location 3 × 10 = 30, 4 × 10 = 52, 5 × 10 = 62.
- C2 : prêt 3/4/5 × 10 = 30/40/50, sans frais.
- C3 : zéro jour = 0 ; location 4 jours à tarif zéro = 12 ; prêt à tarif zéro = 0 ; 4 × 0,3333 + 12 = 13,3332 sans arrondi ajouté.
- C4 : écritures individuelles de jours, tarif et type recalculent les totaux persistés, sans cumul des frais ; lot mixte couvert.
- C5 : total réellement stocké et relu après flush/invalidation ; aucune modification d'écran, de droits ou de facturation.
- C6 : nombres négatifs refusés, création et modification ; valeurs nulles acceptées.
- C7 : installation/tests sur QA et update sur copie réussis ; reprise des témoins préexistants et seconde exécution identiques, entrées source préservées.

## 9. Découpage et QA
Un point : modèle et tests, lint, installation/tests ciblés, update et reprise sur copie synthétique, journal.
**QA renforcée**, transition `module_high_risk` car changement d'un calcul déjà stocké ; trois voies de QA exécutées séquentiellement par Codex conformément à LAB.md.

## 10. Ce que l'utilisateur verra
Rien de nouveau à l'écran. La valeur serveur du total inclut les frais D-02.
