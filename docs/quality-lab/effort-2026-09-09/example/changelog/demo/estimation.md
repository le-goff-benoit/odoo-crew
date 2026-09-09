# Estimation du temps des agents

Minutes d’exécution, outils inclus. Aucun barème commercial appliqué.
Valeur centrale = (optimiste + 4 × probable + pessimiste) / 6 ; fourchette de jugement, pas intervalle statistique.

| Lot de travail | Agent | Optimiste | Probable | Pessimiste | Central | Confiance |
|---|---|---:|---:|---:|---:|---|
| RELEASE — Recette et consolidation communes | odoo-tester | 12.00 | 20.00 | 40.00 | 22.00 | faible |
| RELEASE — Recette et consolidation communes | orchestrateur | 5.00 | 9.00 | 18.00 | 9.83 | faible |
| T01 — Référence de livraison | odoo-developer | 10.00 | 18.00 | 32.00 | 19.00 | faible |
| T01 — Référence de livraison | odoo-tester | 5.00 | 9.00 | 18.00 | 9.83 | faible |
| T01 — Référence de livraison | orchestrateur | 2.00 | 4.00 | 8.00 | 4.33 | faible |
| T02 — Filtre de recherche | odoo-developer | 5.00 | 10.00 | 22.00 | 11.17 | faible |
| T02 — Filtre de recherche | odoo-tester | 4.00 | 7.00 | 15.00 | 7.83 | faible |
| T02 — Filtre de recherche | orchestrateur | 2.00 | 3.00 | 6.00 | 3.33 | faible |

## RELEASE / odoo-tester

Base : Jugement initial ; aucun historique comparable mesuré dans ce projet synthétique

- Suite complète unique
- Restauration disponible selon scénario, aucun environnement réel vérifié

## RELEASE / orchestrateur

Base : Jugement initial ; aucun historique comparable mesuré dans ce projet synthétique

- Consolidation et bilan de release une seule fois

## T01 / odoo-developer

Base : Jugement initial ; aucun historique comparable mesuré dans ce projet synthétique

- Analyse reçue, un module Odoo 19
- Champ texte sans reprise ni nouvelle règle de droits
- Inclut implémentation et tests ciblés du développeur
- Réévaluation avant exécution : couvrir aussi le cas de saisie vide, sans nouveau périmètre métier

## T01 / odoo-tester

Base : Jugement initial ; aucun historique comparable mesuré dans ce projet synthétique

- Copie locale disponible selon scénario
- QA ciblée ; recette complète exclue de cette ligne

## T01 / orchestrateur

Base : Jugement initial ; aucun historique comparable mesuré dans ce projet synthétique

- Transmission et réception des preuves de la tâche

## T02 / odoo-developer

Base : Jugement initial ; aucun historique comparable mesuré dans ce projet synthétique

- Cause et domaine déjà identifiés
- Correction limitée et test de régression, une reprise plausible

## T02 / odoo-tester

Base : Jugement initial ; aucun historique comparable mesuré dans ce projet synthétique

- Copie disponible selon scénario
- Recherche simple et combinée ; QA ciblée uniquement

## T02 / orchestrateur

Base : Jugement initial ; aucun historique comparable mesuré dans ce projet synthétique

- Transmission et réception de la tâche
