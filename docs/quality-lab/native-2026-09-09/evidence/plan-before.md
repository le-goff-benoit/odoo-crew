# Validation indépendante du plan et du garde

Date : 2026-09-09. Aucun dépôt, profil actif ni client modifié. Projet intégralement synthétique sous ce répertoire. Scripts réellement exécutés depuis `/home/blegoff/odoo-agents-native-lab/scripts`. Aucun banc ou rapport d'expérience lu.

Les états `complete` des flows sont des doublures écrites explicitement dans le projet synthétique ; cette validation porte sur les frontières plan/réceptions/clôture, pas sur l'exécution Odoo ni la validité des étapes du graphe. Les commandes de preuves sont de vrais sous-processus Python et les empreintes/logs sont réellement vérifiés, mais les commandes ne sont pas des tests Odoo. Ne pas publier ces artefacts comme une recette client.

## Résultats reproduits avant corrections de l'orchestrateur

1. **P1 — réactivation automatique du dépendant après décision changée.** T01 et T02 validées ; T03 dépend des deux et est validée. Modifier `demande-T01.md` rend T01/T03 stale. Rouvrir, démarrer et recevoir T01 uniquement rend T03 validated sans nouvelle exécution/réception. La réception enfant ne capture pas la version de ses dépendances. Preuves : `transcript.txt`, `resurrected-plan.json`, copie `before-decision/`.
2. **P1 — préparation de version bloque la clôture ordinaire.** `odoo_release_guard.py prepare ... --module module_1 --module module_2 --module module_3` après validation des tâches invalide les trois preuves par changement du manifest. Une preuve fraîche finale ne suffit pas à seal, et `finish` sur le flow déjà terminé refuse : « le graphe doit être terminé avant la réception ». Seul reopen/start de chaque tâche est exposé, ce qui reprend inutilement le graphe. Preuve : `transcript.txt`. La répétition de prepare est bien idempotente.
3. **P1 — choix Studio dans controls contourne les exigences module.** Dans un plan de trois tâches `route=module`, une preuve générique sans module est correctement refusée si `controls.route=module`. Changer ce seul champ en `studio` autorise seal/check/close, sans aucun test Odoo. Le garde impose le risque du plan mais pas sa voie. Preuve : `closure-transcript.txt`, `closure_probe.py`.
4. **P1 — retirer le plan supprime ses contraintes après sceau.** Une décision modifiée rend check rouge (`plan non réceptionné`). Renommer `plan.json` en `plan-removed.json` fait réussir check avec le même sceau. L'existence et l'identité du plan ne sont pas scellées. Preuve : `closure-transcript.txt`.
5. **P2 — sceau transférable à une autre release du même projet.** Copier les sept documents exigés et closure.json de R01 vers R02 fait réussir check R02 sans seal R02. Le sceau contient l'identité projet, pas celle de la release. Preuve : `closure-transcript.txt`, `project/changelog/R02`.

## Comportements corrects observés

- T01/T02 prêtes simultanément et démarrables sur leurs périmètres distincts ; T03 bloquée tant que les deux dépendances ne sont pas validées.
- Suppression d'un flow actif : statut interrupted ; start refuse ; reopen exige une raison et permet la reprise explicite.
- Changement de demande : périme sa réception, conserve initialement la tâche indépendante T02 valide et périme temporairement T03.
- Version prepare idempotente, preuve finale effectivement requise sur code modifié.
- Réception absente ou preuve module manquante bloquent le garde avec un message explicite.
- Clôture sans DOCX/PDF possible et retrait du marqueur README compatible avec check. Ce résultat utilise le cas négatif de voie Studio, ce n'est pas une preuve positive de recette Odoo.
- Copie du projet à un nouveau chemin : preuves d'un autre projet explicitement stale. Aucun faux vert ; la génération actuelle emploie des chemins absolus, donc cette validation ne démontre pas la reprise portable annoncée sur preuve nouvelle.

## Reproduction

`probe.py` construit le scénario, appelle plan/evidence/guard et consigne commandes/sorties dans transcript.txt. L'ajout concurrent de controls.json pendant ce premier passage a arrêté sa fin sur absence de closure.json ; ses étapes antérieures sont toutes conservées. `closure_probe.py` poursuit depuis cet état avec le contrat controls courant et conserve closure-transcript.txt. Les scripts de scénario ne sont pas idempotents : utiliser un nouveau répertoire pour un nouveau passage, ou reprendre les commandes individuelles consignées.

Limites : aucun navigateur, serveur/base Odoo, test module réel, environnement distant, réseau ou concurrence multiprocessus éprouvés ; aucune conclusion sur leur comportement.
