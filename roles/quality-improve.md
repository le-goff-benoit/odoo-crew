# Améliorer les agents Odoo à partir d'essais

Cette commande porte sur le dispositif partagé, hors projet client. Le résultat
attendu est une correction **adoptée dans les profils** après validation, ou une
explication prouvée de son rejet ; un rapport seul ne clôt pas une amélioration
réalisable. Pour une remarque propre à un client, utiliser `/odoo-feedback`.

1. Lire `docs/IMPROVEMENTS.md` et `docs/quality-lab/OPERATIONS.md`. Choisir le défaut
   ou la proposition, le comportement attendu et la dimension à mesurer. Figer
   la révision de référence, les cas, grilles, modèles/efforts, limites de durée
   et nombre d'exécutions. Conserver un cas inédit pour la contre-épreuve.
2. Reproduire sur dossiers synthétiques, outils isolés et copies jetables.
   Les commandes du banc distinguent exécution et qualité. Le mode dossier sans
   outils ne prouve pas une chaîne native ; le mode natif du laboratoire adapte
   le transport Docker et n'évalue pas la délégation. Consigner ces limites.
3. Contrôler le correcteur : références correctes acceptées, défauts injectés
   détectés, grilles indépendantes des réponses. Relire les désaccords critiques.
   Un oracle défectueux se corrige séparément, puis tous les candidats concernés
   se rejouent sur le même oracle, sans retoucher leurs réponses ou leur code.
4. Modifier la source canonique `roles/*.md`, les outils ou une référence selon
   la cause observée. Pour un skill, suivre `skill-creator` : précision utile,
   pas d'accumulation de règles génériques. Ne jamais éditer les profils générés.
5. Rejouer le défaut et la contre-épreuve, à réglages constants, puis les contrôles
   de non-régression pertinents. Un échec critique ne se compense pas par la vitesse.
   Un incident du banc ou fournisseur reste séparé d'un échec métier. Arrêter une
   variante après deux corrections sans progrès, conserver la référence et la cause.
6. Statuer par changement : adopté, expérimental ou rejeté, avec preuves avant/après,
   risques résiduels et dimensions non mesurées. Actualiser le suivi des propositions
   et le README pour le fonctionnement réellement livré, sans classement global
   des modèles sur quelques essais.
7. Valider graphe, tests, build isolé et parité. Installer par `build.sh`, intégrer
   et publier selon l'autorisation de la session, vérifier la CI et mettre à jour
   la mémoire du dispositif. Les nouvelles instructions deviennent les profils
   actifs seulement à cette étape. Conserver la référence Git pour revenir en arrière.

Les campagnes LLM sont explicites : pas de lancement caché à chaque CI ou chaque
retour d'expérience client. La CI déterministe ne consomme pas d'appels modèles.
Les corpus publiés sont synthétiques et dépourvus de secrets ou de données client.
Les essais ajustent les instructions et les outils, pas les poids des modèles.
