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
étapes exécutées. Applique `roles/estimation.md` avant l'exécution : chaque tâche
reçoit une prévision en minutes par rôle, avec fourchette et hypothèses ; le
travail commun de clôture est compté une seule fois. `odoo_effort.py init`
reprend les identifiants du plan, puis `estimate` et `report` produisent
`estimation.md`. Présente les tâches prêtes, leur prévision et les arbitrages restants.
Préparer ou ouvrir un document ne démarre pas l'exécution. Si l'utilisateur a
explicitement demandé d'exécuter aussi, continue avec `/odoo-start`.

Pour une nouvelle demande dans un plan existant, `odoo_plan.py add <release>
--file <definition-ajouts.json>` conserve l'historique et les réceptions. Ne
réinitialise pas le plan et ne remplace pas un identifiant existant. Les nouvelles
dépendances restent explicites et les tâches déjà reçues ne sont pas rejouées
sans changement de contrat, de preuve ou de dépendance.
Ajoute la prévision des nouvelles tâches et motive toute révision des autres ;
conserve l'estimation initiale et les mesures déjà enregistrées.
