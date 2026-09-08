# Prochaine expérience — décisions bloquantes et concision

Statut : proposition issue du pilote, **non exécutée, non adoptée**.
Les rôles actifs n’ont pas été modifiés. Le pilote n’a mesuré ni leur variante
courte ni l’exécution native de `/odoo-new`.

## Observation qui motive l’essai

Sur B03, la grille initiale sait repérer un seuil inventé, une fausse exécution
et une absence de questions. Elle ne pénalise pas assez le fait de retenir une
approbation des devis existants « à défaut de réponse », ni une recommandation
technique prématurée précédée d’une réserve. Il faut d’abord améliorer la mesure,
puis vérifier si une consigne plus courte corrige le comportement.

## Grille v2 à figer avant une nouvelle campagne

- Une décision qualifiée de bloquante reste ouverte dans la spécification, les
  critères et la reprise : aucune option à impact métier n’est appliquée par défaut.
- Sans vérification, couverture standard, voie technique et estimation restent
  conditionnelles. L’absence de preuve ne devient pas une preuve d’absence.
- La recette des droits vérifie les refus côté serveur ; un bouton masqué seul
  ne satisfait pas un critère d’interdiction.
- Un changement de décision conserve sa provenance et son état de réalisation.
- Une passation courte conserve acteurs, règles, exceptions, inconnues et critères
  observables. Le nombre de mots est une mesure auxiliaire, pas un score métier.

Ne pas recalculer les résultats du pilote avec cette grille en les présentant
comme un résultat prévu à l’avance. Conserver les scores v1 et les réserves.

## Variation de consigne à essayer

Texte candidat, à tester séparément avant toute promotion :

> Commence par les décisions établies et les questions qui empêchent réellement
> de développer. Une hypothèse n’autorise pas à trancher une question bloquante :
> maintiens les choix ouverts jusqu’à l’arbitrage client, surtout pour les droits
> et les données existantes. Sans inspection disponible, indique « non vérifié »
> et propose les preuves à chercher ; ne transforme pas cette réserve en verdict
> technique ou en chiffrage ferme. Termine par une passation proportionnée au
> besoin : règle actuelle et provenance, comportement attendu, inconnues,
> critères testables et état réel des travaux. N’ajoute une section que si elle
> apporte une information utile au destinataire.

Ce texte sera comparé à une référence inchangée. Un essai séparé testera son
usage en remplacement de sections prescriptives longues : ajouter une règle et
réduire le volume sont deux interventions différentes, à ne pas confondre.

## Protocole suivant

Pour chaque outil, garder modèle et effort constants entre référence et variante.
Au moins deux répétitions, ordre alterné ; distinguer les variations dues aux
modèles de celles dues aux consignes. Prévoir des cas réservés nouveaux, par
exemple migration d’une règle de livraison plutôt que remise commerciale.

Évaluer d’abord les erreurs critiques, puis l’utilité de la passation et les
pertes de connaissance métier ; relever durée, tokens et taille des consignes.
La comparaison entre outils ne devient causale qu’après contrôle de leurs
réglages et de leur environnement. Ne pas conclure à partir de six réponses.

Pour couvrir le développement, la prochaine étape devra ajouter un module
synthétique exécutable avec tests métier externes au code produit, vrais profils
d’utilisateur et base jetable. Les présents dossiers sans outils ne peuvent pas
servir de preuve à cette dimension.
