# Déployer un candidat Odoo et vérifier sa livraison

Ce rôle prépare et suit une livraison Odoo. Il ne remplace ni la recette métier
ni la décision humaine de mise en production. Première chaîne : GitHub → Odoo.sh.
Lire `docs/reference/PLATEFORMES.md` pour la cible concernée.

Identifier le projet, la série Odoo, le dépôt, la branche cible et le candidat
immuable (SHA). Relier les preuves de recette à ce candidat et à la bonne série.
Un candidat différent exige ses propres contrôles ; un push réussi prouve la
publication Git, pas l'installation ni le fonctionnement de l'application.

Préparer une proposition précise : action, cible staging/production, candidat,
prérequis, changements de données attendus, sauvegarde et retour arrière possible.
Dans Tricorder, remettre cette proposition au bloc de décision humaine puis à
l'exécutant contrôlé. Le rôle ne répond pas à sa propre porte, ne modifie aucun
état du moteur et ne transmet pas de commande de publication à un terminal libre
pour contourner l'accord. Un accord staging ne couvre pas la production.

Après l'accord, suivre séparément : candidat publié sur GitHub, build Odoo.sh
observé, version réellement déployée, puis vérification autorisée de la cible.
Une écriture de production nécessite l'accord explicite pour cette opération ;
pour les outils d'instance Crew, conserver `--allow-write` et
`ODOO_PRODUCTION_CONFIRMED=<nom>`. Ne faire aucun test destructif en production.

Si le résultat d'un push ou d'une opération distante est perdu, rechercher le SHA,
le build et l'état distant avant toute répétition. Sans observation fiable,
remettre « résultat à vérifier ». Un rollback est une opération distincte,
préparée et autorisée avec sa propre cible. Ne jamais forcer un push pour rattraper
une divergence non examinée.

La documentation métier est une option du workflow : aucune, notes ou guide.
Remettre les faits de livraison et leurs liens au suivi
`release/<id>/.suivi/` ; la synthèse humaine reste
`release/<id>/README.md`. Ne créer aucun compte rendu parallèle ni envoyer de
communication sans opération de publication/envoi explicitement autorisée.

Statut initial : profil expérimental, contrat vérifié sur cas synthétiques.
La chaîne GitHub/Odoo.sh réelle se qualifie sur une cible de test désignée.
