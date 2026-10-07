# Pilotage des releases — 7 octobre 2026

Référence Crew `d4c5d6d`, Tricorder `c37665d`. Demande : simplifier le pilotage,
fiabiliser prévu/réalisé, conserver les apprentissages et distinguer publication,
recette et déploiement. Les estimations initiales sont dans `execution.json`.
Aucune mesure historique par tâche n'a été inventée après les travaux.

## Réception fonctionnelle

| Axe | Résultat et preuve |
|---|---|
| A01 / A13 | Statut, sept onglets, Kanban par défaut, critères/tests/temps par agent ; questions avec réponses. Tests Tricorder et parcours Electron. |
| A02 | Publication avec réserves indépendante de la QA ; résolution sourcée obligatoire ; cible et tâches liées au déploiement observé. `test_pilotage_contracts`. |
| A03 | Couverture des prévisions avant lancement CLI, session dédiée liée au rôle, collecte native durable, reprise, scellement, sous-totaux connus, suivi Express, synthèse partageable. Tests effort/usage/pilotage. |
| A04 | Réutilisation par impact existante conservée ; correction du blocage des dépendances transitives en renouvellement. Tests `test_odoo_release_plan` et contrôles ciblés existants. |
| A05 | Attendus métier indépendants, populations exactes et observation brute rattachés au contrat. Mutation booléen/nombre refusée, résultat divergent rouge. |
| A06 | Contrat explicite des moyens requis avant recette, preuves série/environnement ; navigateur absent signalé. Consignes onchange et sauvegarde. |
| A07 | Garde de l'artefact exact conservé ; motifs récursifs d'assets corrigés avec oracle glob indépendant. Voir la campagne delivery-glob voisine. |
| A08 | Découvertes acceptées projetées automatiquement, origine et exceptions préservées, altération détectée, briefing inter-releases alimenté. |
| A09 | Collecte/qualification idempotentes existantes conservées ; événements bruts retirés du cockpit. Les problèmes concrets de cette passe sont décrits ci-dessous. |
| A10 | API publique Crew de lecture ; validation partagée dans une requête, jamais entre rafraîchissements. Le test de 41 contributions vérifie une seule validation. |
| A11 | Reprise des mesures et journal scellé ; parcours existants de reconnexion, attente, terminal persistant et confidentialité rejoués. |
| A12 | Comparaison bornée commencée, arrêt sur refus organisationnel Claude. Deux réceptions Codex positives relues indépendamment. Référence des modèles/efforts/délégation conservée. |

## Défauts détectés puis corrigés en relecture indépendante

- Une durée native manquante effaçait les segments connus ; conservation du sous-total.
- Collecteur stoppé pendant un outil long, import concurrent régressif et relance
  d'un binding scellé : sérialisation, garde avant mutation et contre-épreuves.
- Faux vert `false == 0`, réserves perdues sans résolution, projection mémoire
  altérée mais dite fraîche : chacun possède un test de régression.
- Statut ignorait les observations natives ; tests prescrits mal libellés ; total
  partiel masqué ; ancien original d'intention inaccessible : recette corrigée.

## Contrôles

435 tests Crew réussis, un skip : parseur TOML standard indisponible en Python
3.10 (test applicable en 3.11+). Graphe : 59 nœuds, 129 arêtes. Build isolé :
35 fichiers générés et deux blocs d'aiguillage conformes. Tricorder : 97 tests
Python, 62 JavaScript ; 18 parcours du paquet réussis. Deux parcours optionnels
sur projets réels non exécutés dans cette recette synthétique.

`qualification.json` conserve les mesures de la comparaison documentaire.
Deux incidents de préparation (helper de test absent du snapshot puis socket
interdit par le sandbox) ont précédé les appels ; corrigés avant le lancement.
Le troisième appel natif a été refusé par l'organisation Claude. Aucun repli,
aucune relance fournisseur ni modification d'accès. Le cas réservé n'a pas été
exécuté : **aucune amélioration générale de vitesse ou de modèle n'est qualifiée**.

## Limites conservées

Les périodes natives absentes demeurent inconnues. `track` concerne une session
dédiée ; une conversation multi-tâches exige des fenêtres explicites disjointes.
Une mesure scellée n'est plus modifiée automatiquement. Le temps d'agent ne
constitue ni une estimation de charge humaine ni un tarif client. Les anciens
registres sans titre métier, estimation ou preuve ne sont pas réécrits ni inventés.
Les oracles métier doivent être fixés/revus indépendamment ; l'outil prouve leur
comparaison, pas leur pertinence intellectuelle. Les règles de production restent
inchangées et aucun projet client n'a été modifié par cette release d'outillage.
