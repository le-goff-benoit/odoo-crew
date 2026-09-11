# Temps partiels et chronomètres de clôture

Référence Crew : `782f50a420b7301cd8646a295b0c01aabacf502e`, avec l'intégration
email locale déjà en cours. Référence Tricorder : `bf5393abc55abdf8c6e8d1a3023a56a2fca7fbe6`,
avec les modifications locales 0.2.2. Aucun changement client dans cet essai.

## Contrat figé

- Un rôle absent ne masque pas les durées des autres rôles ; le sous-total reste partiel.
- Une tâche sans relevé ne vaut pas zéro ; un zéro explicitement mesuré reste zéro.
- Pas d'addition des temps natifs aux mêmes périodes enregistrées, ni de variance partielle.
- Un nouveau sceau refuse un chronomètre actif, mais accepte l'absence historique de mesures.
- Une période perdue se déclare interrompue avec raison : aucun calcul de durée jusqu'à la découverte.
- Les bilans et sceaux historiques restent lisibles ; aucune migration automatique de données client.

## Reproduction et contre-épreuves

Tricorder : quatre nouveaux cas rouges avant correction (rôle manquant, reprise
incomplète avec observation native, total avec tâche absente, observation native
incomplète). Les six contrôles précédents restent verts. Contre-épreuve : zéro
mesuré distinct de l'absence, contrôlée sans ajustement des données.

Crew : quatre nouveaux cas initialement rouges ou en erreur : contrôle de clôture,
interruption, motif obligatoire, suivi absent/partiel. Après correction, ajout d'un
parcours CLI avec code d'échec avant résolution puis réussite sans durée inventée.

Tests déterministes uniquement : aucun appel payant ni essai comportemental LLM.
L'effet sur la discipline future des agents n'est donc pas mesuré. Le garde rend
le refus mécanique à l'appel de `seal` ; la complétude sémantique des rôles reste
une responsabilité de l'orchestrateur. Le contrôle nouveau ne s'applique pas
rétroactivement à `check` sur un ancien sceau.

## Adoption

Changements ciblés dans `odoo_effort.py`, `odoo_release_guard.py`, les rôles
`orchestration.md` et `release-close.md`, et `docs/EFFORT.md`. La méthode
skill-creator a conduit à préciser les transitions de rôles et la borne finale,
sans imposer une nouvelle session de terminal par tâche. Génération Claude/Codex
isolée puis installation locale ; publication distincte.

Les captures réelles restent privées dans les résultats Tricorder. La QA
applicative et celle du paquet sont détaillées dans son `QA.md`.

Validation : 286 tests Crew, dont 33 tests d'effort ; graphe inchangé (59 nœuds,
129 arêtes), build isolé puis actif et 30 sorties + aiguillage conformes.
Tricorder : 52 Python + 11 JavaScript et 6 parcours Electron, rejoués sur paquet
Ubuntu 0.2.3. Aucune installation de l'app ni publication GitHub. La contre-épreuve
de sceau historique laisse `check` réussir et refuse un nouveau `seal` sur le
même registre contenant un chronomètre ouvert.
