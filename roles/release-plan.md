# Préparer une release de plusieurs demandes

Cette commande prépare le travail sans lancer le développement. `/odoo-new`
reste la voie directe pour une demande de bout en bout ; `/odoo-plan` puis
`/odoo-start` conviennent à plusieurs tâches, dépendances ou reprises.

Lis le briefing et applique `roles/functional-review.md`. Conserve chaque demande
originale, les décisions actées et les questions encore bloquantes. Ouvre ou
réutilise la release avec `odoo-release.sh`. Écris la revue globale, puis un
`plan-definition.json` suivant `docs/RELEASE_PLAN.md` : chaque tâche a un résultat
métier, des critères, une voie, un risque, des dépendances et des périmètres.
Une question bloquante reste dans la revue ; ne crée pas une tâche exécutable
fondée sur une réponse inventée.

Valide la définition avec `odoo_plan.py init <release> --file <définition>`.
Le fichier versionné `plan.json` est le plan ; les flows restent l'autorité des
étapes exécutées. Présente les tâches prêtes et les arbitrages restants.
Préparer ou ouvrir un document ne démarre pas l'exécution. Si l'utilisateur a
explicitement demandé d'exécuter aussi, continue avec `/odoo-start`.
