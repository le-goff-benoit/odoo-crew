# Mesurer le cadrage avant le plan

Référence gelée : Crew `55ca44d`, Tricorder `5175b7e`.
Problème : le premier registre de mesure arrive après l'analyse de `/odoo-plan`.

Critères avant correction : démarrer sur un projet sans changelog ; lire le
temps en cours sans écriture ; rattacher uniquement l'entrée explicitement
choisie à une release ouverte du même projet ; préserver son identifiant, ses
bornes et l'absence de prévision ; refuser le double comptage entre registres ;
exclure les suspensions et ne pas reconstituer un redémarrage.

Contre-cas réservé : deux préparations indépendantes sur le même projet. Créer
une release ne doit pas aspirer la préparation de l'autre demande.

Essais déterministes sur projets temporaires, compteurs et horloges synthétiques.
Aucun appel modèle payant, aucune modification client. La preuve porte sur le
contrat des outils et des écrans, pas sur l'obéissance universelle des modèles.

## Résultat et adoption locale — 11 septembre 2026

Reproduction : 5 erreurs rouges, API de préparation absente sur la référence.
Correction : même moteur de chronomètre, registre projet unique, rattachement
explicite et projection de lecture dans les bilans de release. Les commandes
`prepare-*` sont prescrites dans le rôle canonique de `/odoo-plan` pour Claude
et Codex, sans demander à l'humain de manipuler le registre.

12 tests dédiés verts : sans release, rattachement idempotent, inter-projets,
release close, chevauchements dans les deux sens, 4 démarrages concurrents,
préparation seule à la clôture, bilan périmé, contre-cas des deux demandes,
transition vers une tâche, aperçu sans écriture, veille/reboot et lecteurs CLI
natifs Claude/Codex. Suite Crew : 283 tests verts. Graphe et génération isolée
conformes ; profils locaux régénérés après validation.

Tricorder sépare préparation, tâches et clôture et leurs parts du temps connu.
Les observations natives non bornées de la même session ne s'ajoutent pas à la
préparation ; des fenêtres explicitement disjointes restent admissibles.
Un parcours Electron couvre projet → release → retour hors release ; les
lectures ne modifient ni le registre ni les estimations.

Limites : aucune durée passée reconstituée, aucune campagne payante de conformité
des modèles. L'agent doit utiliser le skill à jour et identifier sa trace native.
Les attentes humaines demandent un arrêt de mesure ; les jetons sont ceux du
dernier arrêt observé. Le registre projet doit accompagner les bilans versionnés.
